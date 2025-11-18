# 🔐 Guía Simplificada de Autenticación con Google Drive

Esta aplicación ahora tiene **solo 2 modos de autenticación** simples y claros:

---

## 📊 Comparación Rápida

| Característica | **api_key** | **oauth** |
|----------------|-------------|-----------|
| **Carpetas públicas** | ✅ Sí | ✅ Sí |
| **Carpetas privadas** | ❌ No | ✅ Sí |
| **Configuración** | ⭐ Fácil | ⭐⭐ Moderada |
| **API Key requerida** | ✅ Sí | ❌ No |
| **OAuth Client ID requerido** | ❌ No | ✅ Sí |
| **Ingreso por UI** | ✅ Sí | ❌ No (redirect) |
| **Mejor para** | Carpetas públicas | Carpetas privadas |

---

## 1️⃣ Modo API_KEY - Para Carpetas Públicas

### ✨ Características
- ✅ **Más simple**: Solo necesitas una API key
- ✅ **Ingreso por UI**: Ingresas tu API key directamente en la interfaz
- ✅ **Sin OAuth**: No requiere flujo de autenticación complejo
- ⚠️ **Limitación**: Solo funciona con carpetas **públicas**

### 📝 Pasos para configurar

#### 1. Crear API Key de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea o selecciona un proyecto
3. Habilita **Google Drive API**:
   - Menú → "APIs y servicios" → "Biblioteca"
   - Busca "Google Drive API" → Habilitar
4. Crea una API Key:
   - Menú → "APIs y servicios" → "Credenciales"
   - Clic en **"+ CREAR CREDENCIALES"** → **"Clave de API"**
   - **Copia la clave** (ejemplo: `AIzaSyC1234567890abcdefghijklmnopqrs`)
5. (Opcional) Restringe la API key:
   - Clic en la API key creada
   - "Restricciones de API" → Seleccionar: **Google Drive API**
   - Guardar

#### 2. Hacer pública tu carpeta de Drive

1. Abre Google Drive en tu navegador
2. Encuentra la carpeta con los CVs
3. Clic derecho → **"Compartir"** o **"Obtener enlace"**
4. En **"Acceso general"**, cambia a:
   - **"Cualquiera con el enlace"**
   - Rol: **"Lector"**
5. Copia el enlace
6. El ID de la carpeta está en la URL:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                          ↑ Este es el ID
   ```

#### 3. Usar en la aplicación

1. Abre la app de Streamlit
2. Sidebar → "Modo de autenticación" → **api_key**
3. Ingresa tu **API key** en el campo que aparece
4. Ingresa el **ID de la carpeta** (solo el ID, no la URL completa)
5. Clic en **"🔍 Listar Archivos de Drive"**

✅ ¡Listo! Verás los archivos de la carpeta pública.

---

## 2️⃣ Modo OAUTH - Para Carpetas Privadas

### ✨ Características
- ✅ **Carpetas privadas**: Accede a tus carpetas personales sin hacerlas públicas
- ✅ **Usa tu sesión de Chrome**: Aprovecha la sesión de Google ya abierta en tu navegador
- ✅ **Seguro**: Autorización directa con Google
- ✅ **Persistente**: La sesión se mantiene mientras uses la app

### 📝 Pasos para configurar

#### 1. Crear OAuth Client ID

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita **Google Drive API** (si no lo hiciste antes)
3. Configura la **pantalla de consentimiento OAuth** (si es primera vez):
   - Menú → "APIs y servicios" → "Pantalla de consentimiento de OAuth"
   - Tipo de usuario: **Externo** (para uso personal) o **Interno** (para organización)
   - Nombre de la app: `CV Analyzer`
   - Email de asistencia: tu email
   - Ámbitos: Agregar `https://www.googleapis.com/auth/drive.readonly`
   - Usuarios de prueba: Agrega tu email (si es Externo)

4. Crea el **OAuth Client ID**:
   - Menú → "APIs y servicios" → "Credenciales"
   - **"+ CREAR CREDENCIALES"** → **"ID de cliente de OAuth 2.0"**
   - Tipo de aplicación: **Aplicación web** (¡no "escritorio"!)
   - Nombre: `CV Analyzer Web`

5. **URIs de redireccionamiento autorizados** (¡importante!):
   - Para desarrollo local: `http://localhost:8501/`
   - Para Streamlit Cloud: `https://tu-app.streamlit.app/`

6. Clic en **"Crear"**

#### 2. Descargar o copiar credenciales

