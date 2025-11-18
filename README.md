# CV Analyzer 📄

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Aplicación web en Streamlit para análisis automático de CVs usando LLMs (Large Language Models).

---

📚 **[Ver Índice Completo de Documentación →](INDEX.md)**

## 🎯 Características

- ✅ Análisis de CVs en **PDF** y **DOCX**
- ☁️ Integración con **Google Drive** para procesar carpetas completas
- 📤 Subida local de múltiples archivos (drag & drop)
- 🤖 Soporte para **múltiples proveedores LLM**: OpenAI, Anthropic, Azure OpenAI
- 📊 Export a **Excel**, **CSV** y **JSON**
- ⚙️ Schema **configurable** vía YAML para definir qué extraer
- 🔄 Procesamiento **concurrente** con retry automático
- ✨ Validación **automática** de datos extraídos
- 🔐 **Seguridad**: API keys solo desde variables de entorno

## 📋 Requisitos

- Python 3.9+
- API key de OpenAI (o proveedor LLM alternativo)
- (Opcional) Credenciales de Google Drive para integración

## � Estructura del Proyecto

```
cv_analyzer/
├── app.py                  # Aplicación principal Streamlit
├── requirements.txt        # Dependencias Python
├── .env.example           # Template de configuración
├── docs/                  # 📚 Toda la documentación
│   ├── README.md         # Índice de documentación
│   ├── QUICKSTART.md     # Guía de inicio rápido
│   ├── API_KEY_SETUP.md  # Configuración de API keys
│   └── ...               # Más guías
├── tests/                 # 🧪 Tests y verificación
│   ├── README.md         # Guía de tests
│   ├── test_*.py         # Archivos de tests
│   └── verify_setup.py   # Script de verificación
├── components/            # Componentes UI
├── ingestion/            # Módulos de ingesta (Drive, local)
├── llm_client/           # Clientes LLM (OpenAI, Anthropic, etc.)
├── parsing/              # Parsers (PDF, DOCX)
├── schema/               # Schemas YAML y validación
└── utils/                # Utilidades (Excel, limpieza de texto)
```

**📚 Documentación completa**: Ver carpeta [`docs/`](./docs/)

## �🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd cv_analyzer
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita `.env` y configura tu API key:

```bash
# API key de OpenAI (REQUERIDO)
OPENAI_API_KEY=sk-tu-api-key-aquí

# O para otros proveedores:
# ANTHROPIC_API_KEY=tu-key-aquí
# AZURE_OPENAI_KEY=tu-key-aquí

# Google Drive (OPCIONAL)
DRIVE_AUTH_MODE=service  # o 'oauth'
GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/credenciales.json
```

### 5. (Opcional) Configurar Google Drive

Hay **4 modos de autenticación** disponibles:

#### Opción A: Carpetas Públicas (✨ RECOMENDADO - más simple)

**Ideal para**: Carpetas públicas de Google Drive que no requieren autenticación.

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Habilita la **Google Drive API**
4. Ve a **Credenciales** → **Crear credenciales** → **Clave de API**
5. Copia la API key
6. Agrega a tu `.env`:

```bash
DRIVE_AUTH_MODE=public
GOOGLE_API_KEY=tu-api-key-aquí
```

7. **Importante**: La carpeta de Drive debe ser **pública**:
   - Abre la carpeta en Google Drive
   - Clic derecho → Compartir
   - Cambiar a "Cualquiera con el enlace puede ver"

**Ventajas**: ✅ Sin OAuth, ✅ Sin Service Account, ✅ Funciona inmediatamente

#### Opción B: OAuth en la UI de Streamlit (🔐 RECOMENDADO - carpetas privadas)

**Ideal para**: Acceder a tus carpetas privadas directamente desde la interfaz web.

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Habilita la **Google Drive API**
4. Ve a **Credenciales** → **Crear credenciales** → **ID de cliente de OAuth 2.0**
5. Tipo de aplicación: **Aplicación de escritorio**
6. Descarga el archivo JSON o copia el Client ID y Client Secret
7. Opción 1 - Archivo: Guarda como `credentials.json` en la raíz del proyecto
8. Opción 2 - Variables de entorno en `.env`:

