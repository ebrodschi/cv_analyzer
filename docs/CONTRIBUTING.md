# Contributing to CV Analyzer

¡Gracias por tu interés en contribuir! 🎉

## 🤝 Cómo Contribuir

### Reportar Bugs

1. Verifica que el bug no esté ya reportado en [Issues](https://github.com/tuusuario/cv-analyzer/issues)
2. Crea un nuevo issue con:
   - Título descriptivo
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots (si aplica)
   - Versión de Python y SO

### Sugerir Features

1. Abre un issue con el tag `enhancement`
2. Describe claramente el feature y su beneficio
3. Si es posible, incluye mockups o ejemplos

### Pull Requests

1. **Fork el repo**
   ```bash
   git clone https://github.com/tuusuario/cv-analyzer.git
   cd cv-analyzer
   ```

2. **Crea una branch**
   ```bash
   git checkout -b feature/mi-nuevo-feature
   # o
   git checkout -b fix/mi-bug-fix
   ```

3. **Desarrolla tu cambio**
   - Sigue el estilo de código existente
   - Agrega tests si es necesario
   - Actualiza documentación
   - Mantén commits atómicos y descriptivos

4. **Ejecuta tests**
   ```bash
   pytest tests/ -v
   python test_basic.py
   ```

5. **Commit y push**
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   git push origin feature/mi-nuevo-feature
   ```

6. **Abre Pull Request**
   - Describe los cambios claramente
   - Referencia issues relacionados
   - Incluye screenshots si hay cambios visuales

## 📝 Guías de Estilo

### Python

Seguimos [PEP 8](https://pep8.org/):

```python
# ✅ Bueno
def process_cv_file(file_path: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa un archivo de CV y extrae información.

    Args:
        file_path: Ruta al archivo
        schema: Schema de extracción

    Returns:
        Datos extraídos
    """
    result = parse_and_extract(file_path, schema)
    return result

# ❌ Malo
def processFile(filePath,schema):
    result=parseExtract(filePath,schema)
    return result
```

### Docstrings

Usa formato Google:

```python
def mi_funcion(param1: str, param2: int) -> bool:
    """
    Breve descripción en una línea.

    Descripción más detallada si es necesario,
    explicando el propósito y comportamiento.

    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2

    Returns:
        Descripción del valor de retorno

    Raises:
        ValueError: Cuándo se lanza y por qué
    """
    pass
```

### Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat: agregar soporte para archivos RTF
fix: corregir parsing de fechas en CVs
docs: actualizar README con nuevos ejemplos
style: formatear código según PEP 8
refactor: reorganizar módulo de parsing
test: agregar tests para validación de schema
chore: actualizar dependencias
```

## 🏗️ Estructura de Módulos

Al agregar nuevas funcionalidades:

```
cv_analyzer/
├── nuevo_modulo/
│   ├── __init__.py          # Exports públicos
│   ├── core.py              # Lógica principal
│   ├── utils.py             # Utilidades
│   └── types.py             # Type hints / modelos
├── tests/
│   └── test_nuevo_modulo.py # Tests completos
└── README.md                # Actualizar con nueva funcionalidad
```

## 🧪 Tests

### Escribir Tests

```python
# tests/test_nuevo_feature.py
import pytest
from nuevo_modulo import nueva_funcion

def test_nueva_funcion_caso_normal():
    """Test caso de uso normal."""
    resultado = nueva_funcion("input")
    assert resultado == "output esperado"

def test_nueva_funcion_caso_error():
    """Test manejo de errores."""
    with pytest.raises(ValueError):
        nueva_funcion("input inválido")

def test_nueva_funcion_edge_cases():
    """Test casos borde."""
    assert nueva_funcion("") == ""
    assert nueva_funcion(None) is None
```

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_nuevo_modulo.py -v

# Con coverage
pytest tests/ --cov=. --cov-report=html
```

## 📚 Documentación

Al agregar features:

1. **Docstrings en el código**
2. **Actualizar README.md** con ejemplos
3. **Agregar a QUICKSTART.md** si es relevante
4. **Actualizar DEPLOYMENT.md** si afecta deployment

## 🔍 Code Review

Tu PR será revisado considerando:

- ✅ Funcionalidad correcta
- ✅ Tests apropiados
- ✅ Código limpio y legible
- ✅ Documentación actualizada
- ✅ Sin breaking changes (o justificados)
- ✅ Performance aceptable

## 🎯 Áreas para Contribuir

### Fácil (Good First Issue)

- Mejorar mensajes de error
- Agregar más tests
- Mejorar documentación
- Agregar ejemplos de uso
- Traducir documentación

### Intermedio

- Agregar soporte para nuevos formatos (RTF, ODT)
- Implementar cache con Redis
- Mejorar UI/UX de Streamlit
- Agregar más proveedores LLM
- Optimizar parsing de PDFs

### Avanzado

- Implementar OCR para PDFs escaneados
- Sistema de queue para procesamiento async
- API REST además de UI
- Análisis batch con Celery
- Integración con otros storage (S3, Azure Blob)

## 💬 Comunicación

- **Issues**: Para bugs, features, preguntas
- **Discussions**: Para ideas, arquitectura, roadmap
- **Discord/Slack**: (Si hay) Para chat en tiempo real

## 🙏 Reconocimiento

Los contribuidores serán listados en el README y releases.

## ❓ Preguntas

No dudes en:
- Abrir un issue con tus preguntas
- Comentar en PRs existentes
- Contactar a los maintainers

---

**¡Gracias por contribuir a CV Analyzer! 🚀**