**Opción A: Archivo credentials.json** (recomendado para local)
1. Descarga el archivo JSON
2. Guárdalo como `credentials.json` en la raíz de tu proyecto:
   ```
   cv_analyzer/
   ├── credentials.json  ← Aquí
   ├── app.py
   └── ...
   ```

**Opción B: Variables de entorno** (para Streamlit Cloud)
1. Copia el **Client ID** y **Client Secret**
2. En tu archivo `.env`:
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=123456789-abc.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abc123def456
   ```
3. O en Streamlit Cloud (Settings → Secrets):
   ```toml
   GOOGLE_OAUTH_CLIENT_ID = "123456789-abc.apps.googleusercontent.com"
   GOOGLE_OAUTH_CLIENT_SECRET = "GOCSPX-abc123def456"
   ```

#### 3. Usar en la aplicación

1. Abre la app de Streamlit
2. Sidebar → "Modo de autenticación" → **oauth**
3. Clic en **"🔑 Conectar con Google Drive"**
4. Clic en el botón azul **"🔐 Autorizar con Google"**
5. Serás redirigido a Google (usa tu sesión activa del navegador)
6. Autoriza la aplicación
7. Volverás automáticamente a la app
8. Ingresa el **ID de la carpeta** (puede ser pública o privada)
9. Clic en **"🔍 Listar Archivos de Drive"**

✅ ¡Autenticado! Ahora puedes acceder a carpetas privadas.

---

## 🆘 Troubleshooting

### Error: "API key no encontrada" (modo api_key)

**Solución**:
- Verifica que ingresaste correctamente la API key
- Confirma que la API key tenga Google Drive API habilitada
- Asegúrate de no tener espacios al inicio o final de la key

---

### Error: "No se puede acceder a la carpeta" (modo api_key)

**Soluciones**:
1. Verifica que la carpeta sea **pública** ("Cualquiera con el enlace")
2. Confirma que el ID de la carpeta sea correcto
3. Verifica que Google Drive API esté habilitada en tu proyecto de Google Cloud

---

### Error: "No se pudo obtener credenciales OAuth" (modo oauth)

**Soluciones**:
1. Verifica que `credentials.json` esté en la raíz del proyecto
2. O que las variables `GOOGLE_OAUTH_CLIENT_ID` y `GOOGLE_OAUTH_CLIENT_SECRET` estén configuradas
3. Confirma que el Client ID sea tipo **"Aplicación web"** (no "escritorio")
4. Asegúrate de haber agregado las URIs de redirect correctas

---

### Error: "redirect_uri_mismatch" (modo oauth)

**Problema**: La URI de redirect no coincide con las configuradas en Google Cloud.

**Solución**:
1. Ve a Google Cloud Console → Credenciales
2. Clic en tu OAuth Client ID
3. En **"URIs de redireccionamiento autorizados"**, verifica que esté:
   - Para local: `http://localhost:8501/` (con la barra `/` al final)
   - Para Streamlit Cloud: tu URL exacta con `/` al final
4. Guarda y espera 5 minutos para que los cambios se propaguen

---

### Error: "Access blocked: This app isn't verified" (modo oauth)

**Problema**: La app no está verificada por Google.

**Solución para uso personal**:
1. En la pantalla de error, busca "Advanced" o "Configuración avanzada"
2. Clic en "Go to [App Name] (unsafe)" o similar
3. Autoriza la aplicación

**Solución permanente**:
1. Google Cloud Console → Pantalla de consentimiento de OAuth
2. Agrega tu email en "Usuarios de prueba"
3. O completa el proceso de verificación de Google (para apps públicas)

---

## 💡 ¿Cuál modo usar?

### Usa **api_key** si:
- ✅ Tus carpetas de Drive son públicas o las puedes hacer públicas
- ✅ Quieres la configuración más simple
- ✅ Solo necesitas leer archivos (no escribir)
- ✅ No te importa que cualquiera con el enlace pueda ver la carpeta

### Usa **oauth** si:
- ✅ Tus carpetas son privadas y deben permanecer privadas
- ✅ Quieres acceso completo a tu Drive con tu cuenta personal
- ✅ No quieres hacer públicas tus carpetas
- ✅ Estás dispuesto a configurar OAuth (15 minutos una sola vez)

---

## 📚 Recursos Adicionales

- [Google Cloud Console](https://console.cloud.google.com/)
- [Documentación de Google Drive API](https://developers.google.com/drive/api/guides/about-sdk)
- [Guía OAuth 2.0 de Google](https://developers.google.com/identity/protocols/oauth2)
- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**¿Preguntas?** Abre un issue en el repositorio del proyecto.
