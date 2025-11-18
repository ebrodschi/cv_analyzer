# Quick Start Guide

## 🚀 Inicio Rápido (5 minutos)

### Prerequisitos
- Python 3.9+ instalado
- API key de OpenAI (consíguela en [platform.openai.com](https://platform.openai.com/api-keys))

### Pasos

#### 1️⃣ Usar el script automático

**En macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**En Windows:**
```cmd
start.bat
```

El script hará todo automáticamente:
- ✅ Crear entorno virtual
- ✅ Instalar dependencias
- ✅ Crear archivo .env
- ✅ Iniciar la aplicación

#### 2️⃣ Configurar API Key

Cuando el script te lo pida, edita `.env`:

```bash
# macOS/Linux
nano .env

# Windows
notepad .env
```

Reemplaza `sk-your-openai-api-key-here` con tu API key real de OpenAI.

#### 3️⃣ ¡Listo!

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 🧪 Test Rápido (sin UI)

Para probar la funcionalidad sin abrir la UI:

```bash
# Activa el entorno virtual primero
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate.bat  # Windows

# Ejecuta el test
python test_basic.py
```

Este script:
- ✅ Valida el schema
- ✅ Inicializa el cliente LLM
- ✅ Procesa un CV de ejemplo
- ✅ Muestra los datos extraídos

---

## 📖 Uso Básico

### 1. Subir CVs Localmente

1. Ve a la pestaña "📤 Subir Archivos"
2. Arrastra archivos PDF o DOCX
3. Haz clic en "🚀 Procesar CVs"

### 2. Usar Google Drive (Opcional)

1. Configura credenciales (ver README.md completo)
2. En la sidebar, pega el ID de carpeta de Drive
3. Haz clic en "🔍 Listar Archivos"
4. Procesa los archivos encontrados

### 3. Personalizar Schema

1. En la sidebar, desmarca "Usar esquema por defecto"
2. Edita el YAML para definir qué campos extraer
3. El schema se valida automáticamente

### 4. Descargar Resultados

1. Ve a la pestaña "📊 Resultados"
2. Visualiza la tabla de datos
3. Descarga en Excel, CSV o JSON

---

## ⚡ Comandos Útiles

```bash
# Ejecutar aplicación
streamlit run app.py

# Ejecutar tests
pytest tests/ -v

# Test básico sin UI
python test_basic.py

# Instalar nueva dependencia
pip install nombre-paquete
pip freeze > requirements.txt

# Limpiar cache de Streamlit
streamlit cache clear
```

---

## 🔧 Troubleshooting Rápido

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API key not found"
Verifica que `.env` exista y contenga:
```
OPENAI_API_KEY=sk-tu-key-real-aquí
```

### Puerto 8501 en uso
```bash
streamlit run app.py --server.port 8502
```

### Limpiar todo y empezar de nuevo
```bash
rm -rf venv
rm .env
./start.sh  # o start.bat en Windows
```

---

## 📚 Más Información

- **README completo**: Ver `README.md`
- **Documentación de código**: Todos los módulos tienen docstrings
- **Ejemplos**: Ver `tests/samples/`

---

## 💡 Tips

1. **Usa gpt-4o-mini** para pruebas (más barato)
2. **Limita a 10 archivos** al principio para probar
3. **Temperatura baja (0.1)** para extracción consistente
4. **Revisa la pestaña Resultados** para errores por archivo

---

## 🆘 ¿Necesitas Ayuda?

1. Revisa los errores en la UI (se muestran por archivo)
2. Ejecuta `python test_basic.py` para diagnóstico
3. Verifica los logs en la consola donde ejecutaste streamlit
4. Abre un issue en GitHub con:
   - Mensaje de error completo
   - Versión de Python (`python --version`)
   - Sistema operativo

---

**¡Disfruta analizando CVs! 📄✨**
