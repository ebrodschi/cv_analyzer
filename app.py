"""
CV Analyzer - Aplicación Streamlit para análisis de CVs con LLMs
"""

import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# IMPORTANTE: Limpiar variables de entorno del sistema antes de cargar .env
# Esto asegura que SOLO se usen las keys del archivo .env, no del sistema
env_vars_to_clear = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "LLM_API_KEY",
]
for var in env_vars_to_clear:
    if var in os.environ:
        del os.environ[var]

# Cargar SOLO variables de entorno desde archivo .env
load_dotenv(override=True)

from components.google_drive_picker import google_drive_picker
from ingestion.drive import (
    complete_oauth_flow,
    download_file,
    exchange_code_for_tokens,
    get_authorization_url_with_redirect,
    get_drive_service,
    get_oauth_authorization_url,
    list_files_by_folder,
    validate_folder_access,
)
from ingestion.hashing import compute_hash
from ingestion.local import is_supported_file, process_uploaded_file
from llm_client.litellm_client import LiteLLMClient
from llm_client.openai_client import OpenAIClient
from llm_client.prompt_templates import (
    DEFAULT_SCORE_CRITERIA,
    PromptConfig,
    get_especialidades_disponibles,
)
from parsing.docx import parse_docx
from parsing.pdf import parse_pdf
from schema.validator import validate_extraction

# Imports de módulos locales
from schema.yaml_loader import get_default_schema, get_variable_names, load_yaml_schema
from utils.excel import (
    create_summary_stats,
    export_to_csv,
    export_to_excel,
    export_to_json,
)
from utils.text_clean import normalize_text

