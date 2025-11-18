# Sistema de Configuración de Prompts

## Descripción

Este sistema permite configurar de forma dinámica los prompts de análisis de CVs según el perfil/especialidad buscado, la localidad de la posición y criterios personalizados de evaluación.

## Características Principales

### 1. Especialidades Predefinidas

El sistema incluye plantillas predefinidas para las siguientes especialidades:

- **Electricista**: Mantenimiento industrial eléctrico
- **Electromecánico**: Mantenimiento industrial electromecánico
- **Mecánico**: Mecánico industrial y soldador
- **Pañolero**: Pañolero industrial
- **Personalizado**: Permite definir tu propia especialidad

### 2. Configuración desde la UI

En la interfaz de Streamlit, en la sección **"🎯 Configuración de Análisis"**, puedes configurar:

#### Especialidad/Perfil
Selecciona una especialidad predefinida o elige "personalizado" para definir tu propia búsqueda.

#### Localidad y Radio
- **Localidad**: Ubicación de la posición a cubrir (ej: "Lanús, Buenos Aires")
- **Radio (km)**: Distancia aceptable desde la localidad (por defecto: 10 km)

#### Criterios de Score (Avanzado)
Puedes usar los criterios por defecto o definir tus propios criterios para calcular el score del 1 al 10.

**Criterios por defecto:**
```
🎯 Criterios para el score (1-10):

Educación relevante (hasta 2 puntos):
• +1 si culminó el secundario
• +1 si el secundario es técnico

Experiencia (hasta 4 puntos):
• +1 si tiene más de 2 años
• +1 si tiene más de 3 años
• +1 si trabajó en fábricas industriales y rubros afines
• +1 si tuvo responsabilidades específicas o lideró tareas

Claridad y presentación del CV (hasta 1 punto):
• 1 punto si está bien organizado, con fechas y descripciones claras

Conocimientos técnicos (hasta 2 puntos):
• Presencia de conocimientos relevantes para la posición

Ubicación geográfica (hasta 1 punto):
• +1 si reside en la zona objetivo o radio cercano
```

#### Configuración Personalizada
Si seleccionas "personalizado", puedes definir:
- **Título de la posición**
- **Nombre del campo de experiencia** (ej: `experiencia_soldador_confirmada`)
- **Descripción de experiencia requerida**

### 3. Variables a Extraer

El schema YAML define qué campos se extraerán del CV. Ejemplo para electricistas:

```yaml
variables:
  - name: nombre
    type: string
    required: false

  - name: primaria_completa
    type: boolean
    required: true

  - name: secundaria_completa
    type: boolean
    required: true

  - name: experiencia_electricista_confirmada
    type: boolean
    required: true

  - name: años_experiencia
    type: integer
    min: 0
    max: 50
    required: true

  - name: score_general
    type: integer
    min: 1
    max: 10
    required: true
```

## Uso

### Paso 1: Configurar LLM
En la sidebar, configura el proveedor de LLM (OpenAI, Anthropic, etc.) y el modelo a usar.

### Paso 2: Definir Variables
En la sección "📝 Variables a Extraer", define o carga un schema YAML con los campos a extraer.

### Paso 3: Configurar Análisis
En la sección "🎯 Configuración de Análisis":
1. Selecciona la especialidad
2. Ingresa la localidad de la posición
3. Ajusta el radio en kilómetros
4. (Opcional) Personaliza los criterios de score

### Paso 4: Subir CVs
- **Tab "📤 Subir Archivos"**: Sube archivos PDF/DOCX locales
- **Tab "☁️ Google Drive"**: Conecta con Google Drive para listar archivos

### Paso 5: Procesar
Haz clic en **"🚀 Procesar CVs"** para analizar los archivos con las configuraciones definidas.

### Paso 6: Ver Resultados
En el tab **"📊 Resultados"**, visualiza y descarga los datos extraídos en formato Excel, CSV o JSON.

## Ejemplos de Uso

### Ejemplo 1: Electricista en Lanús
```
Especialidad: Electricista
Localidad: Lanús, Buenos Aires, Argentina
Radio: 10 km
Criterios: Por defecto
```

### Ejemplo 2: Mecánico en Lugano
```
Especialidad: Mecánico
Localidad: Lugano, Capital Federal, Argentina
Radio: 10 km
Criterios: Por defecto
```

### Ejemplo 3: Perfil Personalizado
```
Especialidad: Personalizado
  - Título: Técnico en Refrigeración
  - Campo experiencia: experiencia_refrigeracion_confirmada
  - Descripción: trabajo previo con sistemas de refrigeración industrial
Localidad: Ramos Mejía, Buenos Aires
Radio: 15 km
Criterios: Personalizados (definir en text area)
```

## Estructura de Archivos

```
llm_client/
├── base.py                    # Clase base abstracta
├── openai_client.py           # Cliente OpenAI
├── litellm_client.py          # Cliente LiteLLM (Anthropic, Azure, etc.)
└── prompt_templates.py        # Sistema de plantillas configurables ⭐

schema/
├── validator.py               # Validación de schemas
├── yaml_loader.py             # Carga de schemas YAML
└── electricista_schema.yaml   # Ejemplo de schema para electricistas

app.py                         # Aplicación Streamlit principal
```

## Archivos Clave Modificados

1. **`llm_client/prompt_templates.py`** (NUEVO)
   - Clase `PromptConfig`: Gestiona configuración de prompts
   - Templates predefinidos para especialidades
   - Generación dinámica de prompts

2. **`llm_client/base.py`**
   - Actualizado para soportar `PromptConfig` como parámetro opcional

3. **`llm_client/openai_client.py`** y **`llm_client/litellm_client.py`**
   - Método `extract_profile` actualizado para recibir `PromptConfig`
   - Método `_build_extraction_prompt` usa el sistema de templates

4. **`app.py`**
   - Nueva función `configure_prompt_settings()`: UI para configurar prompts
   - Funciones de procesamiento actualizadas para pasar la configuración

## Notas Importantes

- Los prompts se adaptan automáticamente según la especialidad seleccionada
- Los campos del schema deben coincidir con los campos mencionados en las definiciones
- El sistema valida automáticamente el JSON devuelto por el LLM
- Se pueden agregar nuevas especialidades editando `ESPECIALIDAD_TEMPLATES` en `prompt_templates.py`

## Próximos Pasos

Para agregar una nueva especialidad predefinida:

1. Edita `llm_client/prompt_templates.py`
2. Agrega un nuevo entry en `ESPECIALIDAD_TEMPLATES`:
   ```python
   "tu_especialidad": {
       "titulo": "Título del Puesto",
       "experiencia_campo": "experiencia_campo_confirmada",
       "descripcion_experiencia": "descripción de la experiencia",
       "exclusiones": "qué NO debe incluirse",
       "rango_edad": "25-45",
       "conocimientos_relevantes": "conocimientos técnicos importantes",
       "industrias_relevantes": "industrias o sectores relevantes",
   }
   ```
3. Crea un schema YAML correspondiente en `schema/`
