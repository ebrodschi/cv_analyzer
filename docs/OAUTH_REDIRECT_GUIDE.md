# 🚀 OAuth con Redirect - Guía Completa

## ⭐ El Modo Recomendado para la Mejor UX

El modo **OAuth con Redirect** (`oauth_redirect`) es la forma más profesional y user-friendly de autenticar usuarios con Google Drive en Streamlit Cloud.

---

## 🎯 Por Qué Usar OAuth con Redirect

### Ventajas vs Otros Modos

| Característica | oauth_redirect | oauth_streamlit | public | service |
|----------------|----------------|-----------------|--------|---------|
| **UX (experiencia de usuario)** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **Carpetas privadas** | ✅ | ✅ | ❌ | ✅ |
| **Sin copiar códigos** | ✅ | ❌ | ✅ | ✅ |
| **Streamlit Cloud** | ✅ | ✅ | ✅ | ✅ |
| **Seguridad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Facilidad setup** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

### Flujo del Usuario (UX)

```
1. Usuario hace clic en "Conectar con Google Drive" 🔘
2. Es redirigido a Google (en la misma ventana) 🔄
3. Autoriza la aplicación en Google ✅
4. Google lo redirige de vuelta a tu app 🔙
5. ¡Listo! Está autenticado 🎉
```

**Total de clics**: 2-3 clicks
**Tiempo**: 10-15 segundos

---

## 🛠️ Setup Paso a Paso

### Paso 1: Crear OAuth Client ID en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)

2. Selecciona o crea un proyecto:
   - Nombre sugerido: `cv-analyzer-oauth`

3. Habilita Google Drive API:
   - Menú → APIs y servicios → Biblioteca
   - Busca "Google Drive API"
   - Haz clic en "Habilitar"

4. Configura pantalla de consentimiento (solo la primera vez):
   - Menú → APIs y servicios → Pantalla de consentimiento de OAuth
   - Tipo de usuario: **Externo** (si es para uso público)
   - Nombre de la aplicación: `CV Analyzer`
   - Correo electrónico de asistencia: tu email
   - Ámbitos: Agregar `https://www.googleapis.com/auth/drive.readonly`
   - Usuarios de prueba: Agrega los emails que probarán (solo si es "Externo")
   - Guardar y continuar

5. Crea credenciales OAuth 2.0:
   - Menú → APIs y servicios → Credenciales
   - "+ CREAR CREDENCIALES"
   - Selecciona "ID de cliente de OAuth 2.0"

6. **IMPORTANTE**: Configura como "Aplicación web":
   - Tipo de aplicación: **Aplicación web** (NO "Aplicación de escritorio")
   - Nombre: `CV Analyzer Web Client`

7. **CRÍTICO**: Agrega URIs de redirect autorizadas:

   **Para Streamlit Cloud:**
   ```
   https://tu-app.streamlit.app/
   ```
   ⚠️ **Importante**: Incluye la barra final `/`

   **Para desarrollo local:**
   ```
   http://localhost:8501/
   ```

   Puedes agregar ambas para que funcione en local y cloud.

8. Haz clic en "Crear"

9. **Descarga las credenciales**:
   - Se abrirá un modal con tu Client ID y Client Secret
   - Opción A: Descarga el archivo JSON
   - Opción B: Copia el Client ID y Secret manualmente

---

### Paso 2: Configurar Credenciales en tu App

Tienes dos opciones:

#### Opción A: Archivo credentials.json (Recomendado para local)

1. Descarga el archivo JSON de Google Cloud Console

2. **IMPORTANTE**: El archivo debe tener estructura de tipo "web":
   ```json
   {
     "web": {
       "client_id": "123456789-abc.apps.googleusercontent.com",
       "project_id": "tu-project",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "GOCSPX-abc123...",
       "redirect_uris": ["http://localhost:8501/"]
     }
   }
   ```

   ⚠️ **Nota**: Si descargaste para "Aplicación de escritorio", tendrá `"installed"` en lugar de `"web"`. Necesitas cambiarlo a `"web"` o recrear las credenciales como "Aplicación web".

3. Guarda el archivo como `credentials.json` en la raíz del proyecto:
   ```
   cv_analyzer/
   ├── credentials.json  ← Aquí
   ├── app.py
   ├── .env
   └── ...
   ```

4. Agrega a `.gitignore` (ya debería estar):
   ```
   credentials.json
   ```

#### Opción B: Variables de Entorno (Recomendado para Streamlit Cloud)

En `.env`:
```bash
DRIVE_AUTH_MODE=oauth_redirect
GOOGLE_OAUTH_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abc123...
```

En **Streamlit Cloud** (Settings → Secrets):
```toml
DRIVE_AUTH_MODE = "oauth_redirect"
GOOGLE_OAUTH_CLIENT_ID = "123456789-abc.apps.googleusercontent.com"
GOOGLE_OAUTH_CLIENT_SECRET = "GOCSPX-abc123..."
```

---

### Paso 3: Configurar Redirect URI

#### Para Streamlit Cloud