# Configuración de página
st.set_page_config(
    page_title="CV Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado para hacer la scrollbar de la sidebar más ancha y visible
st.markdown(
    """
    <style>
    /* Scrollbar de la sidebar más ancha */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 14px;
    }

    section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
        border: 2px solid #f1f1f1;
    }

    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    /* Para Firefox */
    section[data-testid="stSidebar"] {
        scrollbar-width: thick;
        scrollbar-color: #888 #f1f1f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    """Función principal de la aplicación."""

    # Manejar OAuth redirect ANTES de cualquier otra cosa
    handle_oauth_redirect()

    st.title("📄 CV Analyzer")
    st.markdown(
        """
    **Analiza CVs automáticamente usando LLMs**
    Sube archivos PDF/DOCX o conecta con Google Drive para extraer información estructurada.
    """
    )

    # Inicializar estado de sesión
    init_session_state()

    # Sidebar: Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")

        # Proveedor LLM
        llm_config = configure_llm_provider()

        # Configuración de Prompts (Especialidad, Localidad, Criterios)
        # IMPORTANTE: Debe ir antes de schema porque el schema depende de la especialidad
        prompt_config = configure_prompt_settings()

        # Schema de variables
        schema = configure_schema()

        # Google Drive
        drive_config = configure_google_drive()

        # Opciones avanzadas
        advanced_options = configure_advanced_options()

    # Crear tabs para diferentes secciones
    tab1, tab2, tab3 = st.tabs(["📤 Subir Archivos", "☁️ Google Drive", "📊 Resultados"])

    # Tab 1: Upload local
    with tab1:
        local_files = handle_local_upload()

    # Tab 2: Google Drive
    with tab2:
        drive_files = handle_drive_selection(drive_config)

    # Combinar archivos de ambas fuentes
    all_files = combine_file_sources(local_files, drive_files)

    # Guardar en session_state para persistencia
    if all_files:
        # Inicializar o actualizar la lista de archivos en session_state
        if "all_files_list" not in st.session_state:
            st.session_state.all_files_list = all_files
        else:
            # Actualizar solo si la cantidad cambió (nuevos archivos subidos/listados)
            if len(st.session_state.all_files_list) != len(all_files):
                st.session_state.all_files_list = all_files

        # Usar la lista del session_state
        all_files = st.session_state.all_files_list

    # Mostrar tabla de archivos seleccionados
    if all_files:
        selected_count = sum(1 for f in all_files if f.get("selected", True))
        st.subheader(f"📋 Archivos ({selected_count}/{len(all_files)} seleccionados)")
        display_file_table(all_files)

        # Botón de procesamiento
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Verificar que la API key esté configurada antes de procesar
            if not llm_config.get("api_key_configured", False):
                st.button(
                    "🚀 Procesar CVs",
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    help="⚠️ Primero configura tu API key del LLM en la configuración",
                )
            elif st.button("🚀 Procesar CVs", type="primary", use_container_width=True):
                process_all_cvs(
                    all_files, schema, llm_config, advanced_options, prompt_config
                )
    else:
        st.info("👈 Sube archivos o conecta con Google Drive para comenzar")

    # Tab 3: Resultados
    with tab3:
        display_results()


def init_session_state():
    """Inicializa variables de estado de sesión."""
    if "results_df" not in st.session_state:
        st.session_state.results_df = None
    if "local_files" not in st.session_state:
        st.session_state.local_files = []
    if "drive_files" not in st.session_state:
        st.session_state.drive_files = []
    if "drive_service" not in st.session_state:
        st.session_state.drive_service = None
    if "drive_config" not in st.session_state:
        st.session_state.drive_config = None
    if "processing_logs" not in st.session_state:
        st.session_state.processing_logs = []
    if "oauth_state" not in st.session_state:
        st.session_state.oauth_state = None
    if "oauth_flow" not in st.session_state:
        st.session_state.oauth_flow = None


def handle_oauth_redirect():
    """
    Maneja el redirect de OAuth cuando Google devuelve al usuario a la app.
    Detecta si hay query parameters con el código de autorización.
    """
    # Obtener query parameters
    query_params = st.query_params

    # Verificar si es un redirect de OAuth
    if "code" in query_params and "state" in query_params:
        code = query_params["code"]
        state = query_params["state"]

        # Verificar el state token (protección CSRF)
        if st.session_state.get("oauth_state") == state:
            try:
                # Obtener el flow guardado
                flow = st.session_state.get("oauth_flow")

                if flow:
                    # Construir la URL de respuesta completa
                    # Streamlit elimina el protocolo, tenemos que reconstruirlo
                    current_url = st.query_params.to_dict()

                    # Obtener la URL base de la app
                    try:
                        # En Streamlit Cloud
                        base_url = os.getenv("STREAMLIT_SERVER_BASE_URL", "")
                        if not base_url:
                            # Fallback para desarrollo local
                            base_url = "http://localhost:8501"
                    except:
                        base_url = "http://localhost:8501"

                    # Construir authorization_response
                    authorization_response = f"{base_url}/?code={code}&state={state}"

                    # Intercambiar código por tokens
                    credentials = exchange_code_for_tokens(flow, authorization_response)

                    # Guardar credenciales en session state
                    st.session_state.google_oauth_creds = {
                        "token": credentials.token,
                        "refresh_token": credentials.refresh_token,
                        "token_uri": credentials.token_uri,
                        "client_id": credentials.client_id,
                        "client_secret": credentials.client_secret,
                        "scopes": credentials.scopes,
                    }

                    # Limpiar query parameters y state
                    st.query_params.clear()
                    st.session_state.oauth_state = None
                    st.session_state.oauth_flow = None

                    # Mostrar mensaje de éxito
                    st.success("✅ ¡Autenticación exitosa con Google Drive!")
                    st.balloons()
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error al completar autenticación: {str(e)}")
                # Limpiar query params
                st.query_params.clear()
        else:
            st.warning(
                "⚠️ Estado OAuth inválido. Por favor, intenta autenticarte de nuevo."
            )
            st.query_params.clear()


def configure_llm_provider() -> Dict[str, Any]:
    """Configura el proveedor LLM."""
    st.subheader("🤖 Proveedor LLM")

    provider = st.selectbox(
        "Proveedor",
        ["OpenAI", "Anthropic (vía LiteLLM)", "Google Gemini", "Otro (LiteLLM)"],
        help="Selecciona el proveedor de LLM a usar",
    )

    # Mapeo de modelos sugeridos
    model_suggestions = {
        "OpenAI": [
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "Anthropic (vía LiteLLM)": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
        ],
        "Google Gemini": [
            "gemini/gemini-2.0-flash-exp",
            "gemini/gemini-1.5-flash",
            "gemini/gemini-1.5-flash-8b",
            "gemini/gemini-1.5-pro",
            "gemini/gemini-exp-1206",
        ],
        "Otro (LiteLLM)": [],
    }

    suggestions = model_suggestions.get(provider, [])

    if suggestions:
        model = st.selectbox("Modelo", suggestions)
    else:
        model = st.text_input(
            "Modelo",
            help="Ingresa el nombre del modelo (ej: gpt-4, claude-3-opus-20240229)",
        )

    # Verificar y configurar API key
    api_key_var, api_key_configured = check_and_configure_api_key(provider)

    return {
        "provider": provider,
        "model": model,
        "api_key_configured": api_key_configured,
    }


def check_and_configure_api_key(provider: str) -> tuple[str, bool]:
    """
    Verifica y configura la API key del proveedor.
    Prioridad: 1) .env file, 2) Streamlit secrets, 3) UI input

    NOTA: NO lee del environment del sistema para mantener aislamiento.

    Returns:
        tuple: (nombre_variable, configurada_exitosamente)
    """
    key_map = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic (vía LiteLLM)": "ANTHROPIC_API_KEY",
        "Google Gemini": "GEMINI_API_KEY",
        "Otro (LiteLLM)": "LLM_API_KEY",
    }

    env_var = key_map.get(provider, "OPENAI_API_KEY")

    # Intentar obtener de diferentes fuentes
    api_key_source = None
    api_key_value = None

    # 1. Verificar en archivo .env (ya cargado por dotenv al inicio)
    # Como limpiamos el environment del sistema, os.getenv solo tiene valores de .env
    if os.getenv(env_var):
        api_key_value = os.getenv(env_var)
        api_key_source = "archivo .env"

    # 2. Verificar en secrets de Streamlit (para deployment)
    if not api_key_value:
        try:
            if env_var.lower() in st.secrets:
                api_key_value = st.secrets[env_var.lower()]
                api_key_source = "Streamlit secrets"
        except:
            pass

    # Mostrar estado y permitir ingreso manual
    if api_key_value:
        st.success(f"✅ API key encontrada ({api_key_source})")
        # Guardar en environment para que la usen los clientes LLM
        os.environ[env_var] = api_key_value
        return env_var, True
    else:
        st.warning(f"⚠️ API key no encontrada para {provider}")

        with st.expander("📝 ¿Cómo configurar la API key?"):
            st.markdown(
                f"""
            **Opción 1 - Archivo .env (Recomendado)**:
            1. Crea un archivo `.env` en la raíz del proyecto (copia de `.env.example`)
            2. Agrega la línea: `{env_var}=tu-api-key-aqui`
            3. Reinicia la aplicación

            **Opción 2 - Ingresar aquí (Temporal)**:
            Usa el campo de abajo para esta sesión solamente

            **Opción 3 - Streamlit Secrets** (solo para deployment):
            Define en `.streamlit/secrets.toml` para Streamlit Cloud

            **NOTA**: La app NO lee variables de entorno del sistema por diseño.
            Esto mantiene aislamiento entre proyectos.
            """
            )

        # Campo para ingresar API key manualmente
        manual_key = st.text_input(
            f"Ingresa tu {provider} API key:",
            type="password",
            key=f"manual_api_key_{provider}",
            help=f"Esta key solo se usará durante esta sesión",
        )

        if manual_key:
            # Guardar en environment para esta sesión
            os.environ[env_var] = manual_key
            st.success(f"✅ API key configurada para esta sesión")
            return env_var, True
        else:
            st.error(f"❌ Por favor ingresa tu API key para continuar")
            return env_var, False


def configure_schema() -> Dict[str, Any]:
    """Configura el schema de extracción."""
    st.subheader("📝 Datos a Extraer de los CVs")

    # Obtener la especialidad seleccionada del session_state si existe
    # (se configuró antes en configure_prompt_settings)
    especialidad = st.session_state.get("selected_especialidad", "electricista")

    use_default = st.checkbox(
        "Usar configuración predeterminada",
        value=True,
        help="Activa esta opción para usar los campos estándar ya configurados",
    )

    if use_default:
        schema_yaml = get_default_schema(especialidad)
        st.code(schema_yaml, language="yaml")
    else:
        st.info(
            """
        **Modo Personalizado**: Aquí puedes modificar qué información extraer de los CVs.
        """
        )

        # Expander con guía para agregar campos
        with st.expander("� Guía: ¿Cómo agregar un campo nuevo?"):
            st.markdown(
                """
            ### 🎯 Pasos para agregar un nuevo campo

            **1. Copia el formato de un campo existente**

            Por ejemplo, si quieres agregar "tiene_auto", copia este formato:

            ```yaml
            - name: tiene_auto
              type: boolean
              required: false
            ```

            **2. Pégalo al final de la lista** (antes del último campo)

            **3. Modifica los valores** según lo que necesites

            ---

            ### 📚 Glosario de Términos

            #### **name** (nombre del campo)
            - Es el nombre que le das a tu campo
            - Usa minúsculas y guiones bajos `_` en lugar de espacios
            - **Ejemplos:** `nombre`, `tiene_auto`, `años_experiencia`

            #### **type** (tipo de dato)

            **Para respuestas Sí/No:**
            ```yaml
            type: boolean
            ```
            - Úsalo cuando la respuesta sea "sí" o "no"
            - **Ejemplos:** tiene_auto, sabe_ingles, fumador

            **Para texto (nombres, direcciones, comentarios):**
            ```yaml
            type: string
            ```
            - Úsalo para cualquier texto libre
            - **Ejemplos:** nombre, dirección, observaciones

            **Para números enteros (edad, años, cantidad):**
            ```yaml
            type: integer
            min: 0        # valor mínimo permitido
            max: 100      # valor máximo permitido
            ```
            - Úsalo para números sin decimales
            - Puedes agregar límites con `min` y `max`
            - **Ejemplos:** edad, años_experiencia, cantidad_hijos

            **Para números con decimales:**
            ```yaml
            type: float
            ```
            - Úsalo para números con comas (ej: 5.5)
            - **Ejemplos:** altura, salario_pretendido

            **Para listas de opciones:**
            ```yaml
            type: categorical
            allowed_values: [opción1, opción2, opción3]
            ```
            - Úsalo cuando solo haya opciones específicas válidas
            - **Ejemplo:**
            ```yaml
            - name: nivel_ingles
              type: categorical
              allowed_values: [básico, intermedio, avanzado, nativo]
              required: false
            ```

            **Para listas de textos (tecnologías, habilidades):**
            ```yaml
            type: list[string]
            ```
            - Úsalo para extraer varias cosas del mismo tipo
            - **Ejemplos:** tecnologías, certificaciones, hobbies

            **Para listas complejas (con varios datos por elemento):**
            ```yaml
            type: list[object]
            properties:
              campo1: string
              campo2: integer
            ```
            - Úsalo cuando cada elemento tenga varios datos
            - **Ejemplo de idiomas:**
            ```yaml
            - name: idiomas
              type: list[object]
              properties:
                idioma: string
                nivel: [básico, intermedio, avanzado, nativo]
              required: false
            ```

            #### **required** (obligatorio u opcional)

            ```yaml
            required: true   # El sistema DEBE extraer este dato siempre
            required: false  # El sistema puede dejarlo vacío si no lo encuentra
            ```

            - Usa `true` para datos críticos que no pueden faltar
            - Usa `false` para datos que pueden no estar en todos los CVs

            #### **description** (descripción)

            ```yaml
            description: Explicación de qué debe extraer el sistema
            ```

            - Es opcional pero recomendado
            - Ayuda a que el sistema entienda mejor qué buscar
            - **Ejemplo:**
            ```yaml
            - name: experiencia_relevante
              type: boolean
              required: false
              description: Indica si tiene experiencia en el sector de construcción
            ```

            #### **min / max** (valores mínimo y máximo)

            ```yaml
            min: 18   # valor mínimo
            max: 70   # valor máximo
            ```

            - Solo se usa con números (`integer` o `float`)
            - Define los límites aceptables

            #### **format** (formato especial)

            ```yaml
            format: email   # para correos electrónicos
            ```

            - Solo se usa con texto (`string`)
            - Verifica que el formato sea correcto

            ---

            ### ✅ Ejemplos Completos

            **Agregar campo de género:**
            ```yaml
            - name: genero
              type: categorical
              allowed_values: [masculino, femenino, otro, prefiero_no_decir]
              required: false
            ```

            **Agregar campo de salario pretendido:**
            ```yaml
            - name: salario_pretendido
              type: integer
              min: 0
              max: 1000000
              required: false
              description: Salario mensual pretendido en pesos argentinos
            ```

            **Agregar campo de disponibilidad:**
            ```yaml
            - name: disponibilidad_inmediata
              type: boolean
              required: false
              description: Puede incorporarse en menos de 2 semanas
            ```

            **Agregar lista de certificaciones:**
            ```yaml
            - name: otros_oficios_tecnicos
              type: list[string]
              required: false
              description: Listado de otros conocimientos técnicos
            ```

            ---

            ### ⚠️ Consejos Importantes

            1. **Respeta la indentación** (los espacios al inicio de cada línea)
            2. **No uses tildes ni espacios en los nombres** (usa guiones bajos `_`)
            3. **Los comentarios con `#` son solo para ti**, el sistema los ignora
            4. **Guarda una copia** antes de hacer cambios grandes
            5. **Prueba con pocos CVs primero** para ver si funciona como esperas
            """
            )

        schema_yaml = st.text_area(
            "Configuración de campos",
            value=get_default_schema(),
            height=400,
            help="Modifica los campos según tus necesidades. Usa la guía de arriba si tienes dudas.",
        )

    # Validar schema
    try:
        schema = load_yaml_schema(schema_yaml)
        variables = get_variable_names(schema)
        st.success(f"✅ Configuración válida ({len(variables)} campos a extraer)")
        with st.expander("📊 Ver lista de campos"):
            st.markdown("**Campos que se extraerán de cada CV:**")
            for var in variables:
                st.write(f"• {var}")
        return schema
    except Exception as e:
        st.error(f"❌ Error en la configuración: {str(e)}")
        st.warning(
            "💡 Revisa que el formato sea correcto. Puedes volver a activar 'Usar configuración predeterminada' para restaurar."
        )
        return None


def configure_prompt_settings() -> PromptConfig:
    """Configura los settings de prompts (especialidad, localidad, criterios)."""
    st.subheader("🎯 Configuración de Análisis")

    # Selección de especialidad
    especialidades = ["personalizado"] + get_especialidades_disponibles()
    especialidad = st.selectbox(
        "Especialidad/Perfil a buscar",
        especialidades,
        help="Selecciona una especialidad predefinida o personaliza tu propia búsqueda",
    )

    # Guardar en session_state para que configure_schema pueda usarlo
    st.session_state.selected_especialidad = especialidad

    # Localidad y radio
    col1, col2 = st.columns(2)
    with col1:
        localidad = st.text_input(
            "Localidad de la posición",
            value="Buenos Aires",
            help="Localidad donde se encuentra la posición a cubrir",
        )
    with col2:
        radio_km = st.number_input(
            "Radio (km)",
            min_value=1,
            max_value=100,
            value=10,
            help="Radio aceptable desde la localidad",
        )

    # Criterios de score personalizados
    with st.expander("📊 Criterios de Score (avanzado)"):
        use_default_score = st.checkbox("Usar criterios por defecto", value=True)

        if use_default_score:
            criterios_score = None
            st.code(DEFAULT_SCORE_CRITERIA, language="text")
        else:
            criterios_score = st.text_area(
                "Criterios personalizados",
                value=DEFAULT_SCORE_CRITERIA,
                height=300,
                help="Define tus propios criterios para calcular el score del 1-10",
            )

    # Campos adicionales para especialidad personalizada
    campos_adicionales = {}
    if especialidad == "personalizado":
        with st.expander("⚙️ Configuración Personalizada"):
            campos_adicionales["titulo"] = st.text_input(
                "Título de la posición", value="Perfil Técnico"
            )
            campos_adicionales["experiencia_campo"] = st.text_input(
                "Nombre del campo de experiencia",
                value="experiencia_confirmada",
                help="Ej: experiencia_electricista_confirmada",
            )
            campos_adicionales["descripcion_experiencia"] = st.text_area(
                "Descripción de experiencia requerida",
                value="trabajo previo relevante",
                help="Describe qué tipo de experiencia se busca",
            )

    # Crear configuración de prompts
    config = PromptConfig(
        especialidad=especialidad,
        localidad=localidad,
        radio_km=radio_km,
        criterios_score=criterios_score,
        campos_adicionales=campos_adicionales if campos_adicionales else None,
    )

    return config


def configure_google_drive() -> Dict[str, Any]:
    """Configura conexión con Google Drive."""
    st.subheader("☁️ Google Drive")

    folder_id = st.text_input(
        "ID de Carpeta",
        help="ID de la carpeta de Google Drive (extraído de la URL). Ejemplo: 1a2b3c4d5e6f7g8h9i",
    )

    # Solo mostrar modo api_key (oauth requiere configuración del desarrollador)
    auth_mode = st.selectbox(
        "Modo de autenticación",
        ["api_key"],
        help="**api_key**: Ingresa tu API key de Google (solo para carpetas públicas)",
    )

    # NOTA: El modo 'oauth' está deshabilitado porque requiere que el desarrollador
    # configure credenciales OAuth en Google Cloud Console. Si en el futuro quieres
    # habilitarlo, cambia la línea de arriba a: ["api_key", "oauth"]

    # Configuración específica según el modo
    api_key = None

    if auth_mode == "api_key":
        st.info(
            "🔑 **Modo API Key**: Ingresa tu API key de Google para acceder a carpetas públicas."
        )

        # Verificar si hay API key en variables de entorno
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            st.warning(
                "⚠️ **¿Cómo obtener tu API key de Google?**\n\n"
                "1. Ve a [Google Cloud Console](https://console.cloud.google.com/)\n"
                "2. Crea o selecciona un proyecto\n"
                "3. Habilita **Google Drive API**\n"
                "4. Ve a **Credenciales** → **Crear credenciales** → **Clave de API**\n"
                "5. Copia la clave\n\n"
                "**⚠️ Importante**: La carpeta de Drive debe ser **pública** (compartida con 'cualquiera con el enlace')."
            )

        # Permitir ingresar API key manualmente
        api_key_input = st.text_input(
            "Ingresa tu API key de Google:",
            value=api_key if api_key else "",
            type="password",
            help="Tu API key de Google Cloud con acceso a Google Drive API",
        )

        if api_key_input:
            api_key = api_key_input
            st.success("✅ API key configurada")

        # Información sobre cómo hacer pública una carpeta
        with st.expander("ℹ️ ¿Cómo hacer pública mi carpeta de Drive?"):
            st.markdown(
                """
            1. Abre Google Drive en tu navegador
            2. Encuentra la carpeta con los CVs
            3. Clic derecho → **Compartir** o **Obtener enlace**
            4. En **"Acceso general"**, selecciona:
               - **"Cualquiera con el enlace"**
               - Rol: **"Lector"**
            5. Copia el enlace (debe tener `?usp=sharing` al final)
            6. El ID de la carpeta está en la URL:
               ```
               https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                                      ↑ Este es el ID
               ```
            """
            )

    # ============================================================================
    # NOTA: Modo OAuth deshabilitado
    # ============================================================================
    # El modo 'oauth' fue removido de la UI porque requiere que el desarrollador
    # configure credenciales OAuth (credentials.json o variables de entorno).
    #
    # Si en el futuro quieres habilitarlo:
    # 1. Agrega "oauth" en la lista del selectbox (línea ~403)
    # 2. Restaura el código OAuth desde app.py.backup (líneas 463-574)
    # 3. Configura credentials.json o GOOGLE_OAUTH_CLIENT_ID/SECRET
    # ============================================================================

    return {
        "folder_id": folder_id,
        "auth_mode": auth_mode,
        "api_key": api_key if auth_mode == "api_key" else None,
    }


def configure_advanced_options() -> Dict[str, Any]:
    """Configura opciones avanzadas."""
    with st.expander("🔧 Opciones Avanzadas"):
        # OCR para detección de fotos
        use_ocr = st.checkbox(
            "🖼️ Usar OCR (Docling) para detectar fotos",
            value=True,  # Habilitado por defecto
            help=(
                "Habilita OCR con Docling para detectar si el CV tiene foto del candidato.\n"
                "Requiere instalar: pip install docling\n"
                "⚠️ El procesamiento será más lento pero más preciso."
            ),
        )

        if use_ocr:
            st.info(
                "ℹ️ **OCR habilitado**: El sistema detectará si los CVs tienen foto.\n"
                "Asegúrate de haber instalado: `pip install docling`"
            )

        max_files = st.number_input(
            "Límite de archivos",
            min_value=1,
            max_value=1000,
            value=100,
            help="Máximo número de archivos a procesar",
        )

        max_workers = st.number_input(
            "Concurrencia máxima",
            min_value=1,
            max_value=20,
            value=5,
            help="Número de archivos a procesar en paralelo",
        )

        temperature = st.slider(
            "Temperatura LLM",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Mayor temperatura = más creatividad (menos recomendado para extracción)",
        )

        max_tokens = st.number_input(
            "Máximo tokens respuesta", min_value=500, max_value=4000, value=2000
        )

        return {
            "use_ocr": use_ocr,
            "max_files": max_files,
            "max_workers": max_workers,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }


def handle_local_upload() -> List[Dict[str, Any]]:
    """Maneja la subida de archivos locales."""
    st.subheader("📤 Subir Archivos Locales")

    uploaded_files = st.file_uploader(
        "Arrastra archivos aquí o haz clic para seleccionar",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Soporta archivos PDF y DOCX",
    )

    files_info = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if is_supported_file(uploaded_file.name):
                filename, content, mime_type = process_uploaded_file(uploaded_file)
                file_hash = compute_hash(content)

                files_info.append(
                    {
                        "source": "local",
                        "name": filename,
                        "content": content,
                        "mime_type": mime_type,
                        "hash": file_hash,
                        "size": len(content),
                        "selected": True,
                        "link": "",  # Archivos locales no tienen link clickeable
                    }
                )

        st.success(f"✅ {len(files_info)} archivo(s) cargado(s)")

    return files_info


def handle_drive_selection(drive_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Maneja la selección de archivos de Drive."""
    st.subheader("☁️ Archivos de Google Drive")

    folder_id = drive_config.get("folder_id", "").strip()
    auth_mode = drive_config.get("auth_mode")

    if not folder_id:
        st.info("👆 Ingresa un ID de carpeta en la configuración de arriba")
        return []

    # Botón para listar archivos
    if st.button("🔍 Listar Archivos de Drive"):
        with st.spinner("Conectando con Google Drive..."):
            try:
                # Obtener servicio según el modo de autenticación
                api_key = drive_config.get("api_key")

                service = get_drive_service(auth_mode=auth_mode, api_key=api_key)

                # Validar acceso
                has_access, error = validate_folder_access(folder_id, service)

                if not has_access:
                    st.error(f"❌ {error}")

                    # Ayuda contextual según el modo
                    if auth_mode == "api_key":
                        st.info(
                            "💡 **Sugerencias para modo API Key:**\n"
                            "1. Verifica que el ID de la carpeta sea correcto\n"
                            "2. Asegúrate de que la carpeta sea **pública** (clic derecho → Compartir → 'Cualquiera con el enlace')\n"
                            "3. Verifica que tu API key sea válida y tenga la Google Drive API habilitada"
                        )
                    elif auth_mode == "oauth":
                        st.info(
                            "💡 **Sugerencias para modo OAuth:**\n"
                            "1. Verifica que autorizaste correctamente con Google\n"
                            "2. El token puede haber expirado, vuelve a autorizar\n"
                            "3. Asegúrate de tener permisos sobre la carpeta"
                        )
                    return []

                # Listar archivos
                files = list_files_by_folder(folder_id, service)

                if not files:
                    st.warning("⚠️ No se encontraron archivos PDF/DOCX en la carpeta")
                    return []

                st.success(f"✅ {len(files)} archivo(s) encontrado(s)")

                # Guardar en sesión
                st.session_state.drive_files = files
                st.session_state.drive_service = service
                st.session_state.drive_config = {
                    "auth_mode": auth_mode,
                    "api_key": api_key,
                }

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

                # Mostrar detalles del error en un expander
                with st.expander("Ver detalles del error"):
                    st.code(str(e))

                return []

    # Mostrar archivos encontrados
    if st.session_state.drive_files:
        files_info = []

        for file in st.session_state.drive_files:
            # Construir link de Google Drive
            # Si webViewLink no está disponible (api_key mode), construir manualmente
            link = file.get("webViewLink", "")
            if not link and file.get("id"):
                link = f"https://drive.google.com/file/d/{file['id']}/view"

            files_info.append(
                {
                    "source": "drive",
                    "name": file["name"],
                    "file_id": file["id"],
                    "mime_type": file["mimeType"],
                    "size": int(file.get("size", 0)),
                    "selected": True,
                    "content": None,  # Se descargará al procesar
                    "link": link,
                }
            )

        return files_info

    return []


