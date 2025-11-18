# 📚 Índice de Documentación - CV Analyzer

Bienvenido al proyecto **CV Analyzer**. Aquí encontrarás enlaces a toda la documentación.

---

## 🚀 Inicio Rápido

**¿Primera vez aquí?** Empieza por:

1. **[QUICKSTART.md](QUICKSTART.md)** - Comienza en 5 minutos ⚡
2. **[README.md](README.md)** - Documentación completa 📖
3. **[SUMMARY.md](SUMMARY.md)** - Resumen ejecutivo del proyecto 🎯

---

## 📖 Documentación Principal

### Para Usuarios

| Documento | Descripción | Tiempo de Lectura |
|-----------|-------------|-------------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Guía de inicio rápido con scripts automáticos | 5 min |
| **[README.md](README.md)** | Documentación completa: instalación, uso, configuración | 15 min |
| **[GOOGLE_DRIVE_AUTH.md](GOOGLE_DRIVE_AUTH.md)** | ⭐ Guía completa de autenticación con Google Drive (4 modos) | 10 min |

### Para Desarrolladores

| Documento | Descripción | Tiempo de Lectura |
|-----------|-------------|-------------------|
| **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** | Arquitectura, estructura, flujo de datos, convenciones | 20 min |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Guía para contribuir, estándares de código, PRs | 10 min |
| **Docstrings en código** | Cada función/clase está documentada | N/A |

### Para DevOps/Admins

| Documento | Descripción | Tiempo de Lectura |
|-----------|-------------|-------------------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Deployment en Streamlit Cloud, Docker, AWS, Azure | 30 min |
| **[docker-compose.yml](docker-compose.yml)** | Configuración Docker Compose | 5 min |
| **[Dockerfile](Dockerfile)** | Configuración de contenedor | 5 min |

### Para Stakeholders

| Documento | Descripción | Tiempo de Lectura |
|-----------|-------------|-------------------|
| **[SUMMARY.md](SUMMARY.md)** | Resumen ejecutivo, métricas, ROI, casos de uso | 10 min |
| **[LICENSE](LICENSE)** | Licencia MIT - open source | 2 min |

---

## 🗂️ Índice por Tema

### 🎯 Getting Started

