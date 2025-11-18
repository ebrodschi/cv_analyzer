"""
Script de prueba para verificar los diferentes modos de autenticación de Google Drive.

Uso:
    python test_drive_auth.py --mode public --folder-id YOUR_FOLDER_ID
    python test_drive_auth.py --mode service --folder-id YOUR_FOLDER_ID
    python test_drive_auth.py --mode oauth --folder-id YOUR_FOLDER_ID
"""

import argparse
import os
import sys

from ingestion.drive import (
    get_drive_service,
    list_files_by_folder,
    validate_folder_access,
)


def test_public_mode(folder_id: str, api_key: str = None):
    """Prueba el modo de carpetas públicas."""
    print("\n🔍 Probando modo PUBLIC (carpetas públicas)...")

    try:
        # Obtener servicio
        service = get_drive_service(auth_mode="public", api_key=api_key)
        print("✅ Servicio de Drive creado correctamente")

        # Validar acceso
        has_access, error = validate_folder_access(folder_id, service)

        if not has_access:
            print(f"❌ Error validando acceso: {error}")
            return False

        print("✅ Acceso a la carpeta validado")

        # Listar archivos
        files = list_files_by_folder(folder_id, service)
        print(f"✅ Archivos encontrados: {len(files)}")

        if files:
            print("\n📄 Primeros 5 archivos:")
            for file in files[:5]:
                print(f"  - {file['name']} ({file['mimeType']})")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_service_mode(folder_id: str):
    """Prueba el modo de Service Account."""
    print("\n🤖 Probando modo SERVICE (Service Account)...")

    try:
        # Verificar que exista el archivo de credenciales
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not creds_path:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS no está definida")
            return False

        if not os.path.exists(creds_path):
            print(f"❌ Archivo de credenciales no encontrado: {creds_path}")
            return False

        print(f"✅ Archivo de credenciales encontrado: {creds_path}")

        # Obtener servicio
        service = get_drive_service(auth_mode="service")
        print("✅ Servicio de Drive creado correctamente")

        # Validar acceso
        has_access, error = validate_folder_access(folder_id, service)

        if not has_access:
            print(f"❌ Error validando acceso: {error}")
            print(
                "\n💡 Asegúrate de que la carpeta esté compartida con el email de la service account"
            )
            return False

        print("✅ Acceso a la carpeta validado")

        # Listar archivos
        files = list_files_by_folder(folder_id, service)
        print(f"✅ Archivos encontrados: {len(files)}")

        if files:
            print("\n📄 Primeros 5 archivos:")
            for file in files[:5]:
                print(f"  - {file['name']} ({file['mimeType']})")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_oauth_mode(folder_id: str):
    """Prueba el modo OAuth tradicional."""
    print("\n🌐 Probando modo OAUTH (OAuth tradicional)...")

    try:
        # Verificar que exista credentials.json
        if not os.path.exists("credentials.json"):
            print("❌ credentials.json no encontrado")
            return False

        print("✅ credentials.json encontrado")

        # Obtener servicio (abrirá navegador si es necesario)
        service = get_drive_service(auth_mode="oauth")
        print("✅ Servicio de Drive creado correctamente")

        # Validar acceso
        has_access, error = validate_folder_access(folder_id, service)

        if not has_access:
            print(f"❌ Error validando acceso: {error}")
            return False

        print("✅ Acceso a la carpeta validado")

        # Listar archivos
        files = list_files_by_folder(folder_id, service)
        print(f"✅ Archivos encontrados: {len(files)}")

        if files:
            print("\n📄 Primeros 5 archivos:")
            for file in files[:5]:
                print(f"  - {file['name']} ({file['mimeType']})")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Prueba los modos de autenticación de Google Drive"
    )

    parser.add_argument(
        "--mode",
        choices=["public", "service", "oauth", "all"],
        default="public",
        help="Modo de autenticación a probar",
    )

    parser.add_argument(
        "--folder-id", required=True, help="ID de la carpeta de Google Drive"
    )

    parser.add_argument(
        "--api-key", help="API key para modo public (opcional si está en .env)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🧪 TEST DE AUTENTICACIÓN DE GOOGLE DRIVE")
    print("=" * 60)

    results = {}

    if args.mode == "all":
        modes_to_test = ["public", "service", "oauth"]
    else:
        modes_to_test = [args.mode]

    for mode in modes_to_test:
        if mode == "public":
            success = test_public_mode(args.folder_id, args.api_key)
            results["public"] = success

        elif mode == "service":
            success = test_service_mode(args.folder_id)
            results["service"] = success

        elif mode == "oauth":
            success = test_oauth_mode(args.folder_id)
            results["oauth"] = success

        print("\n" + "-" * 60)

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    for mode, success in results.items():
        status = "✅ ÉXITO" if success else "❌ FALLÓ"
        print(f"{mode.upper():15} : {status}")

    # Código de salida
    all_success = all(results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
    main()