def combine_file_sources(
    local_files: List[Dict[str, Any]], drive_files: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Combina archivos de diferentes fuentes."""
    all_files = []

    # Agregar archivos locales
    all_files.extend(local_files)

    # Agregar archivos de Drive
    all_files.extend(drive_files)

    return all_files


def display_file_table(files: List[Dict[str, Any]]):
    """Muestra tabla de archivos seleccionados con controles de selección."""

    # Botones de selección rápida
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("✅ Seleccionar Todos", use_container_width=True):
            for f in files:
                f["selected"] = True
            st.rerun()

    with col2:
        if st.button("❌ Deseleccionar Todos", use_container_width=True):
            for f in files:
                f["selected"] = False
            st.rerun()

    # Crear DataFrame para display
    df_display = pd.DataFrame(
        [
            {
                "Archivo": f["name"],
                "Fuente": "💻 Local" if f["source"] == "local" else "☁️ Drive",
                "Tamaño": format_file_size(f["size"]),
                "Incluir": "✅" if f["selected"] else "❌",
            }
            for f in files
        ]
    )

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Checkboxes individuales para cada archivo
    st.markdown("##### Selección individual:")
    cols_per_row = 2
    for idx in range(0, len(files), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            file_idx = idx + i
            if file_idx < len(files):
                with col:
                    current_state = files[file_idx]["selected"]
                    new_state = st.checkbox(
                        files[file_idx]["name"],
                        value=current_state,
                        key=f"file_select_{file_idx}_{files[file_idx]['name']}",
                    )
                    if new_state != current_state:
                        files[file_idx]["selected"] = new_state


def format_file_size(size_bytes: int) -> str:
    """Formatea tamaño de archivo."""
    for unit in ["B", "KB", "MB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} GB"


def process_all_cvs(
    files: List[Dict[str, Any]],
    schema: Dict[str, Any],
    llm_config: Dict[str, Any],
    options: Dict[str, Any],
    prompt_config: PromptConfig,
):
    """Procesa todos los CVs."""

    if not schema:
        st.error("❌ Schema inválido. Corrige el schema antes de procesar.")
        return

    # Filtrar archivos seleccionados
    selected_files = [f for f in files if f.get("selected", True)]

    # Aplicar límite
    max_files = options["max_files"]
    if len(selected_files) > max_files:
        st.warning(f"⚠️ Limitando a {max_files} archivos")
        selected_files = selected_files[:max_files]

    # Inicializar cliente LLM
    try:
        llm_client = create_llm_client(llm_config, options)
    except Exception as e:
        st.error(f"❌ Error inicializando LLM: {str(e)}")
        return

    # Obtener servicio de Drive si hay archivos de Drive
    drive_service = None
    has_drive_files = any(f["source"] == "drive" for f in selected_files)

    if has_drive_files:
        # Intentar obtener servicio de Drive
        if (
            hasattr(st.session_state, "drive_service")
            and st.session_state.drive_service is not None
        ):
            drive_service = st.session_state.drive_service
        elif (
            hasattr(st.session_state, "drive_config") and st.session_state.drive_config
        ):
            # Recrear servicio si es necesario
            try:
                config = st.session_state.drive_config
                drive_service = get_drive_service(
                    auth_mode=config.get("auth_mode"), api_key=config.get("api_key")
                )
            except Exception as e:
                st.error(f"❌ Error conectando con Google Drive: {str(e)}")
                st.info("💡 Ve a la tab 'Google Drive' y vuelve a listar los archivos")
                return

        if drive_service is None:
            st.error("❌ Servicio de Google Drive no disponible")
            st.info(
                "💡 Ve a la tab 'Google Drive' y lista los archivos antes de procesarlos"
            )
            return

    # Procesar archivos
    st.subheader("⚙️ Procesando CVs...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    results = []
    errors = []

    max_workers = options["max_workers"]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar tareas
        future_to_file = {
            executor.submit(
                process_single_cv,
                file_info,
                schema,
                llm_client,
                prompt_config,
                drive_service,
                options.get("use_ocr", False),  # Pasar configuración de OCR
            ): file_info
            for file_info in selected_files
        }

        # Procesar resultados
        for i, future in enumerate(as_completed(future_to_file)):
            file_info = future_to_file[future]

            try:
                result = future.result()
                results.append(result)

                if result.get("error"):
                    errors.append(f"❌ {file_info['name']}: {result['error']}")

            except Exception as e:
                error_msg = f"Error procesando {file_info['name']}: {str(e)}"
                errors.append(error_msg)

                # Agregar resultado con error
                results.append(
                    {
                        "archivo": file_info["name"],
                        "fuente": file_info["source"],
                        "link": file_info.get("link", ""),
                        "error": str(e),
                    }
                )

            # Actualizar progreso
            progress = (i + 1) / len(selected_files)
            progress_bar.progress(progress)
            status_text.text(f"Procesados: {i + 1}/{len(selected_files)}")

    # Crear DataFrame con resultados
    if results:
        df_results = pd.DataFrame(results)
        st.session_state.results_df = df_results

        # Mostrar resumen
        st.success(f"✅ Procesamiento completado: {len(results)} archivos")

        if errors:
            with st.expander(f"⚠️ Errores ({len(errors)})"):
                for error in errors:
                    st.warning(error)

        # Cambiar a tab de resultados
        st.info("👉 Ve a la pestaña 'Resultados' para ver los datos extraídos")


def create_llm_client(llm_config: Dict[str, Any], options: Dict[str, Any]):
    """Crea instancia de cliente LLM."""
    provider = llm_config["provider"]
    model = llm_config["model"]
    temperature = options["temperature"]
    max_tokens = options["max_tokens"]

    try:
        if provider == "OpenAI":
            return OpenAIClient(
                model=model, temperature=temperature, max_tokens=max_tokens
            )
        else:
            # Usar LiteLLM para otros proveedores
            return LiteLLMClient(
                model=model, temperature=temperature, max_tokens=max_tokens
            )
    except TypeError as e:
        # Capturar errores de argumentos incorrectos
        error_msg = str(e)
        if "proxies" in error_msg or "unexpected keyword argument" in error_msg:
            raise ValueError(
                f"Error de compatibilidad con la librería {provider}. "
                f"Verifica las versiones instaladas:\n"
                f"  - openai: debe ser >= 1.0.0 (recomendado: 1.54.0)\n"
                f"  - litellm: debe ser >= 1.0.0 (recomendado: 1.29.3)\n\n"
                f"Ejecuta: pip install --upgrade openai==1.54.0 litellm==1.29.3\n\n"
                f"Error original: {error_msg}"
            )
        raise


def process_single_cv(
    file_info: Dict[str, Any],
    schema: Dict[str, Any],
    llm_client,
    prompt_config: PromptConfig,
    drive_service=None,
    use_ocr: bool = False,
) -> Dict[str, Any]:
    """Procesa un solo CV.

    Args:
        file_info: Información del archivo
        schema: Schema de extracción
        llm_client: Cliente LLM
        prompt_config: Configuración de prompts
        drive_service: Servicio de Google Drive (necesario para archivos de Drive)
        use_ocr: Si True, usa OCR para detectar fotos
    """

    result = {
        "archivo": file_info["name"],
        "fuente": file_info["source"],
        "link": file_info.get("link", ""),
        "error": "",
    }

    try:
        # Obtener contenido
        if file_info["source"] == "local":
            content = file_info["content"]
        else:
            # Descargar de Drive
            if drive_service is None:
                raise ValueError("Servicio de Google Drive no disponible")

            content = download_file(file_info["file_id"], drive_service)
            result["sha1"] = compute_hash(content)

        # Parsear archivo con OCR si está habilitado
        parsed_result = parse_file(content, file_info["mime_type"], use_ocr)

        # Detectar si hay foto (para informar al LLM)
        has_photo = False
        if use_ocr and isinstance(parsed_result, dict):
            text = parsed_result.get("text", "")
            has_photo = parsed_result.get("has_photo", False)
            # Agregar información de foto al texto para que el LLM la procese
            if has_photo:
                text = f"[NOTA: Este CV contiene {parsed_result.get('images_count', 1)} imagen(es)/foto(s)]\n\n{text}"
        else:
            # Modo tradicional, solo texto
            text = (
                parsed_result if isinstance(parsed_result, str) else str(parsed_result)
            )

        # Normalizar texto
        text = normalize_text(text)

        if not text.strip():
            raise ValueError("No se pudo extraer texto del archivo")

        # Extraer información con LLM usando la configuración de prompts
        # El LLM ahora puede extraer hay_foto_en_cv desde el contexto del texto

        # DEBUG: Ver qué campos de experiencia hay en el schema
        exp_fields = [
            v["name"]
            for v in schema["variables"]
            if "experiencia" in v["name"] and "años" not in v["name"]
        ]
        if exp_fields:
            print(f"\n🔎 DEBUG Schema - Campos de experiencia en schema: {exp_fields}")

        extracted_data = llm_client.extract_profile(text, schema, prompt_config)

        # DEBUG: Ver qué devuelve el LLM
        if extracted_data.get("nombre"):
            print(f"\n📋 DEBUG LLM Response - {extracted_data.get('nombre')}:")
            print(
                f"   experiencia_electricista_confirmada en respuesta: {extracted_data.get('experiencia_electricista_confirmada', 'CAMPO NO EXISTE')}"
            )
            print(f"   Todas las claves: {list(extracted_data.keys())}\n")

        # Agregar datos extraídos
        result.update(extracted_data)

        # POST-PROCESAMIENTO: Calcular campos derivados
        result = calculate_derived_fields(result)

    except Exception as e:
        result["error"] = str(e)

    return result


def calculate_derived_fields(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula campos derivados basados en los datos extraídos por el LLM.

    Campos calculados:
    - preaprobado: edad_en_rango AND experiencia_electricista_confirmada AND hay_foto_en_cv AND secundaria_tecnica

    Args:
        result: Diccionario con datos extraídos del CV

    Returns:
        Diccionario actualizado con campos derivados
    """

    # Función auxiliar para convertir valores a booleano
    def to_bool(value):
        if value is None or value == "" or pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "yes", "sí", "si", "1"]
        if isinstance(value, (int, float)):
            return bool(value)
        return False

    # Calcular preaprobado
    edad_en_rango = to_bool(result.get("edad_en_rango", False))

    # Buscar el campo de experiencia confirmada (puede tener diferentes nombres según especialidad)
    experiencia_confirmada = False
    possible_exp_fields = [
        "experiencia_electricista_confirmada",
        "experiencia_electromecanico_confirmada",
        "experiencia_mecanico_industrial_confirmada",
        "experiencia_pañol_depositos_confirmada",
        "experiencia_confirmada",
    ]
    for field in possible_exp_fields:
        if field in result:
            experiencia_confirmada = to_bool(result.get(field, False))
            break

    hay_foto = to_bool(result.get("hay_foto_en_cv", False))
    secundaria_tecnica = to_bool(result.get("secundaria_tecnica", False))

    # DEBUG: Imprimir valores para diagnóstico (comentar después)
    if result.get("nombre"):  # Solo si tiene nombre para evitar spam
        print(f"\n🔍 DEBUG Preaprobado - {result.get('nombre', 'Sin nombre')}:")
        print(f"   edad_en_rango: {result.get('edad_en_rango')} → {edad_en_rango}")
        print(
            f"   experiencia_electricista_confirmada: {result.get('experiencia_electricista_confirmada')} → {experiencia_confirmada}"
        )
        print(f"   hay_foto_en_cv: {result.get('hay_foto_en_cv')} → {hay_foto}")
        print(
            f"   secundaria_tecnica: {result.get('secundaria_tecnica')} → {secundaria_tecnica}"
        )

    # Un candidato está preaprobado si cumple TODOS los criterios
    preaprobado_value = (
        edad_en_rango and experiencia_confirmada and hay_foto and secundaria_tecnica
    )

    if result.get("nombre"):
        print(f"   → PREAPROBADO: {preaprobado_value}\n")

    result["preaprobado"] = preaprobado_value

    return result


