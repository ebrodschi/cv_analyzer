# Configuración de OCR con Docling

## ¿Qué es OCR y por qué usarlo?

# Guía de OCR con Docling

## 📢 Resumen

Se ha implementado soporte para **OCR (Reconocimiento Óptico de Caracteres)** usando **Docling**. El sistema ahora puede **detectar fotos en CVs**, una variable crítica que antes no se podía analizar.

### ✨ Características

- ✅ **Detección de fotos** en CVs (PDF y DOCX)
- ✅ **Extracción mejorada** de texto en imágenes y PDFs escaneados
- ✅ **OCR opcional** - activar/desactivar desde la UI
- ✅ **100% compatible** con código anterior (sin breaking changes)
- ✅ **Fallback automático** si Docling no está instalado
- ✅ **Integración con schema existente** - usa el campo `hay_foto_en_cv` ya definido

### 🎯 ¿Por qué es importante?

Detectar fotos en CVs es útil para:
- **Cumplimiento normativo**: GDPR, normativas de privacidad
- **Selección ciega**: procesos sin sesgos visuales
- **Análisis de diversidad**: identificar prácticas inclusivas

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Instalar Docling
pip install docling
```

**Nota**: Si no instalas Docling, el sistema funcionará con el método tradicional (pymupdf + pdfplumber), pero no podrá detectar fotos.

### 2. Usar en la Aplicación

1. Ejecuta: `streamlit run app.py`
2. Sidebar → **"🔧 Opciones Avanzadas"**
3. ✅ Activa: **"🖼️ Usar OCR (Docling) para detectar fotos"**
4. Procesa tus CVs normalmente

### 3. Resultados

Con OCR activado, el campo `hay_foto_en_cv` del schema se completará correctamente:

| archivo | nombre | **hay_foto_en_cv** | score |
|---------|--------|--------------------|-------|
| juan.pdf | Juan Pérez | True | 8.5 |
| maria.pdf | María Gómez | False | 7.8 |

**Nota**: El sistema usa el campo `hay_foto_en_cv` que ya está definido en el schema YAML. No agrega columnas adicionales.

## 📊 Comparación: OCR vs Tradicional

| Característica | Sin OCR (pymupdf/pdfplumber) | Con OCR (Docling) |
|----------------|------------------------------|-------------------|
| Velocidad | ⚡ 2-5 seg/CV | 🐌 10-20 seg/CV |
| Memoria | 💚 Baja | 💛 Media/Alta |
| Detecta fotos | ❌ No | ✅ Sí |
| Texto en imágenes | ❌ No | ✅ Sí (OCR) |
| PDFs escaneados | ❌ No | ✅ Sí (OCR) |
| Tablas complejas | 🟡 Limitado | ✅ Excelente |
| Dependencias | Mínimas | +Docling (~500MB) |

### ¿Cuándo usar cada método?

**✅ Usa OCR cuando:**
- Necesites detectar fotos en CVs
- Los CVs estén escaneados (imágenes)
- Necesites extraer texto de imágenes
- Tengas diseños complejos con tablas

**⚡ Usa método tradicional cuando:**
- La velocidad sea prioridad
- No necesites detectar fotos
- Los CVs sean PDF con texto seleccionable
- Proceses grandes volúmenes (100+ CVs)

### Configuración recomendada

**Procesamiento rápido (sin OCR):**
```
OCR: [ ] Desactivado
Concurrencia: 5-10 workers
Tiempo: ~2-5 segundos por CV
```

**Máxima precisión (con OCR):**
```
OCR: [✓] Activado
Concurrencia: 2-3 workers
Tiempo: ~10-20 segundos por CV
```

## 🧪 Probar OCR

### Script de prueba

```bash
# Probar con OCR
python test_ocr.py mi_cv.pdf

# Probar sin OCR
python test_ocr.py mi_cv.pdf --no-ocr

# Comparar ambos métodos
python test_ocr.py mi_cv.pdf --compare
```

### Ejemplo en código Python

```python
from parsing.pdf import parse_pdf

with open('cv.pdf', 'rb') as f:
    content = f.read()

# Con OCR - detecta fotos
result = parse_pdf(content, use_ocr=True)
print(f"Tiene foto: {result['has_photo']}")
print(f"Imágenes: {result['images_count']}")
print(f"Texto: {result['text'][:200]}")

# Sin OCR - más rápido
text = parse_pdf(content, use_ocr=False)
print(f"Texto: {text[:200]}")
```

## 🔧 Cómo Funciona

### Arquitectura

```
Usuario activa OCR en UI
    ↓
app.py → parse_file(content, use_ocr=True)
    ↓
parsing/pdf.py → parse_pdf(content, use_ocr=True)
    ↓
parsing/ocr.py → parse_with_docling()
    ↓
    ┌─ Crea archivo temporal
    │  (Docling requiere Path, no BytesIO)
    ↓
    ┌─ Detecta fotos? ─┐
    │                  │
   Sí                 No
    │                  │
    ↓                  ↓
Agrega nota al texto  Solo texto
    │                  │
    └──────┬───────────┘
           ↓
   Texto con contexto de foto
           ↓
   LLM extrae hay_foto_en_cv
   (usa info del contexto)
           ↓
   Resultado con campo del schema
