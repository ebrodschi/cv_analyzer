# 🌟 User OAuth Mode - Autenticación Sin Credenciales del Desarrollador

## 🎯 ¿Qué es esto?

**User OAuth Mode** (`user_oauth`) permite que **el usuario final se autentique con SU propia cuenta de Google**, sin que tú (el desarrollador) necesites configurar OAuth Client Secrets ni `credentials.json`.

---

## ✨ Ventajas

| Característica | user_oauth | oauth_redirect | public |
|----------------|------------|----------------|--------|
| **Sin credenciales del dev** | ✅ | ❌ | ✅ |
| **Carpetas privadas** | ✅ | ✅ | ❌ |
| **Picker visual** | ✅ | ❌ | ❌ |
| **Usuario controla acceso** | ✅ | ⚠️ | ❌ |
| **Sin Client Secret** | ✅ | ❌ | ✅ |
| **Configuración** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |

---

## 🛠️ Setup (5 minutos)

### Paso 1: Habilitar APIs en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea o selecciona un proyecto
3. Habilita estas APIs:
   - **Google Drive API**
   - **Google Picker API**

### Paso 2: Crear API Key

1. Menú → APIs y servicios → Credenciales
2. "+ CREAR CREDENCIALES" → "Clave de API"
3. **Opcional**: Restringir la clave:
   - Restricciones de API → Seleccionar APIs
   - Marcar: Google Drive API y Google Picker API
4. Copiar la API key

### Paso 3: Crear OAuth Client ID (Solo ID, Sin Secret)

1. Menú → APIs y servicios → Credenciales
2. "+ CREAR CREDENCIALES" → "ID de cliente de OAuth 2.0"
3. Configurar pantalla de consentimiento (si es primera vez):
   - Tipo: **Externo**
   - Nombre: `CV Analyzer`
   - Scopes: Agregar `https://www.googleapis.com/auth/drive.readonly`
4. Tipo de aplicación: **Aplicación web**
5. **IMPORTANTE**: En "Orígenes JavaScript autorizados":
   - Para local: `http://localhost:8501`
   - Para Streamlit Cloud: `https://tu-app.streamlit.app`
6. **NO agregues** "URIs de redireccionamiento autorizados"
7. Crear y copiar el **Client ID** (solo el ID, no necesitas el Secret)

### Paso 4: Configurar en tu App

**En `.env`:**
```bash
DRIVE_AUTH_MODE=user_oauth
GOOGLE_API_KEY=AIzaSy...
GOOGLE_OAUTH_CLIENT_ID_PUBLIC=123456789-abc.apps.googleusercontent.com
```

**En Streamlit Cloud (Secrets):**
```toml
DRIVE_AUTH_MODE = "user_oauth"
GOOGLE_API_KEY = "AIzaSy..."
GOOGLE_OAUTH_CLIENT_ID_PUBLIC = "123456789-abc.apps.googleusercontent.com"
```

⚠️ **Nota**: Usamos `GOOGLE_OAUTH_CLIENT_ID_PUBLIC` (diferente variable) para distinguirlo del Client ID que requiere Secret.

---

## 🚀 Cómo Funciona (UX del Usuario)

### Flujo Completo:

```
1. Usuario abre la app
   ↓
2. Selecciona "user_oauth" en modo de autenticación
   ↓
3. Ve un botón: "Autorizar con Google"
   ↓
4. Hace clic → Se abre diálogo de Google (inline, sin redirect)
   ↓
5. Se autentica con SU cuenta de Google
   (usa la sesión ya logueada del navegador)
   ↓
6. Autoriza el acceso a Drive (solo lectura)
   ↓
7. Se abre el Google Picker (selector visual de Google)
   ↓
8. Selecciona la carpeta que quiere compartir
   ↓
9. ✅ ¡Listo! La app tiene acceso a esa carpeta
```

**Tiempo total**: ~20-30 segundos
**Clics**: 3-4 clicks
**Complejidad para el usuario**: ⭐⭐ Fácil

---

## 🔒 Seguridad

### ✅ Por Qué Es Seguro

1. **Token generado en el cliente**: El access token se genera en el navegador del usuario
2. **No pasa por tu servidor**: El token nunca viaja por tu backend
3. **Session-only**: El token solo existe durante la sesión del navegador
4. **Usuario controla**: El usuario ve exactamente qué permisos otorga
5. **Scope mínimo**: Solo `drive.readonly` (solo lectura)
6. **Sin Client Secret**: No hay secreto que proteger

### ⚠️ Consideraciones

- El token expira (típicamente 1 hora)
- No hay refresh token (el usuario debe reautorizarse si expira)
- El token está disponible en JavaScript (client-side)
- Cada sesión requiere nueva autorización

---

## 🆚 Comparación con Otros Modos

### vs. oauth_redirect

| Aspecto | user_oauth | oauth_redirect |
|---------|------------|----------------|
| **Setup del dev** | API Key + Client ID | Client ID + Client Secret + credentials.json |
| **Secret requerido** | ❌ No | ✅ Sí |
| **Redirect URIs** | ❌ No | ✅ Sí (debe configurarse) |
| **Refresh token** | ❌ No | ✅ Sí |
| **Duración sesión** | ~1 hora | Días/semanas |
| **Picker visual** | ✅ Sí | ❌ No |
| **Complejidad** | ⭐⭐ | ⭐⭐⭐⭐ |