def parse_file(
    content: bytes, mime_type: str, use_ocr: bool = False
) -> Union[str, Dict[str, Any]]:
    """Parsea un archivo según su tipo.

    Args:
        content: Contenido del archivo en bytes
        mime_type: Tipo MIME del archivo
        use_ocr: Si True, usa OCR para detectar fotos

    Returns:
        Si use_ocr=False: str con el texto extraído
        Si use_ocr=True: dict con 'text', 'has_photo', 'images_count', 'metadata'
    """
    if "pdf" in mime_type.lower():
        return parse_pdf(content, use_ocr=use_ocr)
    elif "word" in mime_type.lower() or "docx" in mime_type.lower():
        return parse_docx(content, use_ocr=use_ocr)
    else:
        raise ValueError(f"Tipo de archivo no soportado: {mime_type}")


def display_results():
    """Muestra resultados del procesamiento."""

    if st.session_state.results_df is None:
        st.info("📊 Los resultados aparecerán aquí después de procesar los CVs")
        return

    df = st.session_state.results_df.copy()

    # Ordenar por score_general descendente
    if "score_general" in df.columns:
        df = df.sort_values("score_general", ascending=False)

    st.subheader("📊 Resultados")

    # Estadísticas resumen
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total CVs", len(df))

    with col2:
        exitosos = len(df[df["error"] == ""])
        st.metric("Exitosos", exitosos)

    with col3:
        con_errores = len(df[df["error"] != ""])
        st.metric("Con Errores", con_errores)

    with col4:
        # Mostrar cantidad de preaprobados en lugar de experiencia promedio
        if "preaprobado" in df.columns:
            # Convertir a booleano y contar True
            preaprobados_count = (
                pd.to_numeric(df["preaprobado"], errors="coerce")
                .fillna(0)
                .astype(bool)
                .sum()
            )
            st.metric("Preaprobados", int(preaprobados_count))
        else:
            st.metric("Preaprobados", "N/A")

    # Mostrar tabla
    st.subheader("📋 Tabla de Datos")

    # Preparar DataFrame para mejor visualización
    df_display = df.copy()

    # Convertir nombres de columnas de snake_case a Title Case legible
    def snake_to_title(column_name):
        """Convierte snake_case a Title Case."""
        # Casos especiales para nombres comunes
        special_cases = {
            "score_general": "Score",
            "mail": "Mail",
            "cv": "CV",
            "hay_foto_en_cv": "Foto en CV",
        }

        if column_name in special_cases:
            return special_cases[column_name]

        # Conversión general: reemplazar _ con espacio y capitalizar
        return column_name.replace("_", " ").title()

    # Aplicar conversión a todos los nombres de columnas
    df_display.columns = [snake_to_title(col) for col in df_display.columns]

    # IMPORTANTE: Asegurar que las columnas prioritarias existan (aunque sea vacías)
    # Esto garantiza que siempre se muestren en el orden correcto
    priority_columns_snake = [
        "score_general",
        "nombre",
        "telefono",
        "mail",
        "localidad_residencia",
        "edad",
        "secundaria_completa",
        "secundaria_tecnica",
        "titulo_secundario",
        "preaprobado",
    ]

    # Agregar columnas faltantes con valores None (antes de la conversión de nombres)
    # Primero revertimos temporalmente a nombres snake_case
    df_temp = df.copy()
    for col_snake in priority_columns_snake:
        if col_snake not in df_temp.columns:
            df_temp[col_snake] = None

    # Ahora aplicamos todas las transformaciones al DataFrame temporal con columnas completas
    df_display = df_temp.copy()

    # Convertir valores booleanos a Sí/No (antes de cambiar nombres de columnas)
    bool_columns = df_display.select_dtypes(include=["bool"]).columns.tolist()
    for col in df_display.columns:
        if (
            col in bool_columns
            or col.startswith(
                (
                    "tiene_",
                    "hay_",
                    "es_",
                    "edad_en_",
                    "preaprobado",
                    "secundaria_",
                    "primaria_",
                    "terciario_",
                    "experiencia_",
                    "lugar_",
                )
            )
            or col in ["preaprobado"]
        ):
            try:
                df_display[col] = df_display[col].apply(
                    lambda x: (
                        "Sí"
                        if (
                            x is True
                            or x == "True"
                            or x == "true"
                            or x == 1
                            or x == "1"
                        )
                        else (
                            "No"
                            if (
                                x is False
                                or x == "False"
                                or x == "false"
                                or x == 0
                                or x == "0"
                            )
                            else x
                        )
                    )
                )
            except:
                pass

    # Ahora sí convertir nombres de columnas
    df_display.columns = [snake_to_title(col) for col in df_display.columns]

    # Reordenar columnas con el orden especificado
    # Orden: score, nombre, telefono, mail, localidad residencia, edad, secundario completo, secundario técnico, titulo secundario, preaprobado, resto
    priority_columns = [
        "Score",  # score_general -> Score
        "Nombre",
        "Telefono",
        "Mail",
        "Localidad Residencia",
        "Edad",
        "Secundaria Completa",
        "Secundaria Tecnica",
        "Titulo Secundario",
        "Preaprobado",
    ]

    # Obtener columnas existentes en el orden prioritario
    ordered_cols = [col for col in priority_columns if col in df_display.columns]

    # Agregar el resto de columnas que no están en la lista prioritaria
    remaining_cols = [col for col in df_display.columns if col not in ordered_cols]

    # Combinar en el orden final
    final_column_order = ordered_cols + remaining_cols
    df_display = df_display[final_column_order]

    # Mejorar visualización de links
    link_col_name = snake_to_title("link")
    if link_col_name in df_display.columns:
        # Para archivos locales (sin link), no mostrar nada
        df_display[link_col_name] = df_display.apply(
            lambda row: (
                row[link_col_name]
                if pd.notna(row.get(link_col_name))
                and str(row.get(link_col_name, "")).strip()
                else ""  # Dejar vacío para archivos locales
            ),
            axis=1,
        )

        # Solo configurar LinkColumn si hay al menos un link válido
        has_valid_links = df_display[link_col_name].astype(str).str.strip().any()

        if has_valid_links:
            column_config = {
                link_col_name: st.column_config.LinkColumn(
                    "Ubicación del Archivo",
                    help="Click para abrir archivos de Google Drive en el navegador",
                    width="medium",
                )
            }
        else:
            # Si no hay links válidos, ocultar la columna
            df_display = df_display.drop(columns=[link_col_name])
            column_config = {}
    else:
        column_config = {}

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )

    # Botones de descarga - Usar el mismo DataFrame formateado que se muestra en la UI
    st.subheader("💾 Descargar Resultados")

    # Preparar DataFrame para descarga: usar df_display pero sin la columna de link
    df_download = df_display.copy()

    # Eliminar columna de link si existe (solo es para visualización en UI)
    link_col_name = snake_to_title("link")
    if link_col_name in df_download.columns:
        df_download = df_download.drop(columns=[link_col_name])

    # También eliminar otras columnas de metadatos si existen
    metadata_cols_to_remove = ["Fuente", "Sha1", "Hash"]
    for col in metadata_cols_to_remove:
        if col in df_download.columns:
            df_download = df_download.drop(columns=[col])

    col1, col2, col3 = st.columns(3)

    with col1:
        excel_data = export_to_excel(df_download)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_data,
            file_name="cv_analisis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col2:
        csv_data = export_to_csv(df_download)
        st.download_button(
            label="📥 Descargar CSV",
            data=csv_data,
            file_name="cv_analisis.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        json_data = export_to_json(df_download)
        st.download_button(
            label="📥 Descargar JSON",
            data=json_data,
            file_name="cv_analisis.json",
            mime="application/json",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
