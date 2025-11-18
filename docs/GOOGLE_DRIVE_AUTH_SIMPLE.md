# 🔑 Guía Simple: Conectar Google Drive con API Key

Esta aplicación usa **solo API Key** para acceder a carpetas públicas de Google Drive.

## ⚡ Configuración Rápida (5 minutos)

### 1. Obtén tu API Key

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea/selecciona un proyecto
3. Habilita **Google Drive API** (APIs y servicios → Biblioteca)
4. Crea **API Key** (Credenciales → + Crear Credenciales → Clave de API)
5. Copia la key (ejemplo: `AIzaSyC1234...`)

### 2. Haz pública tu carpeta

1. En Google Drive, clic derecho en la carpeta → **Compartir**
2. Cambia a **"Cualquiera con el enlace"** (Lector)
3. Copia el ID de la URL:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                          ↑ Este es el ID
   ```

### 3. Usa en la app

1. Abre la aplicación
2. Ingresa tu **API key**
3. Ingresa el **ID de la carpeta**
4. Clic en **🔍 Listar Archivos**

✅ ¡Listo!

---

## 🆘 Errores Comunes

**"File not found"** → La carpeta no es pública. Asegúrate de configurar "Cualquiera con el enlace"

**"API key no encontrada"** → Verifica que la API key esté correctamente ingresada (sin espacios)

**"No autorizado"** → Habilita Google Drive API en tu proyecto de Google Cloud

---

Para más detalles, consulta el archivo `GOOGLE_DRIVE_AUTH.md`
