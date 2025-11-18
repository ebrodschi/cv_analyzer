# 🔑 Guía de Configuración de API Keys

## 📋 Sistema de Prioridad de API Keys

La aplicación carga las API keys en el siguiente orden de prioridad:

```
1º .env (archivo local)
  ↓ Si no existe...
2º Variables de entorno del sistema
  ↓ Si no existe...
3º Streamlit secrets (para deployment)
  ↓ Si no existe...
4º Input manual por UI (temporal)
```

---

## ⚡ Configuración Rápida (Recomendada)

### Paso 1: Crear archivo .env

```bash
# En la raíz del proyecto, copia el archivo de ejemplo:
cp .env.example .env
```

### Paso 2: Editar el archivo .env

Abre el archivo `.env` y descomenta/completa tu API key:

```bash
# Para OpenAI:
OPENAI_API_KEY=sk-tu-api-key-real-aqui

# O para Anthropic:
# ANTHROPIC_API_KEY=sk-ant-tu-api-key-aqui

# O para Google Gemini (económico):
# GEMINI_API_KEY=AIzaSy-tu-gemini-api-key-aqui
# Obtén tu API key en: https://aistudio.google.com/app/apikey
```

### Paso 3: Reiniciar la aplicación

```bash
# Detén la app (Ctrl+C) y vuelve a iniciarla:
streamlit run app.py
```

✅ **¡Listo!** La app ahora usará tu API key del archivo `.env`

---

## 🔒 Ventajas del archivo .env

### ✅ Aislamiento del sistema
- No contamina las variables de entorno globales
- Cada proyecto tiene sus propias keys
- Fácil de cambiar entre diferentes API keys

### ✅ Seguridad
- `.env` está en `.gitignore` (no se sube a Git)
- Las keys no quedan guardadas en tu historial de shell
- Fácil de compartir el proyecto sin exponer keys

### ✅ Simplicidad
- Un solo archivo para todas las configuraciones
- Fácil de documentar y mantener
- Compatible con Docker y otros tools

---

## 🚫 NO Usar Variables de Entorno del Sistema

Si tienes `OPENAI_API_KEY` en tu `.bashrc`, `.zshrc`, o similar:

### Problema
```bash
# En ~/.zshrc o ~/.bashrc
export OPENAI_API_KEY=sk-...  # ❌ Afecta TODOS los proyectos
```

### Solución
1. **Elimina** esa línea de tu archivo de shell
2. **Usa** archivo `.env` en cada proyecto

```bash
# En ~/.zshrc (ELIMINAR):
# export OPENAI_API_KEY=sk-...  # ← Comentar o eliminar

# Luego:
source ~/.zshrc  # Recargar configuración
```

---

## 💡 Opciones Alternativas

### Opción 1: Archivo .env (Recomendado) ⭐

**Cuándo usar**: Desarrollo local, proyectos personales

```bash
# .env
OPENAI_API_KEY=sk-tu-key-aqui
```

**Pros**:
- ✅ Aislado por proyecto
- ✅ No afecta otros proyectos
- ✅ Fácil de versionar (con .env.example)

**Contras**:
- ⚠️ Debes crear el archivo manualmente

---

### Opción 2: Streamlit Secrets

**Cuándo usar**: Deployment en Streamlit Cloud

```toml
# .streamlit/secrets.toml
openai_api_key = "sk-tu-key-aqui"
```

**Pros**:
- ✅ Seguro para deployment
- ✅ Interfaz web de Streamlit Cloud

**Contras**:
- ⚠️ Solo funciona en Streamlit Cloud
- ⚠️ No disponible en local

---

### Opción 3: Input Manual por UI

**Cuándo usar**: Pruebas rápidas, demostraciones

La app te permite ingresar la API key directamente en la interfaz.

**Pros**:
- ✅ No requiere archivos
- ✅ Rápido para probar

**Contras**:
- ⚠️ Solo dura durante la sesión
- ⚠️ Debes ingresarla cada vez que inicies la app

---

## 🆘 Troubleshooting

### "La app sigue usando la API key del sistema"

**Problema**: Tienes `OPENAI_API_KEY` en tu environment del sistema y `.env` al mismo tiempo.

