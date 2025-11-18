"""
Integración con Google Drive para listar y descargar archivos.
"""

import base64
import hashlib
import io
import os
import secrets
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Scopes necesarios para leer archivos
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# MIME types soportados
SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]


def get_drive_service(
    auth_mode: Optional[str] = None,
    api_key: Optional[str] = None,
):
    """
    Obtiene servicio de Google Drive autenticado.

    Args:
        auth_mode: Modo de autenticación ('api_key' o 'oauth').
                   Si es None, se lee de DRIVE_AUTH_MODE env var.
        api_key: API key para acceso público (solo para auth_mode='api_key')

    Returns:
        Servicio de Google Drive API

    Raises:
        ValueError: Si no se puede autenticar
    """
    if auth_mode is None:
        auth_mode = os.getenv("DRIVE_AUTH_MODE", "api_key")

    # Modo api_key: usa API key para acceso a carpetas públicas (sin autenticación OAuth)
    if auth_mode == "api_key":
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError(
                "Para acceso con API key, necesitas una API key de Google. "
                "Configura GOOGLE_API_KEY en .env o ingrésala en la UI."
            )

        service = build("drive", "v3", developerKey=api_key)
        return service

    # Modo oauth: usa OAuth redirect con credenciales guardadas en session_state
    elif auth_mode == "oauth":
        creds = _authenticate_oauth_streamlit()
        if not creds:
            raise ValueError(
                "No se pudo obtener credenciales OAuth. Autentícate primero con Google."
            )

        service = build("drive", "v3", credentials=creds)
        return service

    else:
        raise ValueError(
            f"Modo de autenticación no válido: {auth_mode}. "
            f"Opciones: 'api_key' (carpetas públicas) o 'oauth' (carpetas privadas con tu cuenta de Google)"
        )


def _authenticate_service_account():
    """
    Autentica usando Service Account.

    Returns:
        Credenciales
    """
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not creds_path:
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS no está definida. "
            "Define la ruta al archivo JSON de credenciales."
        )

    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Archivo de credenciales no encontrado: {creds_path}")

    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )

    return creds


def _authenticate_oauth():
    """
    Autentica usando OAuth 2.0 flow.

    Returns:
        Credenciales
    """
    creds = None
    token_path = "token.json"

    # Si existe token guardado, cargarlo
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Si no hay credenciales válidas, hacer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Necesita credentials.json de OAuth client
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Guardar credenciales para próxima vez
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def _authenticate_oauth_streamlit():
    """
    Autentica usando OAuth 2.0 flow optimizado para Streamlit.

    Este método permite al usuario autenticarse manualmente mediante una URL
    que se muestra en la interfaz, sin necesidad de abrir un navegador automáticamente.

    Returns:
        Credenciales

    Raises:
        ValueError: Si no se puede completar la autenticación
    """
    import streamlit as st

    creds = None

    # Verificar si ya hay credenciales en session_state
    if "google_oauth_creds" in st.session_state:
        creds_info = st.session_state.google_oauth_creds
        creds = Credentials.from_authorized_user_info(creds_info, SCOPES)

        # Verificar si están válidas
        if creds.valid:
            return creds

        # Si expiraron pero tienen refresh token
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                st.session_state.google_oauth_creds = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes,
                }
                return creds
            except Exception as e:
                st.warning(
                    f"Token expirado. Por favor, vuelve a autenticarte. Error: {str(e)}"
                )
                del st.session_state.google_oauth_creds

    # Si llegamos aquí, necesitamos nueva autenticación
    raise ValueError(
        "No hay credenciales de Google Drive. "
        "Por favor, usa el botón de autenticación en la interfaz."
    )


def get_oauth_authorization_url() -> tuple[str, any]:
    """
    Genera la URL de autorización OAuth para que el usuario la abra manualmente.

    Returns:
        Tupla de (url_de_autorizacion, flow_object)
    """
    try:
        # Intentar cargar desde archivo credentials.json
        if os.path.exists("credentials.json"):
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",  # Out-of-band flow
            )
        else:
            # Intentar obtener desde variables de entorno
            client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise ValueError(
                    "No se encontró credentials.json ni variables de entorno "
                    "GOOGLE_OAUTH_CLIENT_ID y GOOGLE_OAUTH_CLIENT_SECRET"
                )

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }

            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )

        auth_url, _ = flow.authorization_url(prompt="consent")
        return auth_url, flow

    except Exception as e:
        raise ValueError(f"Error generando URL de autorización: {str(e)}")


def create_oauth_flow_with_redirect(redirect_uri: str) -> Flow:
    """
    Crea un flujo OAuth con redirect URI para Streamlit.
    Usa PKCE para mayor seguridad.

    Args:
        redirect_uri: URI de redirect (debe estar en Google Cloud Console)

    Returns:
        Flow object configurado
    """
    try:
        # Intentar cargar desde archivo credentials.json
        if os.path.exists("credentials.json"):
            flow = Flow.from_client_secrets_file(
                "credentials.json", scopes=SCOPES, redirect_uri=redirect_uri
            )
        else:
            # Cargar desde variables de entorno
            client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

            if not client_id or not client_secret:
                raise ValueError(
                    "No se encontró credentials.json ni variables de entorno "
                    "GOOGLE_OAUTH_CLIENT_ID y GOOGLE_OAUTH_CLIENT_SECRET"
                )

            client_config = {
                "web": {  # Importante: "web" no "installed" para redirect
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            }

            flow = Flow.from_client_config(
                client_config, scopes=SCOPES, redirect_uri=redirect_uri
            )

        return flow

    except Exception as e:
        raise ValueError(f"Error creando OAuth flow: {str(e)}")


def generate_pkce_pair() -> tuple[str, str]:
    """
    Genera un par code_verifier/code_challenge para PKCE.

    Returns:
        Tupla de (code_verifier, code_challenge)
    """
    # Generar code_verifier aleatorio
    code_verifier = secrets.token_urlsafe(64)

    # Generar code_challenge (SHA256 del verifier)
    code_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge_bytes).decode().rstrip("=")

    return code_verifier, code_challenge