**Cuándo usar user_oauth**:
- ✅ Quieres setup simple
- ✅ No quieres manejar Client Secrets
- ✅ Sesiones cortas (< 1 hora)
- ✅ Quieres que el usuario vea un picker visual

**Cuándo usar oauth_redirect**:
- ✅ Necesitas sesiones largas
- ✅ Quieres refresh tokens
- ✅ Control total del flujo OAuth
- ✅ No te importa la complejidad del setup

### vs. public

| Aspecto | user_oauth | public |
|---------|------------|--------|
| **Carpetas privadas** | ✅ Sí | ❌ No |
| **Autenticación** | Usuario autoriza | Sin autenticación |
| **Setup** | API Key + Client ID | Solo API Key |
| **Carpeta debe ser pública** | ❌ No | ✅ Sí |

---

## 📋 Checklist de Implementación

### Google Cloud Console:
- [ ] Proyecto creado
- [ ] Google Drive API habilitada
- [ ] Google Picker API habilitada
- [ ] API Key creada
- [ ] API Key restringida (opcional pero recomendado)
- [ ] OAuth Client ID creado (tipo "Aplicación web")
- [ ] Orígenes JavaScript autorizados configurados
- [ ] Pantalla de consentimiento configurada
- [ ] Scope `drive.readonly` agregado

### En tu Aplicación:
- [ ] `GOOGLE_API_KEY` configurada
- [ ] `GOOGLE_OAUTH_CLIENT_ID_PUBLIC` configurada
- [ ] `DRIVE_AUTH_MODE=user_oauth`
- [ ] Component `google_drive_picker` importado
- [ ] Modo `user_oauth` agregado en dropdown

### Testing:
- [ ] Probado en desarrollo local
- [ ] Origen JavaScript autorizado para localhost
- [ ] Probado en Streamlit Cloud
- [ ] Origen JavaScript autorizado para URL de producción
- [ ] Picker se abre correctamente
- [ ] Carpeta se selecciona correctamente
- [ ] Archivos se listan correctamente

---

## 🐛 Troubleshooting

### Error: "popup_closed_by_user"

**Problema**: El usuario cerró el diálogo sin autorizar.

**Solución**: Normal. El usuario puede volver a hacer clic en "Autorizar".

---

### Error: "idpiframe_initialization_failed"

**Problema**: El origen no está autorizado en Google Cloud Console.

**Solución**:
1. Ve a Google Cloud Console → Credenciales
2. Clic en tu OAuth Client ID
3. En "Orígenes JavaScript autorizados", verifica que esté:
   - Local: `http://localhost:8501`
   - Producción: `https://tu-app.streamlit.app`
4. Guarda y espera 5 minutos

---

### Error: "Access blocked: Authorization Error"

**Problema**: La app no está verificada por Google o falta configuración de consentimiento.

**Solución**:
1. Google Cloud Console → Pantalla de consentimiento de OAuth
2. Verifica que:
   - Scopes estén agregados correctamente
   - App esté en modo "Testing" o "Production"
   - Si está en Testing, tu email esté en "Usuarios de prueba"
3. Para usuarios externos, considera publicar la app (proceso de verificación de Google)

---

### El Picker no se abre

**Problemas posibles**:

1. **APIs no habilitadas**:
   - Verifica que Google Drive API y Picker API estén habilitadas

2. **API Key inválida**:
   - Verifica que la API key sea correcta
   - Verifica que no tenga restricciones que bloqueen las APIs

3. **Bloqueador de popups** (no debería pasar porque no es popup):
   - Verifica la consola del navegador (F12) para errores

---

### Token expirado

**Problema**: Después de ~1 hora, las llamadas a la API fallan.

**Solución**:
- El usuario debe volver a autorizar
- Implementa manejo de errores que detecte token expirado
- Muestra mensaje al usuario pidiendo reautorización

---

## 💡 Mejoras Futuras Opcionales

### 1. Refresh Token Support

Actualmente no implementamos refresh tokens. Para sesiones más largas:

```javascript
// En el tokenClient, agregar:
tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: CLIENT_ID,
    scope: SCOPES,
    callback: (response) => { ... },
    // Esto permitiría refresh
    access_type: 'offline',
    prompt: 'consent'
});
```

Pero requiere manejo server-side del refresh token.

### 2. Almacenamiento Persistente

Guardar el token en `localStorage`:

```javascript
// Al recibir token:
localStorage.setItem('drive_token', accessToken);

// Al cargar:
const savedToken = localStorage.getItem('drive_token');
if (savedToken) {
    accessToken = savedToken;
}
```

⚠️ **Consideración de seguridad**: Tokens en localStorage son vulnerables a XSS.

### 3. Auto-refresh UI

Detectar token expirado y mostrar UI para renovar:

```python
try:
    files = list_files_by_folder(folder_id, service)
except Exception as e:
    if "invalid_grant" in str(e) or "unauthorized" in str(e):
        st.warning("⚠️ Tu sesión expiró. Por favor, vuelve a autorizar.")
        # Mostrar botón de reautorización
```

---

## 🎉 ¡Todo Listo!

Ahora tienes **autenticación client-side** donde el usuario:
- ✅ Se autentica con SU propia cuenta
- ✅ Ve un picker visual de Google
- ✅ Controla qué carpetas comparte
- ✅ Sin configuración compleja del desarrollador

**Siguiente paso**: Prueba el flujo completo en tu app.

---

*¿Preguntas? Revisa el código en `components/google_drive_picker.py` o abre un issue.*