La variable `STREAMLIT_SERVER_BASE_URL` se configura automáticamente en Streamlit Cloud con la URL de tu app (ej: `https://tu-app.streamlit.app`).

**No necesitas hacer nada adicional** si tu app ya está deployada.

#### Para Desarrollo Local

El código detecta automáticamente si está corriendo localmente y usa `http://localhost:8501`.

Asegúrate de agregar `http://localhost:8501/` en las URIs autorizadas en Google Cloud Console.

---

### Paso 4: Probar la Autenticación

1. Ejecuta tu app:
   ```bash
   streamlit run app.py
   ```

2. En la sidebar, selecciona:
   - Modo de autenticación: **oauth_redirect**

3. Haz clic en "🔑 Conectar con Google Drive"

4. Serás redirigido a Google (puede ser en la misma pestaña o nueva)

5. Inicia sesión y autoriza:
   - Revisa los permisos (solo lectura de Drive)
   - Haz clic en "Permitir"

6. Google te redirige de vuelta a tu app

7. ✅ ¡Autenticado! Verás "Ya estás autenticado con Google Drive"

---

## 🔒 Seguridad y Buenas Prácticas

### Seguridad Implementada

✅ **State Token (CSRF Protection)**
- Se genera un token único por sesión
- Se valida al recibir el redirect
- Previene ataques CSRF

✅ **PKCE (Proof Key for Code Exchange)** - Opcional
- Código preparado en `generate_pkce_pair()`
- Añade capa extra de seguridad
- Recomendado para apps públicas

✅ **Access + Refresh Tokens**
- Access token para llamadas API
- Refresh token para renovar sesión
- Configurado con `access_type='offline'`

✅ **Scopes Mínimos**
- Solo `drive.readonly`
- Principio de menor privilegio

### Mejores Prácticas

#### ✅ DO - Hacer

- ✅ Usa HTTPS en producción (Streamlit Cloud lo hace automáticamente)
- ✅ Agrega solo las URIs necesarias en Google Cloud
- ✅ Mantén `client_secret` en secrets (no en código)
- ✅ Agrega `credentials.json` a `.gitignore`
- ✅ Revisa y actualiza scopes solo cuando sea necesario
- ✅ Implementa logout (botón "Cerrar sesión")

#### ❌ DON'T - No Hacer

- ❌ No commits `credentials.json` al repositorio
- ❌ No uses redirect HTTP en producción
- ❌ No pidas más scopes de los necesarios
- ❌ No compartas tu `client_secret` públicamente
- ❌ No uses wildcards en redirect URIs

---

## 🐛 Troubleshooting

### Error: "redirect_uri_mismatch"

**Problema**: La URI de redirect no coincide con las configuradas en Google Cloud Console.

**Solución**:
1. Verifica la URL exacta en el error (Google te la muestra)
2. Ve a Google Cloud Console → Credenciales → Tu OAuth Client
3. En "URIs de redireccionamiento autorizados", agrega **exactamente** la URL del error
4. Guarda y espera 5 minutos (propagación de cambios)
5. Intenta de nuevo

**Ejemplo**:
- ❌ Mal: `https://tu-app.streamlit.app`
- ✅ Bien: `https://tu-app.streamlit.app/`
- ⚠️ **La barra final `/` importa!**

---

### Error: "invalid_client"

**Problema**: Client ID o Client Secret incorrectos.

**Solución**:
1. Verifica que copiaste bien el Client ID y Secret
2. Asegúrate de que no haya espacios extra
3. En Streamlit Cloud, verifica que estén en Secrets
4. Re-descarga las credenciales si es necesario

---

### Error: "access_denied"

**Problema**: El usuario no autorizó la aplicación.

**Solución**:
- Normal: El usuario puede cancelar la autorización
- Si el usuario SÍ autorizó pero sale este error:
  1. Verifica que el email esté en "Usuarios de prueba" (si app no está publicada)
  2. Publica la app en Google Cloud Console (si es para uso público)

---

### No se muestra el botón de autenticación

**Problema**: No aparece el botón "Conectar con Google Drive".

**Solución**:
1. Verifica que seleccionaste `oauth_redirect` en el dropdown
2. Revisa la consola de Python para errores
3. Verifica que `credentials.json` existe O que las variables de entorno estén configuradas

---

### Redirect infinito / Loop

**Problema**: Después de autorizar, la app vuelve a pedir autorización.

**Solución**:
1. Limpia cookies y cache del navegador
2. Verifica que `st.session_state.google_oauth_creds` se esté guardando
3. Revisa la consola para errores al intercambiar el código
4. Asegúrate de que el state token coincide

---

### Error en Streamlit Cloud: "STREAMLIT_SERVER_BASE_URL not found"

**Problema**: La variable de entorno no está disponible.

**Solución**:
- Streamlit Cloud configura esto automáticamente
- Si no está, puedes configurarla manualmente en Secrets:
  ```toml
  STREAMLIT_SERVER_BASE_URL = "https://tu-app.streamlit.app"
  ```

---

## 📊 Comparación con Otros Métodos

### vs. OAuth con Popup (JavaScript)