**Solución**:
```bash
# 1. Verifica cuál está usando:
echo $OPENAI_API_KEY  # Ver la del sistema

# 2. Elimínala del sistema (.bashrc/.zshrc)
# Edita ~/.zshrc y comenta/elimina la línea export OPENAI_API_KEY=...

# 3. Recarga el shell
source ~/.zshrc

# 4. Verifica que ya no existe
echo $OPENAI_API_KEY  # Debe estar vacío

# 5. Reinicia la app
streamlit run app.py
```

---

### "La app no encuentra mi .env"

**Problema**: El archivo `.env` no está en la ubicación correcta.

**Solución**:
```bash
# Verifica que .env esté en la raíz del proyecto:
ls -la .env

# Debe estar al mismo nivel que app.py:
cv_analyzer/
├── .env          ← Aquí
├── app.py
├── requirements.txt
└── ...

# Si no existe, créalo:
cp .env.example .env
```

---

### "Error: No module named 'dotenv'"

**Problema**: Falta instalar `python-dotenv`.

**Solución**:
```bash
pip install python-dotenv

# O reinstalar todas las dependencias:
pip install -r requirements.txt
```

---

### "La app me pide la API key en la UI aunque la definí"

**Posibles causas**:

1. **La key está comentada en .env**:
   ```bash
   # Mal:
   # OPENAI_API_KEY=sk-...  ← Está comentada

   # Bien:
   OPENAI_API_KEY=sk-...  ← Sin #
   ```

2. **Espacio extra o error de sintaxis**:
   ```bash
   # Mal:
   OPENAI_API_KEY = sk-...  ← Espacios alrededor del =

   # Bien:
   OPENAI_API_KEY=sk-...  ← Sin espacios
   ```

3. **Archivo en la ubicación incorrecta**: Ver solución arriba

---

## 📚 Recursos Adicionales

### Obtener API Keys

- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)
- **Google Gemini**: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) ⭐ **Gratis con límites generosos**

### Comparación de Costos (aproximado)

| Proveedor | Modelo | Precio (1M tokens) | Velocidad | Calidad |
|-----------|--------|-------------------|-----------|---------|
| Google Gemini | gemini-1.5-flash-8b | ~$0.04 | ⚡⚡⚡ | ⭐⭐⭐ |
| Google Gemini | gemini-1.5-flash | ~$0.075 | ⚡⚡ | ⭐⭐⭐⭐ |
| OpenAI | gpt-4.1-nano | ~$0.10 | ⚡⚡⚡ | ⭐⭐⭐ |
| OpenAI | gpt-4o-mini | ~$0.15 | ⚡⚡ | ⭐⭐⭐⭐ |
| OpenAI | gpt-4.1-mini | ~$0.20 | ⚡⚡ | ⭐⭐⭐⭐ |
| Google Gemini | gemini-1.5-pro | ~$1.25 | ⚡ | ⭐⭐⭐⭐⭐ |
| OpenAI | gpt-4.1 | ~$2.00 | ⚡⚡ | ⭐⭐⭐⭐⭐ |
| OpenAI | gpt-4o | ~$2.50 | ⚡ | ⭐⭐⭐⭐⭐ |

💡 **Recomendación**: Para análisis de CVs, **Gemini 1.5 Flash** o **GPT-4.1-nano/mini** ofrecen excelente relación calidad/precio.

### Documentación

- [Documentación de python-dotenv](https://github.com/theskumar/python-dotenv)
- [Best practices para API keys](https://cloud.google.com/docs/authentication/api-keys)

---

## ✅ Checklist de Configuración

- [ ] Archivo `.env` creado en la raíz del proyecto
- [ ] API key agregada sin comentarios (#)
- [ ] Sin espacios alrededor del `=`
- [ ] `.env` está en `.gitignore`
- [ ] Variables de entorno del sistema eliminadas (si existían)
- [ ] App reiniciada después de crear `.env`
- [ ] `python-dotenv` instalado (`pip install -r requirements.txt`)

---

**¿Problemas?** Revisa el archivo `.env.example` para ver el formato correcto.