- [Instalación](README.md#-instalación)
- [Configuración de API Keys](README.md#4-configurar-variables-de-entorno)
- [Primer Uso](QUICKSTART.md#-uso-básico)
- [Test Básico sin UI](QUICKSTART.md#-test-rápido-sin-ui)

### ⚙️ Configuración

- [Variables de Entorno](.env.example)
- [Schema YAML](README.md#-schema-yaml)
- [Google Drive - Guía Completa](GOOGLE_DRIVE_AUTH.md) ⭐
- [Google Drive Setup Rápido](README.md#5-opcional-configurar-google-drive)
- [Opciones Avanzadas](README.md#-opciones-avanzadas)

### 🚀 Uso

- [Subir Archivos Locales](README.md#flujo-de-trabajo)
- [Conectar Google Drive](README.md#flujo-de-trabajo)
- [Personalizar Schema](README.md#-schema-yaml)
- [Exportar Resultados](README.md#flujo-de-trabajo)

### 🏗️ Arquitectura

- [Estructura del Proyecto](PROJECT_STRUCTURE.md#-estructura-del-proyecto-cv-analyzer)
- [Flujo de Datos](PROJECT_STRUCTURE.md#️-flujo-de-datos)
- [Módulos Principales](PROJECT_STRUCTURE.md#-módulos-principales)
- [Dependencias](PROJECT_STRUCTURE.md#-dependencias-entre-módulos)

### 💻 Desarrollo

- [Setup de Desarrollo](CONTRIBUTING.md#-cómo-contribuir)
- [Guías de Estilo](CONTRIBUTING.md#-guías-de-estilo)
- [Escribir Tests](CONTRIBUTING.md#-tests)
- [Áreas para Contribuir](CONTRIBUTING.md#-áreas-para-contribuir)

### 🚢 Deployment

- [Streamlit Cloud](DEPLOYMENT.md#-deployment-en-streamlit-cloud-gratis)
- [Docker](DEPLOYMENT.md#-deployment-con-docker)
- [AWS](DEPLOYMENT.md#️-deployment-en-aws)
- [Azure](DEPLOYMENT.md#-deployment-en-azure)

### 🧪 Testing

- [Ejecutar Tests](CONTRIBUTING.md#ejecutar-tests)
- [Test Básico](QUICKSTART.md#-test-rápido-sin-ui)
- [Coverage](CONTRIBUTING.md#ejecutar-tests)

### 📊 Métricas y ROI

- [Costos Estimados](SUMMARY.md#-costos-estimados)
- [Casos de Uso](SUMMARY.md#-casos-de-uso)
- [ROI Calculation](SUMMARY.md#análisis-de-100-cvs)

---

## 📁 Archivos de Configuración

### Esenciales

```
.env.example              # ⭐ Template de variables de entorno
requirements.txt          # ⭐ Dependencias Python
```

### Streamlit

```
.streamlit/
├── config.toml           # Configuración de tema y servidor
└── secrets.toml.example  # Template de secrets para Cloud
```

### Docker

```
Dockerfile                # Imagen de contenedor
docker-compose.yml        # Orquestación multi-container
```

### Scripts

```
start.sh                  # 🐧 Inicio automático (Linux/macOS)
start.bat                 # 🪟 Inicio automático (Windows)
test_basic.py            # 🧪 Test sin UI
```

---

## 🎓 Tutoriales

### Tutorial 1: Primer Análisis de CVs (5 min)

1. Ejecuta `./start.sh` (o `start.bat` en Windows)
2. Configura tu API key en `.env`
3. Sube 2-3 CVs de prueba
4. Haz clic en "Procesar CVs"
5. Descarga el Excel

**[Ver guía completa →](QUICKSTART.md)**

### Tutorial 2: Personalizar Schema (10 min)

1. En la sidebar, desmarca "Usar esquema por defecto"
2. Edita el YAML para agregar campos custom
3. Valida el schema
4. Procesa CVs con tu schema
5. Verifica los nuevos campos en el Excel

**[Ver tipos soportados →](README.md#-schema-yaml)**

### Tutorial 3: Conectar Google Drive (Varios Modos)

**Opción A - Carpetas Públicas (5 min):**
1. Obtén una API key de Google Cloud Console
2. Haz pública tu carpeta de Drive
3. Configura `GOOGLE_API_KEY` en `.env`
4. Selecciona modo "public" en la UI
5. Lista y procesa archivos

**Opción B - OAuth en UI (10 min):**
1. Crea OAuth Client ID en Google Cloud
2. Configura credenciales
3. Autentica directamente en la interfaz
4. Accede a carpetas privadas

**Opción C - Service Account (15 min):**
1. Crea Service Account en Google Cloud
2. Descarga credenciales JSON
3. Comparte carpeta con la service account
4. Configura `GOOGLE_APPLICATION_CREDENTIALS`
5. Lista y procesa archivos

**[Ver guía completa con los 4 modos →](GOOGLE_DRIVE_AUTH.md)**

### Tutorial 4: Deploy en Streamlit Cloud (10 min)

1. Push código a GitHub
2. Ve a share.streamlit.io
3. Conecta tu repo
4. Configura secrets
5. Deploy!

**[Ver guía completa →](DEPLOYMENT.md#-deployment-en-streamlit-cloud-gratis)**

---

## 🔍 Búsqueda Rápida

### "¿Cómo hago para...?"

| Tarea | Documento | Sección |
|-------|-----------|---------|
| Instalar la app | [QUICKSTART.md](QUICKSTART.md) | Inicio Rápido |
| Configurar API key | [README.md](README.md) | Instalación → Paso 4 |
| Subir archivos | [README.md](README.md) | Flujo de trabajo → Paso 3 |
| Conectar Google Drive | [README.md](README.md) | Configurar Google Drive |
| Personalizar campos | [README.md](README.md) | Schema YAML |
| Exportar a Excel | [README.md](README.md) | Flujo de trabajo → Paso 5 |
| Deployar la app | [DEPLOYMENT.md](DEPLOYMENT.md) | Varias opciones |
| Contribuir código | [CONTRIBUTING.md](CONTRIBUTING.md) | Cómo Contribuir |
| Ver arquitectura | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Estructura |
| Reportar un bug | [CONTRIBUTING.md](CONTRIBUTING.md) | Reportar Bugs |

---

## 📞 Ayuda y Soporte

### Tengo un Problema

1. **Revisa el troubleshooting**: [README.md → Troubleshooting](README.md#️-troubleshooting)
2. **Ejecuta el test básico**: `python test_basic.py`
3. **Revisa los logs**: En la consola donde ejecutaste streamlit
4. **Busca en Issues**: Puede que ya esté resuelto
5. **Abre un nuevo Issue**: Con detalles del error

### Tengo una Pregunta

1. **Revisa la documentación**: Usa el índice arriba
2. **Busca en el código**: Los docstrings son detallados
3. **Revisa los ejemplos**: En `tests/samples/`
4. **Abre una Discussion**: Para preguntas generales

### Quiero Contribuir

1. **Lee la guía**: [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Revisa la estructura**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
3. **Busca "Good First Issue"**: En GitHub Issues
4. **Abre un PR**: Con tus cambios

---

## 🗺️ Roadmap

Ver [SUMMARY.md → Próximos Pasos](SUMMARY.md#-próximos-pasos-sugeridos) para el roadmap completo.

---

## 📊 Métricas del Proyecto

- **Líneas de código**: ~3,500
- **Módulos**: 7
- **Tests**: 12+
- **Documentación**: 2,500+ líneas
- **Cobertura**: Módulos críticos

**[Ver métricas completas →](SUMMARY.md#-métricas-del-proyecto)**

---

## 🏆 Características Destacadas

✅ Múltiples proveedores LLM (OpenAI, Anthropic, Azure)
✅ Google Drive integration
✅ Schema personalizable vía YAML
✅ Export formateado (Excel, CSV, JSON)
✅ Procesamiento concurrente
✅ Validación automática con retry
✅ Fallback para parsing de PDFs
✅ UI intuitiva con Streamlit
✅ Deployment en 1 click
✅ Open source (MIT)

**[Ver diferenciadores →](SUMMARY.md#-diferenciadores-clave)**

---

## 📝 Licencia

Este proyecto está bajo licencia **MIT**.

Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [Streamlit](https://streamlit.io/) - Framework web
- [OpenAI](https://openai.com/) - API LLM
- [LiteLLM](https://github.com/BerriAI/litellm) - Abstracción multi-proveedor

---

## 📌 Links Rápidos

| Link | Descripción |
|------|-------------|
| [GitHub Repo](#) | Código fuente |
| [Demo Live](#) | Demo en vivo (si está deployado) |
| [Issues](https://github.com/tu-usuario/cv-analyzer/issues) | Reportar bugs |
| [Discussions](https://github.com/tu-usuario/cv-analyzer/discussions) | Preguntas y discusiones |

---

## 📅 Última Actualización

**Versión**: 1.0.0
**Fecha**: Octubre 2024
**Estado**: ✅ Producción

---

**¿Listo para comenzar?** 👉 [QUICKSTART.md](QUICKSTART.md)

**¿Necesitas ayuda?** 👉 [README.md → Troubleshooting](README.md#️-troubleshooting)

**¿Quieres contribuir?** 👉 [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Hecho con ❤️ y ☕ | [Ver resumen ejecutivo →](SUMMARY.md)*
