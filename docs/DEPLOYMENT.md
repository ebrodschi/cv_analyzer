# Deployment Guide

## 🚀 Deployment en Streamlit Cloud (Gratis)

### Paso 1: Preparar el Repositorio

1. **Crear repositorio en GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: CV Analyzer"
   git branch -M main
   git remote add origin https://github.com/tu-usuario/cv-analyzer.git
   git push -u origin main
   ```

2. **Asegurar que estos archivos estén en el repo:**
   - ✅ `app.py`
   - ✅ `requirements.txt`
   - ✅ `.streamlit/config.toml`
   - ✅ Todos los módulos (`llm_client/`, `parsing/`, etc.)

### Paso 2: Deploy en Streamlit Cloud

1. **Ir a [share.streamlit.io](https://share.streamlit.io)**

2. **Conectar tu cuenta de GitHub**

3. **Crear nueva app:**
   - Repository: `tu-usuario/cv-analyzer`
   - Branch: `main`
   - Main file path: `app.py`

4. **Configurar Secrets** (Advanced settings):
   ```toml
   # En la sección "Secrets"
   [secrets]
   openai_api_key = "sk-tu-api-key-aquí"

   # Opcional: Para Google Drive
   drive_auth_mode = "service"
   google_service_account = '''
   {
     "type": "service_account",
     "project_id": "tu-proyecto",
     "private_key_id": "...",
     "private_key": "...",
     "client_email": "...",
     "client_id": "..."
   }
   '''
   ```

5. **Deploy!** 🎉
   - La app estará disponible en: `https://tu-app.streamlit.app`

### Paso 3: Actualizar la App

```bash
git add .
git commit -m "Update: descripción del cambio"
git push
```

Streamlit Cloud detectará el cambio y redesplegará automáticamente.

---

## 🐳 Deployment con Docker

### Crear Dockerfile

Ya está incluido. Ver `Dockerfile` en el proyecto.

### Build y Run

```bash
# Build
docker build -t cv-analyzer .

# Run
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=tu-key-aquí \
  cv-analyzer
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  cv-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
```

Run:
```bash
docker-compose up
```

---

## ☁️ Deployment en AWS

### Opción 1: AWS Elastic Beanstalk

1. **Instalar AWS CLI y EB CLI**
   ```bash
   pip install awscli awsebcli
   ```

2. **Inicializar EB**
   ```bash
   eb init -p python-3.9 cv-analyzer
   ```

3. **Crear environment**
   ```bash
   eb create cv-analyzer-env
   ```

4. **Configurar variables de entorno**
   ```bash
   eb setenv OPENAI_API_KEY=tu-key-aquí
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

### Opción 2: AWS EC2

1. **Lanzar instancia EC2** (Ubuntu 22.04)

2. **SSH a la instancia**
   ```bash
   ssh -i tu-key.pem ubuntu@tu-ip
   ```

3. **Instalar dependencias**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx -y
   ```

4. **Clonar repo y setup**
   ```bash
   git clone https://github.com/tu-usuario/cv-analyzer.git
   cd cv-analyzer
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Crear service systemd**
   ```bash
   sudo nano /etc/systemd/system/cv-analyzer.service
   ```

   Contenido:
   ```ini
   [Unit]
   Description=CV Analyzer Streamlit App
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/cv-analyzer
   Environment="OPENAI_API_KEY=tu-key-aquí"
   ExecStart=/home/ubuntu/cv-analyzer/venv/bin/streamlit run app.py --server.port 8501
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Iniciar service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable cv-analyzer
   sudo systemctl start cv-analyzer
   ```

7. **Configurar nginx (opcional)**
   Para usar puerto 80 y SSL.

---

## 🔷 Deployment en Azure

### Azure Web Apps

1. **Crear Web App**
   ```bash
   az webapp up --name cv-analyzer --runtime "PYTHON:3.9"
   ```

2. **Configurar variables**
   ```bash
   az webapp config appsettings set \
     --name cv-analyzer \
     --resource-group tu-grupo \
     --settings OPENAI_API_KEY=tu-key
   ```

3. **Deploy**
   ```bash
   git push azure main
   ```

---

## 🔧 Configuración Post-Deployment

### Límites de Recursos

Para apps públicas, considera:

```python
# En app.py, agregar al inicio:
MAX_CONCURRENT_USERS = 10
MAX_FILES_PER_USER = 50

