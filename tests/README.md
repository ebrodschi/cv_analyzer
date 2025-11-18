# 🧪 Tests del CV Analyzer

Esta carpeta contiene todos los tests y scripts de verificación del proyecto.

## 📋 Archivos de Test

### Tests Básicos
- **`test_basic.py`** - Tests básicos de funcionalidad
- **`test_parsing.py`** - Tests de parsing de archivos PDF/DOCX

### Tests de Google Drive
- **`test_drive_auth.py`** - Tests de autenticación con Google Drive

### Tests de Schema
- **`test_schema.py`** - Tests de validación de schemas
- **`test_schema_default.py`** - Tests del schema por defecto
- **`test_schema_updated.py`** - Tests de schemas actualizados

### Verificación
- **`verify_setup.py`** - Script para verificar que la instalación esté correcta

## 🚀 Cómo Ejecutar Tests

### Ejecutar todos los tests:
```bash
pytest
```

### Ejecutar un test específico:
```bash
pytest tests/test_basic.py
```

### Ejecutar con verbose:
```bash
pytest -v
```

### Verificar la instalación:
```bash
python tests/verify_setup.py
```

## 📊 Test Samples

La carpeta `samples/` contiene archivos de ejemplo para testing:
- `cv_ejemplo.txt` - CV de ejemplo en texto plano

## 🛠️ Requisitos

Los tests requieren las mismas dependencias que el proyecto principal, definidas en `requirements.txt`.

## ✅ Best Practices

- Agregar tests para nuevas funcionalidades
- Mantener cobertura de tests alta
- Usar fixtures para datos de test comunes
- Documentar casos edge en los tests