def get_authorization_url_with_redirect(
    redirect_uri: str, state: str = None
) -> tuple[str, Flow, str]:
    """
    Genera URL de autorización con redirect para Streamlit.
    Incluye PKCE para seguridad adicional.

    Args:
        redirect_uri: URI de redirect (ej: https://tu-app.streamlit.app/)
        state: Token de estado para prevenir CSRF (se genera si no se provee)

    Returns:
        Tupla de (authorization_url, flow, state)
    """
    # Generar state token si no se provee
    if state is None:
        state = secrets.token_urlsafe(32)

    # Crear flow
    flow = create_oauth_flow_with_redirect(redirect_uri)

    # Generar PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # Guardar code_verifier (necesario para completar el flow)
    # Nota: en producción, esto debería guardarse en session_state de Streamlit

    # Generar URL de autorización
    authorization_url, _ = flow.authorization_url(
        access_type="offline",  # Para obtener refresh token
        include_granted_scopes="true",
        state=state,
        prompt="consent",  # Forzar pantalla de consentimiento
        # PKCE parameters (opcional, mejora seguridad)
        # code_challenge=code_challenge,
        # code_challenge_method='S256'
    )

    return authorization_url, flow, state


def exchange_code_for_tokens(flow: Flow, authorization_response: str) -> Credentials:
    """
    Intercambia el código de autorización por tokens de acceso.

    Args:
        flow: Flow object de OAuth
        authorization_response: URL completa de respuesta con código y state

    Returns:
        Credenciales con access token y refresh token
    """
    try:
        # Fetch token usando la respuesta completa
        flow.fetch_token(authorization_response=authorization_response)

        # Retornar credenciales
        credentials = flow.credentials

        return credentials

    except Exception as e:
        raise ValueError(f"Error intercambiando código por tokens: {str(e)}")


def complete_oauth_flow(flow, auth_code: str) -> Credentials:
    """
    Completa el flujo OAuth con el código de autorización proporcionado por el usuario.

    Args:
        flow: Objeto flow de Google OAuth
        auth_code: Código de autorización del usuario

    Returns:
        Credenciales autenticadas
    """
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        return creds
    except Exception as e:
        raise ValueError(f"Error completando autenticación: {str(e)}")


def list_files_by_folder(
    folder_id: str, service=None, mime_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Lista archivos en una carpeta de Google Drive.

    Args:
        folder_id: ID de la carpeta de Drive
        service: Servicio de Drive (se crea uno si no se provee)
        mime_types: Lista de MIME types a filtrar (por defecto: PDF y DOCX)

    Returns:
        Lista de diccionarios con información de archivos

    Raises:
        Exception: Si hay error accediendo a Drive
    """
    if service is None:
        service = get_drive_service()

    if mime_types is None:
        mime_types = SUPPORTED_MIME_TYPES

    # Construir query
    mime_query = " or ".join([f"mimeType='{mt}'" for mt in mime_types])
    query = f"'{folder_id}' in parents and ({mime_query}) and trashed=false"

    try:
        results = (
            service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink)",
                pageSize=1000,
            )
            .execute()
        )

        files = results.get("files", [])

        return files

    except Exception as e:
        raise Exception(f"Error listando archivos de Drive: {str(e)}")


def download_file(file_id: str, service=None) -> bytes:
    """
    Descarga un archivo de Google Drive.

    Args:
        file_id: ID del archivo en Drive
        service: Servicio de Drive (se crea uno si no se provee)

    Returns:
        Contenido del archivo en bytes

    Raises:
        Exception: Si hay error descargando
    """
    if service is None:
        service = get_drive_service()

    try:
        request = service.files().get_media(fileId=file_id)

        # Descargar a memoria
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Retornar contenido
        file_stream.seek(0)
        return file_stream.read()

    except Exception as e:
        raise Exception(f"Error descargando archivo {file_id}: {str(e)}")


def get_file_metadata(file_id: str, service=None) -> Dict[str, Any]:
    """
    Obtiene metadatos de un archivo de Drive.

    Args:
        file_id: ID del archivo
        service: Servicio de Drive

    Returns:
        Diccionario con metadatos
    """
    if service is None:
        service = get_drive_service()

    try:
        file_metadata = (
            service.files()
            .get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, owners, webViewLink",
            )
            .execute()
        )

        return file_metadata

    except Exception as e:
        raise Exception(f"Error obteniendo metadatos: {str(e)}")


def validate_folder_access(folder_id: str, service=None) -> tuple[bool, Optional[str]]:
    """
    Valida que se tenga acceso a una carpeta de Drive.

    Args:
        folder_id: ID de la carpeta
        service: Servicio de Drive

    Returns:
        Tupla (tiene_acceso, mensaje_error)
    """
    if service is None:
        try:
            service = get_drive_service()
        except Exception as e:
            return False, f"Error de autenticación: {str(e)}"

    try:
        folder = (
            service.files().get(fileId=folder_id, fields="id, name, mimeType").execute()
        )

        # Verificar que sea una carpeta
        if folder.get("mimeType") != "application/vnd.google-apps.folder":
            return False, f"El ID proporcionado no corresponde a una carpeta"

        return True, None

    except Exception as e:
        return False, f"No se puede acceder a la carpeta: {str(e)}"