| Aspecto | OAuth Redirect | OAuth Popup |
|---------|----------------|-------------|
| **Streamlit nativo** | ✅ Sí | ❌ No (requiere componente custom) |
| **Complejidad** | ⭐⭐⭐ Media | ⭐⭐⭐⭐⭐ Muy alta |
| **UX móvil** | ⭐⭐⭐⭐⭐ | ⭐⭐ (popups bloqueados) |
| **Mantenimiento** | ⭐⭐⭐⭐⭐ Fácil | ⭐⭐ Complejo |

**Conclusión**: OAuth con redirect es mejor para Streamlit.

### vs. OAuth Manual (copiar código)

| Aspecto | OAuth Redirect | OAuth Manual |
|---------|----------------|--------------|
| **Clics del usuario** | 2-3 | 4-5 |
| **Pasos manuales** | 0 | 2 (copiar/pegar) |
| **Riesgo de error** | Bajo | Medio |
| **UX** | ⭐⭐⭐⭐⭐ | ⭐⭐ |

**Conclusión**: OAuth redirect es mucho mejor UX.

---

## 🎓 Cómo Funciona (Técnico)

### Flujo Completo

```
1. Usuario → Clic en "Conectar"
   ↓
2. App genera:
   - State token (anti-CSRF)
   - Authorization URL
   - Guarda flow en session_state
   ↓
3. Redirect → Google OAuth
   URL: https://accounts.google.com/o/oauth2/auth?
        client_id=...&
        redirect_uri=https://tu-app.streamlit.app/&
        response_type=code&
        scope=drive.readonly&
        state=abc123...&
        access_type=offline
   ↓
4. Usuario autoriza en Google
   ↓
5. Google → Redirect de vuelta
   URL: https://tu-app.streamlit.app/?code=xyz789&state=abc123
   ↓
6. App detecta query params (handle_oauth_redirect)
   ↓
7. Valida state token
   ↓
8. Intercambia 'code' por tokens:
   POST https://oauth2.googleapis.com/token
   Body: {
     code: xyz789,
     client_id: ...,
     client_secret: ...,
     redirect_uri: ...,
     grant_type: authorization_code
   }
   ↓
9. Google devuelve tokens:
   {
     access_token: "ya29...",
     refresh_token: "1//...",
     expires_in: 3600,
     scope: "drive.readonly",
     token_type: "Bearer"
   }
   ↓
10. App guarda en session_state
    ↓
11. Limpia query params
    ↓
12. ✅ Usuario autenticado!
```

### Código Clave

```python
# 1. Generar URL de autorización
auth_url, flow, state = get_authorization_url_with_redirect(
    redirect_uri="https://tu-app.streamlit.app/",
    state=None  # Se genera automáticamente
)

# 2. Guardar en session state
st.session_state.oauth_flow = flow
st.session_state.oauth_state = state

# 3. Redirigir usuario (con link HTML)
st.markdown(f'<a href="{auth_url}">Autorizar</a>', unsafe_allow_html=True)

# 4. Al volver, detectar query params
if "code" in st.query_params:
    code = st.query_params["code"]
    state = st.query_params["state"]

    # 5. Validar state
    if state == st.session_state.oauth_state:
        # 6. Intercambiar código por tokens
        creds = exchange_code_for_tokens(flow, authorization_response)

        # 7. Guardar credenciales
        st.session_state.google_oauth_creds = {...}
```

---

## 📞 Soporte

### Recursos

- **Documentación Google OAuth**: https://developers.google.com/identity/protocols/oauth2
- **Streamlit Query Params**: https://docs.streamlit.io/library/api-reference/utilities/st.query_params
- **Google Drive API**: https://developers.google.com/drive/api/guides/about-sdk

### Issues Comunes

Si encuentras un problema no listado aquí:
1. Revisa la consola de Python para errores detallados
2. Verifica la consola del navegador (F12)
3. Comprueba los logs de Google Cloud Console
4. Abre un issue en GitHub con:
   - Descripción del problema
   - Mensajes de error
   - Pasos para reproducir

---

## ✅ Checklist de Implementación

- [ ] OAuth Client ID creado como "Aplicación web"
- [ ] Google Drive API habilitada
- [ ] URIs de redirect agregadas en Google Cloud Console
- [ ] Credenciales configuradas (`credentials.json` o variables de entorno)
- [ ] `DRIVE_AUTH_MODE=oauth_redirect` configurado
- [ ] Probado en desarrollo local
- [ ] Probado en Streamlit Cloud
- [ ] Botón de logout funciona
- [ ] Manejo de errores implementado

---

## 🎉 ¡Todo Listo!

Ahora tienes **la mejor experiencia de autenticación** para tus usuarios en Streamlit Cloud.

**Próximos pasos**:
1. Prueba el flujo completo
2. Configura para producción en Streamlit Cloud
3. Monitorea los logs para detectar problemas
4. ¡Disfruta de la mejor UX! 🚀

---

*¿Preguntas? Abre un issue en GitHub o consulta la documentación oficial de Google.*