```bash
DRIVE_AUTH_MODE=oauth_streamlit
GOOGLE_OAUTH_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=tu-client-secret
```

9. En la interfaz de Streamlit, haz clic en **"Autenticar con Google"**
10. Sigue las instrucciones para autorizar la aplicación

**Ventajas**: ✅ Acceso a carpetas privadas, ✅ Autenticación en la UI, ✅ No requiere servidor local

#### Opción C: Service Account (🤖 Para producción)

**Ideal para**: Entornos de producción, automatización, servidores.

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Habilita la **Google Drive API**
4. Crea una **Service Account**
5. Descarga el archivo JSON de credenciales
6. Comparte la carpeta de Drive con el email de la service account (ej: `my-service@project.iam.gserviceaccount.com`)
7. Configura en `.env`:

```bash
DRIVE_AUTH_MODE=service
GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/credenciales.json
```

**Ventajas**: ✅ Sin interacción del usuario, ✅ Ideal para CI/CD

#### Opción D: OAuth tradicional (🌐 Solo local)

**Ideal para**: Desarrollo local, pruebas rápidas.

1. Crea credenciales OAuth 2.0 en Google Cloud Console (tipo "Aplicación de escritorio")
2. Descarga `credentials.json` y ponlo en la raíz del proyecto
3. Configura en `.env`:

```bash
DRIVE_AUTH_MODE=oauth
```

4. La primera vez se abrirá un navegador para autorizar
5. Se creará automáticamente `token.json` con las credenciales

**Ventajas**: ✅ Rápido para desarrollo local

**Desventajas**: ❌ No funciona en Streamlit Cloud (requiere navegador local)

---

### Comparación de Modos de Autenticación

| Modo | Carpetas Públicas | Carpetas Privadas | Streamlit Cloud | Dificultad |
|------|-------------------|-------------------|-----------------|------------|
| **public** | ✅ | ❌ | ✅ | ⭐ Muy fácil |
| **oauth_streamlit** | ✅ | ✅ | ✅ | ⭐⭐ Fácil |
| **service** | ✅ | ✅ (si se comparte) | ✅ | ⭐⭐⭐ Media |
| **oauth** | ✅ | ✅ | ❌ | ⭐⭐ Fácil |

## 🎮 Uso

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

### Flujo de trabajo

1. **Configurar LLM**:
   - Selecciona proveedor (OpenAI, Anthropic, etc.)
   - Elige modelo (ej: gpt-4o-mini)
   - Verifica que la API key esté configurada ✅

2. **Definir Variables a Extraer**:
   - Usa el schema YAML por defecto o personalízalo
   - Valida que el schema sea correcto
   - Ejemplo de campos: nivel educativo, años experiencia, stack tecnológico, idiomas, etc.

3. **Cargar CVs**:
   - **Opción 1**: Arrastra archivos PDF/DOCX localmente
   - **Opción 2**: Pega ID de carpeta de Google Drive y lista archivos
   - Puedes combinar ambas fuentes

4. **Procesar**:
   - Haz clic en "🚀 Procesar CVs"
   - Observa la barra de progreso
   - Los errores se muestran pero no detienen el proceso

5. **Descargar Resultados**:
   - Ve a la pestaña "Resultados"
   - Visualiza la tabla con datos extraídos
   - Descarga en Excel, CSV o JSON

## 📝 Schema YAML

El schema define qué información extraer de cada CV. Ejemplo:

```yaml
version: 1
variables:
  - name: nivel_educativo_alcanzado
    type: categorical
    allowed_values: [secundario, terciario, universitario, posgrado, doctorado]
    required: true

  - name: años_experiencia
    type: integer
    min: 0
    max: 50
    required: true

  - name: stack_tecnológico
    type: list[string]
    required: false

  - name: idiomas
    type: list[object]
    properties:
      idioma: string
      nivel: [básico, intermedio, avanzado, nativo]
    required: false
```

### Tipos soportados:

- `string`: Texto libre
- `integer`: Número entero (con min/max opcional)
- `float`: Número decimal
- `boolean`: Verdadero/falso
- `categorical`: Valor de una lista fija
- `list[string]`: Lista de strings
- `list[object]`: Lista de objetos con propiedades definidas
- `object`: Objeto libre

## ⚙️ Opciones Avanzadas

- **Límite de archivos**: Máximo a procesar (default: 100)
- **Concurrencia**: Archivos en paralelo (default: 5)
- **Temperatura**: Creatividad del LLM (default: 0.1, recomendado bajo)
- **Max tokens**: Tokens máximos en respuesta (default: 2000)

## 🏗️ Estructura del Proyecto

```
cv_analyzer/
├── app.py                      # Aplicación Streamlit principal
├── llm_client/
│   ├── base.py                 # Interfaz abstracta
│   ├── openai_client.py        # Implementación OpenAI
│   └── litellm_client.py       # Implementación genérica (Anthropic, etc)
├── ingestion/
│   ├── drive.py                # Google Drive API
│   ├── local.py                # Archivos locales
│   └── hashing.py              # SHA1 hashing
├── parsing/
│   ├── pdf.py                  # Parser PDF (pymupdf + pdfplumber)
│   ├── docx.py                 # Parser DOCX (python-docx)
├── schema/
│   ├── yaml_loader.py          # Carga y valida YAML
│   └── validator.py            # Validación con pydantic
├── utils/
│   ├── excel.py                # Export a Excel/CSV/JSON
│   └── text_clean.py           # Normalización de texto
├── tests/
│   ├── test_schema.py
│   └── test_parsing.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Tests

Ejecutar tests:

```bash
# Instalar pytest si no está
pip install pytest

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar test específico
pytest tests/test_schema.py -v
```

## 🚢 Deployment en Streamlit Cloud

1. Push tu código a GitHub

2. Ve a [share.streamlit.io](https://share.streamlit.io)

3. Conecta tu repo

4. En "Advanced settings" → "Secrets", agrega:

```toml
[secrets]
openai_api_key = "sk-tu-api-key"
# O el proveedor que uses
```

5. Deploy! 🎉

## 💡 Buenas Prácticas

### Rendimiento

- **Usa lotes**: Configura concurrencia apropiada (5-10 paralelos)
- **Limita contexto**: Los LLMs tienen límites de tokens
- **Cache**: Los archivos se cachean por hash SHA1

### Costos

- **Modelo más barato**: Usa `gpt-4o-mini` para pruebas
- **Temperatura baja**: Reduce aleatoriedad = más consistencia
- **Limita tokens**: Max 2000 tokens suele ser suficiente

### Calidad

- **Schema claro**: Define bien los tipos y valores permitidos
- **Validación**: La app reintenta hasta 2 veces si falla validación
- **Texto limpio**: El normalizador remueve ruido automáticamente

## ⚠️ Troubleshooting

### "API key no encontrada"

- Verifica que `OPENAI_API_KEY` (o equivalente) esté en `.env`
- En Streamlit Cloud, verifica los secrets
- Reinicia la app después de cambiar variables de entorno

### "Error listando archivos de Drive"

- Verifica que `GOOGLE_APPLICATION_CREDENTIALS` apunte al archivo correcto
- Asegúrate de que la carpeta esté compartida con la service account
- Verifica que el folder ID sea correcto (extraído de la URL)

### "Error parseando PDF"

- Algunos PDFs son imágenes escaneadas (requiere OCR, no incluido)
- Verifica que el PDF tenga texto seleccionable
- Prueba con otro archivo para confirmar

### "Validación falló"

- Revisa el schema YAML
- Verifica que los `allowed_values` sean apropiados
- Chequea los logs para ver qué campo falló

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto. Úsalo libremente.

## 🙏 Reconocimientos

- [Streamlit](https://streamlit.io/) - Framework web
- [OpenAI](https://openai.com/) - API de LLM
- [LiteLLM](https://github.com/BerriAI/litellm) - Abstracción multi-proveedor
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Parsing PDF
- [python-docx](https://python-docx.readthedocs.io/) - Parsing DOCX

## 📧 Contacto

¿Preguntas? Abre un issue en GitHub.

---

**Hecho con ❤️ y ☕**
