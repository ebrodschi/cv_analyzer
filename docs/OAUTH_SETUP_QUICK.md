# 🚀 Setup Rápido - Google Drive OAuth

## Para Desarrollo Local (5 minutos)

### Paso 1: Obtén credentials.json

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Navegación: **APIs y servicios** → **Credenciales**
3. Encuentra tu OAuth 2.0 Client ID (o créalo si no existe)
4. Haz clic en el **ícono de descarga** (⬇️) a la derecha
5. Se descargará un archivo JSON

### Paso 2: Configura el proyecto

```bash
# 1. Renombra el archivo descargado (si es necesario)
mv ~/Downloads/client_secret_*.json credentials.json

# 2. Muévelo a la raíz de tu proyecto
mv credentials.json /ruta/a/cv_analyzer/

# 3. Verifica que esté en .gitignore
cat .gitignore | grep credentials.json
# Debería aparecer "credentials.json"
```

### Paso 3: Configura .env

```bash
# Copia el template
cp .env.local.example .env

# Edita .env y agrega tu API key de OpenAI
# OPENAI_API_KEY=sk-tu-api-key

# Para Google Drive, solo necesitas:
DRIVE_AUTH_MODE=oauth_redirect
# ¡Eso es todo! No necesitas GOOGLE_OAUTH_CLIENT_ID ni SECRET
```

### Paso 4: Ejecuta la app

```bash
streamlit run app.py
```

### Paso 5: Prueba OAuth

1. En la sidebar, selecciona: **oauth_redirect**
2. Clic en "🔑 Conectar con Google Drive"
3. Serás redirigido a Google
4. Autoriza la aplicación
5. ¡Listo! Volverás autenticado

---

## Para Streamlit Cloud (3 minutos)

### Paso 1: Obtén Client ID y Secret

**Opción A - Desde archivo JSON:**
```bash
# Si ya tienes credentials.json, ábrelo y copia:
cat credentials.json
# Busca: "client_id" y "client_secret"
```

**Opción B - Desde Google Cloud Console:**
1. Google Cloud Console → Credenciales
2. Clic en tu OAuth Client ID
3. Copia **Client ID** y **Client secret**

### Paso 2: Configura Secrets en Streamlit

1. Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
2. Menú (⚙️) → **Settings** → **Secrets**
3. Agrega:

```toml
# LLM API Key
OPENAI_API_KEY = "sk-tu-api-key"

# Google Drive OAuth
DRIVE_AUTH_MODE = "oauth_redirect"
GOOGLE_OAUTH_CLIENT_ID = "123456789-abc.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET = "GOCSPX-abc123def456"
```

### Paso 3: Configura Redirect URI

1. Google Cloud Console → Credenciales
2. Clic en tu OAuth Client ID
3. En **URIs de redireccionamiento autorizados**, agrega:
   ```
   https://tu-app.streamlit.app/
   ```
   ⚠️ **Importante**: Incluye la barra final `/`

4. Guarda los cambios

### Paso 4: Deploy y prueba

1. Haz push de tu código a GitHub
2. Streamlit Cloud detectará los cambios y redesplegará
3. Prueba el flujo OAuth en tu app deployada

---

## ❓ FAQ

### ¿Necesito ambos credentials.json Y las variables de entorno?

**NO**. Solo necesitas UNO:

- **Local**: `credentials.json` (más fácil)
- **Streamlit Cloud**: Variables en Secrets (más seguro)

### ¿Qué pasa si tengo ambos?

El código da **prioridad a `credentials.json`**:

```python
if os.path.exists("credentials.json"):
    # Usa credentials.json
else:
    # Usa variables de entorno
```

### ¿Debo subir credentials.json a GitHub?

**¡NO! ❌**

Verifica que esté en `.gitignore`:

```bash
# .gitignore
credentials.json
token.json
*.json
```

### ¿Qué formato debe tener credentials.json?

Para OAuth con redirect, debe ser tipo **"web"**:

```json
{
  "web": {
    "client_id": "123456789-abc.apps.googleusercontent.com",
    "project_id": "tu-proyecto",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "GOCSPX-abc123",
    "redirect_uris": ["http://localhost:8501/"]
  }
}
```

❌ **NO** debe tener `"installed"` (eso es para apps de escritorio)

### ¿Cómo sé si está funcionando?

Al ejecutar la app, verás en la terminal:

```bash
# Si encuentra credentials.json:
✅ No hay mensajes de error

# Si NO encuentra credenciales:
❌ ValueError: No se encontró credentials.json ni variables de entorno...
```

### ¿Puedo usar diferentes credenciales en local vs cloud?

**Sí**, esa es la configuración recomendada:

- **Local**: `credentials.json` con `http://localhost:8501/`
- **Cloud**: Secrets con `https://tu-app.streamlit.app/`

Puedes crear **dos OAuth Clients diferentes** en Google Cloud Console si quieres.

---

## 🔧 Troubleshooting

### Error: "No se encontró credentials.json ni variables de entorno"

**Solución**: Necesitas configurar credenciales. Elige una opción:

1. Descarga `credentials.json` y colócalo en la raíz
2. O configura `GOOGLE_OAUTH_CLIENT_ID` y `SECRET` en `.env`

### Error: "redirect_uri_mismatch"

**Solución**: La URI de redirect no coincide.

1. Verifica en el error la URI que la app está usando
2. Agrégala en Google Cloud Console → Credenciales
3. Espera 5 minutos y vuelve a intentar

### credentials.json existe pero sigue sin funcionar

**Verifica que esté en la raíz del proyecto**:

```bash
# Desde la raíz del proyecto:
ls -la | grep credentials.json
# Debería aparecer

# Verifica el contenido:
cat credentials.json | head -5
# Debe empezar con {"web": { o {"installed": {
```

### ¿Cómo cambio de credentials.json a variables de entorno?

```bash
# 1. Renombra o elimina credentials.json
mv credentials.json credentials.json.backup

# 2. Configura variables en .env
echo 'GOOGLE_OAUTH_CLIENT_ID=tu-client-id' >> .env
echo 'GOOGLE_OAUTH_CLIENT_SECRET=tu-secret' >> .env

# 3. Reinicia la app
```

---

## ✅ Checklist de Verificación

### Para Local:

- [ ] `credentials.json` existe en la raíz
- [ ] `credentials.json` tiene estructura `{"web": {...}}`
- [ ] `credentials.json` está en `.gitignore`
- [ ] `DRIVE_AUTH_MODE=oauth_redirect` en `.env`
- [ ] `OPENAI_API_KEY` configurado en `.env`

### Para Streamlit Cloud:

- [ ] `GOOGLE_OAUTH_CLIENT_ID` en Secrets
- [ ] `GOOGLE_OAUTH_CLIENT_SECRET` en Secrets
- [ ] `DRIVE_AUTH_MODE=oauth_redirect` en Secrets
- [ ] Redirect URI agregada en Google Cloud Console
- [ ] Redirect URI incluye la barra final `/`
- [ ] `credentials.json` NO está en el repositorio

---

## 🎉 ¡Todo Configurado!

Ahora deberías poder autenticarte con Google Drive sin problemas.

**Siguiente paso**: Prueba el flujo completo en la app.

---

*¿Problemas? Revisa la [documentación completa](./OAUTH_REDIRECT_GUIDE.md) o abre un issue.*
