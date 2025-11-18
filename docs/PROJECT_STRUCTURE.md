# 📁 Estructura del Proyecto CV Analyzer

```
cv_analyzer/
│
├── 📄 app.py                           # ⭐ Aplicación Streamlit principal
│
├── 📋 Archivos de Configuración
│   ├── requirements.txt                # Dependencias Python
│   ├── .env.example                    # Plantilla de variables de entorno
│   ├── .gitignore                      # Archivos a ignorar en Git
│   ├── package.json                    # Metadatos del proyecto
│   ├── Dockerfile                      # Configuración Docker
│   └── docker-compose.yml              # Orquestación Docker
│
├── 📚 Documentación
│   ├── README.md                       # Documentación principal
│   ├── QUICKSTART.md                   # Guía de inicio rápido
│   ├── DEPLOYMENT.md                   # Guía de deployment
│   ├── CONTRIBUTING.md                 # Guía para contribuir
│   ├── LICENSE                         # Licencia MIT
│   └── PROJECT_STRUCTURE.md            # Este archivo
│
├── 🚀 Scripts de Inicio
│   ├── start.sh                        # Script de inicio (macOS/Linux)
│   ├── start.bat                       # Script de inicio (Windows)
│   └── test_basic.py                   # Test básico sin UI
│
├── ⚙️ .streamlit/                      # Configuración de Streamlit
│   ├── config.toml                     # Configuración de tema y servidor
│   └── secrets.toml.example            # Ejemplo de secrets para deployment
│
├── 🤖 llm_client/                      # Cliente LLM con abstracción
│   ├── __init__.py                     # Exports del módulo
│   ├── base.py                         # Clase base abstracta
│   ├── openai_client.py                # Implementación OpenAI
│   └── litellm_client.py               # Implementación genérica (Anthropic, etc)
│
├── 📥 ingestion/                       # Ingesta de archivos
│   ├── __init__.py                     # Exports del módulo
│   ├── drive.py                        # Integración Google Drive API
│   ├── local.py                        # Procesamiento de uploads locales
│   └── hashing.py                      # Cálculo de hash SHA1
│
├── 📄 parsing/                         # Parsing de archivos
│   ├── __init__.py                     # Exports del módulo
│   ├── pdf.py                          # Parser PDF (pymupdf + pdfplumber)
│   └── docx.py                         # Parser DOCX (python-docx)
│
├── 📋 schema/                          # Validación de schema
│   ├── __init__.py                     # Exports del módulo
│   ├── yaml_loader.py                  # Carga y valida YAML
│   └── validator.py                    # Validación con pydantic
│
├── 🛠️ utils/                           # Utilidades generales
│   ├── __init__.py                     # Exports del módulo
│   ├── excel.py                        # Export a Excel/CSV/JSON
│   └── text_clean.py                   # Normalización de texto
│
└── 🧪 tests/                           # Tests unitarios
    ├── __init__.py                     # Exports del módulo
    ├── test_schema.py                  # Tests de schema y validación
    ├── test_parsing.py                 # Tests de parsing
    └── samples/                        # Archivos de ejemplo
        └── cv_ejemplo.txt              # CV de ejemplo para tests

```

## 🗺️ Flujo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                    Usuario en Streamlit UI                   │
│                          (app.py)                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ├──► 1. Configurar LLM & Schema
                        │      (llm_client/ + schema/)
                        │
                        ├──► 2. Cargar Archivos
                        │      ├─► Local (ingestion/local.py)
                        │      └─► Google Drive (ingestion/drive.py)
                        │
                        ├──► 3. Parsear Archivos
                        │      ├─► PDF (parsing/pdf.py)
                        │      └─► DOCX (parsing/docx.py)
                        │      └─► Normalizar (utils/text_clean.py)
                        │
                        ├──► 4. Extraer con LLM
                        │      └─► llm_client.extract_profile()
                        │          └─► Validar (schema/validator.py)
                        │
                        └──► 5. Exportar Resultados
                             └─► Excel/CSV/JSON (utils/excel.py)