```

### Detalle del Proceso

1. **Parseo con OCR**:
   - Crea archivo temporal en disco (Docling lo requiere)
   - Ejecuta Docling con OCR habilitado
   - Detecta imágenes en el documento

2. **Enriquecimiento del texto**:
   - Si detecta foto: agrega nota al principio del texto
   - Ejemplo: `[NOTA: Este CV contiene 1 imagen(es)/foto(s)]`

3. **Extracción con LLM**:
   - El LLM lee el texto con la nota
   - Extrae `hay_foto_en_cv` como cualquier otro campo del schema
   - No requiere columnas adicionales

### Ventaja de este enfoque

✅ **Usa el schema existente** - No agrega columnas extras
✅ **Flexible** - El LLM puede usar contexto para mejorar precisión
✅ **Coherente** - Todos los campos se extraen de la misma forma

## 🔧 Troubleshooting

### Error: "Docling no está instalado"
```bash
pip install docling
```

### Error: "4 validation errors for DocumentConverter.convert"
Este error ocurría en versiones anteriores del código. Ya está corregido. El sistema ahora:
- ✅ Crea archivos temporales en disco (Docling los requiere)
- ✅ Usa el API correcto de Docling
- ✅ Limpia automáticamente los archivos temporales

Si aún ves este error, asegúrate de tener la última versión del código.

### Error: "Import docling could not be resolved"
Reinicia tu entorno Python:
```bash
deactivate
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate en Windows

pip install docling
```

### OCR muy lento
- Reduce concurrencia a 2-3 workers
- Procesa menos archivos por lote
- Desactiva OCR para grandes volúmenes

### No detecta fotos
1. Verifica que el checkbox OCR esté **activado**
2. Revisa logs en la terminal para advertencias
3. Algunos PDFs tienen fotos como fondo (no siempre detectables)

### Fallback automático
Si ves este mensaje, Docling no está disponible:
```
⚠️ Docling no disponible. Cayendo a método tradicional sin OCR.
   Para usar OCR, instala: pip install docling
```

## 💡 Casos de Uso

### Cumplimiento de Privacidad
```
Necesidad: Identificar CVs con fotos para GDPR
Solución:  Activar OCR, filtrar por tiene_foto=True
Resultado: Lista de CVs que requieren revisión
```

### Selección Ciega
```
Necesidad: Proceso sin sesgos visuales
Solución:  Procesar con OCR, remover CVs con foto
Resultado: Selección basada solo en competencias
```

### CVs Escaneados
```
Necesidad: Extraer texto de CVs en papel
Solución:  Activar OCR para leer documentos escaneados
Resultado: Extracción precisa de datos
```

## 📚 Detalles Técnicos

### Archivos modificados

```
✨ NUEVOS:
- parsing/ocr.py          # Funciones OCR con Docling
- test_ocr.py             # Script de pruebas

✏️ MODIFICADOS:
- app.py                  # Checkbox OCR + procesamiento
- parsing/pdf.py          # Parámetro use_ocr
- parsing/docx.py         # Parámetro use_ocr
- requirements.txt        # Agregado docling>=2.0.0
```

### Flujo de procesamiento

```
Usuario activa OCR en UI
    ↓
app.py → parse_file(content, use_ocr=True)
    ↓
parsing/pdf.py → parse_pdf(content, use_ocr=True)
    ↓
¿Docling instalado?
    │
    ├─ Sí → parsing/ocr.py → parse_with_docling()
    │        └─ Retorna {text, has_photo, images_count}
    │
    └─ No → Fallback a pymupdf/pdfplumber
             └─ Retorna {text, has_photo: False}
```

### Estructura de retorno

**Con OCR:**
```python
{
    'text': "Texto extraído...",
    'has_photo': True,
    'images_count': 1,
    'metadata': {'pages': 2, 'tables_count': 1}
}
```

**Sin OCR:**
```python
"Texto extraído..."  # string simple
```

## ❓ Preguntas Frecuentes

**P: ¿Es obligatorio instalar Docling?**
R: No, es completamente opcional. El sistema funciona perfectamente sin OCR.

**P: ¿Qué pasa si no instalo Docling?**
R: La aplicación funciona normalmente con el método tradicional. Solo no podrás detectar fotos.

**P: ¿Funciona el código anterior sin cambios?**
R: Sí, 100% compatible. OCR solo se activa si lo habilitas.

**P: ¿Puedo cambiar entre OCR y sin OCR?**
R: Sí, simplemente activa/desactiva el checkbox en las opciones avanzadas.

**P: ¿Funciona con DOCX también?**
R: Sí, tanto PDF como DOCX soportan OCR.

**P: ¿Qué es Docling?**
R: Librería de IBM Research para procesamiento avanzado de documentos con OCR, detección de tablas y elementos visuales.

## 🔗 Referencias

- [Docling GitHub](https://github.com/DS4SD/docling) - Repositorio oficial
- [PyMuPDF](https://pymupdf.readthedocs.io/) - Librería tradicional para PDFs
- [pdfplumber](https://github.com/jsvine/pdfplumber) - Alternativa para PDFs complejos