# Usar st.session_state para tracking
if 'processing' not in st.session_state:
    st.session_state.processing = False

if st.session_state.processing:
    st.warning("Ya hay un procesamiento en curso...")
```

### Rate Limiting

Para evitar abuso:

```python
import time
from datetime import datetime, timedelta

# Simple rate limiter
if 'last_process_time' in st.session_state:
    time_since_last = datetime.now() - st.session_state.last_process_time
    if time_since_last < timedelta(seconds=30):
        st.error("Espera 30 segundos entre procesamientos")
        return

st.session_state.last_process_time = datetime.now()
```

### Monitoring

Agregar logging para producción:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cv_analyzer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usar en el código:
logger.info(f"Procesando {len(files)} archivos")
logger.error(f"Error en archivo {filename}: {error}")
```

---

## 📊 Costos Estimados

### Streamlit Cloud
- **Free tier**: 1 app privada gratis
- **Community**: Apps públicas gratis con recursos limitados
- **Team**: $250/mes para apps privadas ilimitadas

### OpenAI API (usando gpt-4o-mini)
- ~$0.15 por 1M tokens input
- ~$0.60 por 1M tokens output
- **Estimado**: ~$0.01-0.02 por CV analizado
- 100 CVs ≈ $1-2 USD

### AWS EC2
- **t2.micro**: ~$8/mes (incluido en free tier)
- **t3.small**: ~$15/mes (recomendado para producción)

### Azure Web Apps
- **Free tier**: Gratis con limitaciones
- **Basic B1**: ~$13/mes

---

## 🔒 Security Best Practices

1. **API Keys**
   - ✅ NUNCA en el código
   - ✅ Usar variables de entorno
   - ✅ Rotar periódicamente

2. **Google Drive**
   - ✅ Service Account con permisos mínimos
   - ✅ Solo acceso de lectura

3. **Input Validation**
   - ✅ Validar tamaño de archivos
   - ✅ Verificar tipos MIME
   - ✅ Limitar número de archivos

4. **Rate Limiting**
   - ✅ Implementar límites por usuario
   - ✅ Timeouts en procesamiento

5. **Logging**
   - ✅ No loggear información sensible
   - ✅ Monitorear errores

---

## 📈 Scaling Considerations

Para más de 100 CVs/día:

1. **Usar Queue/Background Jobs**
   - Celery + Redis
   - AWS SQS
   - Google Cloud Tasks

2. **Cache**
   - Redis para resultados
   - Cloudflare para assets

3. **Database**
   - PostgreSQL para resultados
   - Elasticsearch para búsqueda

4. **Load Balancing**
   - Múltiples instancias
   - Nginx load balancer

---

## 🆘 Troubleshooting Deployment

### "Module not found" en producción
Asegurar que `requirements.txt` tenga todas las dependencias.

### "Streamlit hello" en vez de la app
Verificar que el path sea correcto: `app.py` (no `./app.py`)

### API timeouts
Aumentar `max_tokens` y `temperature` para respuestas más rápidas.

### Out of memory
- Reducir `max_workers` (concurrencia)
- Procesar en lotes más pequeños
- Usar instancia con más RAM

---

## ✅ Checklist Pre-Deployment

- [ ] `requirements.txt` actualizado
- [ ] `.env.example` documentado
- [ ] Secrets configurados
- [ ] Tests pasando (`pytest tests/`)
- [ ] README completo
- [ ] `.gitignore` correcto (no subir `.env`, credentials, etc)
- [ ] Logs implementados
- [ ] Error handling robusto
- [ ] Rate limiting (si es público)
- [ ] Documentación de API keys
- [ ] Backups configurados (si hay DB)

---

**¡Listo para producción! 🚀**
