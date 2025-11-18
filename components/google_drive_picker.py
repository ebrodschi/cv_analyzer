"""
Google Drive Picker Component para Streamlit.
Permite al usuario autenticarse y seleccionar archivos con su propia cuenta.
"""

from typing import Optional

import streamlit.components.v1 as components


def google_drive_picker(
    api_key: str,
    client_id: str,
    app_id: Optional[str] = None,
    folder_only: bool = True,
    key: Optional[str] = None,
) -> dict:
    """
    Muestra el Google Drive Picker para que el usuario seleccione archivos/carpetas.

    IMPORTANTE: Este componente permite AUTENTICACIÓN CLIENT-SIDE.
    - El usuario se autentica con SU propia cuenta de Google
    - NO requiere OAuth del desarrollador (solo API Key y Client ID)
    - El usuario otorga permisos directamente desde su navegador

    Args:
        api_key: API Key de Google Cloud (pública, puede estar en código)
        client_id: OAuth Client ID (solo ID, NO secret) - tipo "Aplicación web"
        app_id: ID del proyecto de Google Cloud (opcional)
        folder_only: Si True, solo permite seleccionar carpetas
        key: Key única para el component (opcional)

    Returns:
        Dict con:
        - access_token: Token de acceso del usuario
        - folder_id: ID de la carpeta seleccionada (si folder_only=True)
        - files: Lista de archivos seleccionados (si folder_only=False)

    Ejemplo de uso:
        ```python
        result = google_drive_picker(
            api_key="AIza...",
            client_id="123-abc.apps.googleusercontent.com"
        )

        if result:
            st.write(f"Token: {result['access_token']}")
            st.write(f"Carpeta: {result['folder_id']}")
        ```

    Setup requerido en Google Cloud Console:
        1. Habilitar Google Drive API
        2. Habilitar Google Picker API
        3. Crear API Key (Credenciales → API Key)
        4. Crear OAuth Client ID tipo "Aplicación web"
           - Orígenes autorizados: https://tu-app.streamlit.app
           - NO necesitas redirect URIs
        5. En "Pantalla de consentimiento OAuth":
           - Agregar scope: https://www.googleapis.com/auth/drive.readonly
    """

    # HTML + JavaScript para Google Drive Picker
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://accounts.google.com/gsi/client" async defer></script>
        <script src="https://apis.google.com/js/api.js"></script>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                padding: 20px;
                margin: 0;
            }}

            #auth-container {{
                text-align: center;
                padding: 20px;
            }}

            .auth-button {{
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                border-radius: 4px;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                transition: background-color 0.3s;
            }}

            .auth-button:hover {{
                background-color: #357ae8;
            }}

            .auth-button:disabled {{
                background-color: #ccc;
                cursor: not-allowed;
            }}

            .status {{
                margin-top: 20px;
                padding: 10px;
                border-radius: 4px;
            }}

            .status.success {{
                background-color: #d4edda;
                color: #155724;
            }}

            .status.error {{
                background-color: #f8d7da;
                color: #721c24;
            }}

            .status.info {{
                background-color: #d1ecf1;
                color: #0c5460;
            }}

            .google-icon {{
                width: 20px;
                height: 20px;
            }}
        </style>
    </head>
    <body>
        <div id="auth-container">
            <h3>🔐 Conectar con Google Drive</h3>
            <p>Autoriza el acceso a tu Google Drive para seleccionar archivos</p>

            <button id="authorize-button" class="auth-button">
                <svg class="google-icon" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z"/>
                </svg>
                Autorizar con Google
            </button>

            <div id="status"></div>
        </div>

        <script>
            const API_KEY = '{api_key}';
            const CLIENT_ID = '{client_id}';
            const APP_ID = '{app_id or ""}';
            const FOLDER_ONLY = {str(folder_only).lower()};
            const SCOPES = 'https://www.googleapis.com/auth/drive.readonly';

            let tokenClient;
            let accessToken = null;
            let pickerInited = false;
            let gisInited = false;

            // Mostrar status
            function showStatus(message, type = 'info') {{
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status ' + type;
                statusDiv.innerHTML = message;
            }}

            // Inicializar Google Identity Services
            function gisLoaded() {{
                tokenClient = google.accounts.oauth2.initTokenClient({{
                    client_id: CLIENT_ID,
                    scope: SCOPES,
                    callback: async (response) => {{
                        if (response.error !== undefined) {{
                            showStatus('❌ Error de autenticación: ' + response.error, 'error');
                            throw (response);
                        }}

                        accessToken = response.access_token;
                        showStatus('✅ Autenticado correctamente. Abriendo selector...', 'success');

                        // Abrir picker automáticamente después de autorizar
                        createPicker();
                    }},
                }});
                gisInited = true;
                maybeEnableButton();
            }}

            // Inicializar Google Picker API
            function pickerLoaded() {{
                pickerInited = true;
                maybeEnableButton();
            }}

            // Habilitar botón cuando todo esté listo
            function maybeEnableButton() {{
                if (pickerInited && gisInited) {{
                    document.getElementById('authorize-button').disabled = false;
                    showStatus('✅ Listo para conectar', 'success');
                }}
            }}

            // Manejar clic en botón de autorización
            document.getElementById('authorize-button').addEventListener('click', () => {{
                if (accessToken === null) {{
                    // Solicitar token de acceso
                    tokenClient.requestAccessToken({{prompt: 'consent'}});
                }} else {{
                    // Ya tenemos token, abrir picker directamente
                    createPicker();
                }}
            }});

            // Crear y mostrar el picker
            function createPicker() {{
                const view = FOLDER_ONLY
                    ? new google.picker.DocsView(google.picker.ViewId.FOLDERS)
                        .setSelectFolderEnabled(true)
                    : new google.picker.DocsView()
                        .setIncludeFolders(true);

                const picker = new google.picker.PickerBuilder()
                    .enableFeature(google.picker.Feature.NAV_HIDDEN)
                    .setAppId(APP_ID || CLIENT_ID.split('-')[0])
                    .setOAuthToken(accessToken)
                    .addView(view)
                    .setDeveloperKey(API_KEY)
                    .setCallback(pickerCallback)
                    .build();

                picker.setVisible(true);
            }}

            // Callback cuando el usuario selecciona algo
            function pickerCallback(data) {{
                if (data.action === google.picker.Action.PICKED) {{
                    const selectedItems = data.docs;

                    if (FOLDER_ONLY && selectedItems.length > 0) {{
                        const folder = selectedItems[0];

                        // Enviar resultado a Streamlit
                        const result = {{
                            access_token: accessToken,
                            folder_id: folder.id,
                            folder_name: folder.name,
                            type: 'folder'
                        }};

                        showStatus('✅ Carpeta seleccionada: ' + folder.name, 'success');

                        // Enviar a Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: result
                        }}, '*');

                    }} else if (!FOLDER_ONLY) {{
                        // Enviar lista de archivos
                        const result = {{
                            access_token: accessToken,
                            files: selectedItems.map(item => ({{
                                id: item.id,
                                name: item.name,
                                mimeType: item.mimeType,
                                url: item.url
                            }})),
                            type: 'files'
                        }};

                        showStatus('✅ ' + selectedItems.length + ' archivo(s) seleccionado(s)', 'success');

                        // Enviar a Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: result
                        }}, '*');
                    }}
                }} else if (data.action === google.picker.Action.CANCEL) {{
                    showStatus('ℹ️ Selección cancelada', 'info');
                }}
            }}

            // Cargar las APIs
            gapi.load('picker', pickerLoaded);

            // Cargar GIS cuando el script esté listo
            if (window.google && window.google.accounts) {{
                gisLoaded();
            }} else {{
                window.addEventListener('load', () => {{
                    setTimeout(gisLoaded, 100);
                }});
            }}

            // Deshabilitar botón inicialmente
            document.getElementById('authorize-button').disabled = true;
            showStatus('⏳ Cargando...', 'info');
        </script>
    </body>
    </html>
    """

    # Renderizar el component
    component_value = components.html(
        html_code,
        height=300,
        scrolling=False,
    )

    return component_value


def google_drive_auth_button(
    api_key: str,
    client_id: str,
    scopes: str = "https://www.googleapis.com/auth/drive.readonly",
    key: Optional[str] = None,
) -> Optional[str]:
    """
    Botón de autenticación simple con Google.
    Devuelve el access token del usuario.

    Args:
        api_key: API Key de Google
        client_id: OAuth Client ID
        scopes: Scopes de OAuth (por defecto: drive.readonly)
        key: Key del component

    Returns:
        Access token si el usuario se autenticó, None si no
    """

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://accounts.google.com/gsi/client" async defer></script>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                padding: 10px;
                margin: 0;
            }}
            .container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div id="buttonDiv"></div>
            <div id="status"></div>
        </div>

        <script>
            let tokenClient;

            function initClient() {{
                tokenClient = google.accounts.oauth2.initTokenClient({{
                    client_id: '{client_id}',
                    scope: '{scopes}',
                    callback: (response) => {{
                        if (response.access_token) {{
                            document.getElementById('status').innerHTML = '✅ Autenticado';

                            // Enviar token a Streamlit
                            window.parent.postMessage({{
                                type: 'streamlit:setComponentValue',
                                value: response.access_token
                            }}, '*');
                        }}
                    }},
                }});

                // Crear botón de Google
                google.accounts.id.renderButton(
                    document.getElementById('buttonDiv'),
                    {{
                        theme: 'outline',
                        size: 'large',
                        text: 'signin_with',
                        shape: 'rectangular',
                    }}
                );
            }}

            // Inicializar cuando Google Identity esté listo
            window.onload = function() {{
                initClient();
            }};
        </script>
    </body>
    </html>
    """

    component_value = components.html(html_code, height=150)

    return component_value
    return component_value