```

## 📦 Módulos Principales

### 1. `app.py` - Aplicación Principal
- **Responsabilidad**: UI de Streamlit y orquestación
- **Dependencias**: Todos los módulos
- **Puntos clave**:
  - Configuración en sidebar
  - Tabs para upload, drive, resultados
  - Procesamiento concurrente con ThreadPoolExecutor
  - Manejo de errores por archivo

### 2. `llm_client/` - Cliente LLM
- **Responsabilidad**: Abstracción de proveedores LLM
- **Componentes**:
  - `base.py`: Interfaz abstracta
  - `openai_client.py`: Implementación OpenAI
  - `litellm_client.py`: Otros proveedores
- **Features**:
  - Retry automático con tenacity
  - Validación y corrección de respuestas
  - Prompts optimizados

### 3. `ingestion/` - Ingesta de Archivos
- **Responsabilidad**: Obtener archivos de diferentes fuentes
- **Componentes**:
  - `drive.py`: Google Drive API (OAuth + Service Account)
  - `local.py`: Archivos subidos vía Streamlit
  - `hashing.py`: SHA1 para deduplicación
- **Features**:
  - Streaming de archivos (no guardar en disco)
  - Validación de MIME types
  - Metadatos de archivos

### 4. `parsing/` - Parsing de Archivos
- **Responsabilidad**: Extraer texto de PDFs y DOCXs
- **Componentes**:
  - `pdf.py`: pymupdf + fallback a pdfplumber
  - `docx.py`: python-docx con preservación de estructura
- **Features**:
  - Fallback automático si un parser falla
  - Extracción de tablas
  - Manejo de PDFs con imágenes

### 5. `schema/` - Validación de Schema
- **Responsabilidad**: Definir y validar estructura de datos
- **Componentes**:
  - `yaml_loader.py`: Carga y valida YAML custom
  - `validator.py`: Validación con pydantic + jsonschema
- **Features**:
  - Schema YAML personalizable
  - Conversión a JSON Schema
  - Modelos pydantic dinámicos
  - Mensajes de error claros

### 6. `utils/` - Utilidades
- **Responsabilidad**: Funciones auxiliares
- **Componentes**:
  - `excel.py`: Export con formato profesional
  - `text_clean.py`: Normalización inteligente
- **Features**:
  - Serialización de tipos complejos (listas, objetos)
  - Remoción de headers/footers repetitivos
  - Preservación de estructura (bullets, secciones)

### 7. `tests/` - Tests Unitarios
- **Responsabilidad**: Verificar funcionalidad
- **Componentes**:
  - `test_schema.py`: Tests de validación
  - `test_parsing.py`: Tests de parsing
- **Features**:
  - Tests con pytest
  - Fixtures y mocks
  - Coverage reports

## 🔗 Dependencias entre Módulos

```
app.py
├── llm_client/
│   ├── schema/ (para validación)
│   └── utils/ (indirectamente)
├── ingestion/
│   └── (sin dependencias internas)
├── parsing/
│   └── utils/text_clean
├── schema/
│   └── (sin dependencias internas)
└── utils/
    └── (sin dependencias internas)
```

**Principio**: Los módulos base (`ingestion/`, `parsing/`, `schema/`, `utils/`) son independientes.
Solo `app.py` y `llm_client/` los orquestan.

## 📝 Convenciones de Código

### Naming
- **Módulos/archivos**: `snake_case`
- **Clases**: `PascalCase`
- **Funciones/variables**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`

### Type Hints
```python
def process_cv(
    file_path: str,
    schema: Dict[str, Any],
    options: Optional[ProcessingOptions] = None
) -> CVResult:
    """Siempre usar type hints."""
    pass
```

### Docstrings
```python
def mi_funcion(param: str) -> int:
    """
    Formato Google docstring.

    Args:
        param: Descripción

    Returns:
        Descripción del return

    Raises:
        ValueError: Cuándo se lanza
    """
    pass
```

## 🎯 Puntos de Extensión

Para agregar nuevas funcionalidades:

### 1. Nuevo proveedor LLM
1. Crear `llm_client/mi_proveedor_client.py`
2. Heredar de `BaseLLMClient`
3. Implementar `extract_profile()`
4. Agregar a selector en `app.py`

### 2. Nuevo formato de archivo
1. Crear `parsing/mi_formato.py`
2. Implementar función `parse_mi_formato(bytes) -> str`
3. Agregar MIME type a `ingestion/local.py`
4. Integrar en `app.py`

### 3. Nueva fuente de archivos
1. Crear `ingestion/mi_fuente.py`
2. Implementar `list_files()` y `download_file()`
3. Agregar UI en `app.py`

### 4. Nuevo formato de export
1. Agregar función `export_to_X()` en `utils/excel.py`
2. Agregar botón de descarga en `app.py`

## 🔒 Seguridad

### Datos Sensibles
- ✅ API keys solo en `.env` o secrets
- ✅ Credenciales Google en archivos `.json` (gitignored)
- ✅ No loggear información personal de CVs

### Validación
- ✅ Validar tamaño de archivos (max 200MB)
- ✅ Verificar MIME types
- ✅ Sanitizar nombres de archivos
- ✅ Rate limiting en producción

## 📈 Performance

### Optimizaciones Implementadas
- ✅ Procesamiento concurrente (ThreadPoolExecutor)
- ✅ Streaming de archivos (no guardar en disco)
- ✅ Cache por hash SHA1
- ✅ Retry con backoff exponencial

### Para Escalar
- 🔄 Redis para cache distribuido
- 🔄 Celery para queue de trabajos
- 🔄 PostgreSQL para persistencia
- 🔄 Elasticsearch para búsqueda

## 🐛 Debugging

### Logs
Los logs se imprimen en la consola donde ejecutas `streamlit run app.py`.

### Variables de Entorno de Debug
```bash
# Ver logs detallados de LiteLLM
export LITELLM_LOG=DEBUG

# Ver logs de Google API
export GOOGLE_API_LOG_LEVEL=DEBUG
```

### Streamlit Debug
```bash
# Modo development con hot reload
streamlit run app.py --server.runOnSave true

# Ver logs de Streamlit
streamlit run app.py --logger.level=debug
```

## 📞 Ayuda

Si tienes preguntas sobre la estructura:
1. Lee los docstrings en el código
2. Revisa los tests para ver ejemplos de uso
3. Abre un issue en GitHub
4. Consulta CONTRIBUTING.md

---

**¡Feliz coding! 💻✨**
