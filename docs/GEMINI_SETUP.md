# 🌟 Guía de Configuración de Google Gemini

## ¿Por qué usar Gemini para análisis de CVs?

### 💰 Ventajas Económicas

- **Gemini 1.5 Flash 8B**: Hasta **10x más barato** que GPT-4o
- **Cuota gratis generosa**: 1,500 requests/día en tier gratuito
- **Sin necesidad de tarjeta**: Comienza gratis inmediatamente

### ⚡ Ventajas Técnicas

- **Rápido**: Flash models optimizados para baja latencia
- **Contexto largo**: Hasta 1M tokens de contexto (perfecto para múltiples CVs)
- **Multilingüe**: Excelente soporte para español
- **JSON mode**: Structured output nativo

---

## 🚀 Configuración Rápida (5 minutos)

### Paso 1: Obtener API Key

1. Ve a: **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
2. Haz clic en **"Create API Key"**
3. Selecciona un proyecto de Google Cloud (o crea uno nuevo)
4. Copia la API key que empieza con `AIzaSy...`

### Paso 2: Configurar en la App

**Opción A - Archivo .env (Recomendado)**:

```bash
# Crea el archivo .env si no existe:
cp .env.example .env

# Edita .env y agrega:
GEMINI_API_KEY=AIzaSy-tu-key-real-aqui
```

**Opción B - Input por UI**:

1. Inicia la app: `streamlit run app.py`
2. En la sidebar, selecciona **"Google Gemini"** como proveedor
3. Ingresa tu API key cuando se te solicite

### Paso 3: Seleccionar Modelo

En la app verás estos modelos disponibles:

| Modelo | Uso Recomendado | Velocidad | Costo |
|--------|-----------------|-----------|-------|
| **gemini-1.5-flash-8b** | CVs simples, alto volumen | ⚡⚡⚡ | 💰 |
| **gemini-1.5-flash** | Uso general (recomendado) | ⚡⚡ | 💰💰 |
| **gemini-1.5-pro** | CVs complejos, máxima calidad | ⚡ | 💰💰💰 |
| **gemini-2.0-flash-exp** | Experimental, muy rápido | ⚡⚡⚡ | 💰 |

💡 **Recomendación**: Empieza con **gemini-1.5-flash** (equilibrado)

---

## 📊 Comparación con Otros Proveedores

### Análisis de 100 CVs (estimado)

| Proveedor | Modelo | Costo Aprox. | Tiempo |
|-----------|--------|--------------|--------|
| Google Gemini | flash-8b | **$0.10** | 5 min |
| OpenAI | gpt-4.1-nano | **$0.15** | 6 min |
| Google Gemini | flash | **$0.20** | 8 min |
| OpenAI | gpt-4.1-mini | **$0.30** | 9 min |
| OpenAI | gpt-4o-mini | $0.50 | 10 min |
| Google Gemini | pro | $1.50 | 15 min |
| OpenAI | gpt-4.1 | $2.50 | 18 min |
| OpenAI | gpt-4o | $3.00 | 20 min |

**🏆 Ganadores en costo/beneficio**:
- **Más económico**: Gemini 1.5 Flash 8B
- **Equilibrado**: Gemini 1.5 Flash o GPT-4.1-nano
- **Máxima calidad**: GPT-4.1 o Gemini 1.5 Pro

---

## 🔧 Configuración Avanzada

### Usar la misma key para Google Drive

Si ya tienes una API key de Google Cloud, puedes usarla tanto para Gemini como para Google Drive:

```bash
# En .env:
GEMINI_API_KEY=AIzaSy-tu-key-aqui
GOOGLE_API_KEY=AIzaSy-tu-key-aqui  # Misma key
```

### Límites del Tier Gratuito

| Recurso | Límite Gratis |
|---------|---------------|
| Requests/día | 1,500 |
| Requests/minuto | 15 |
| Tokens/minuto | 1M (Flash), 32K (Pro) |

💡 **Tip**: Para procesar muchos CVs, usa **flash-8b** o **flash** para mantenerte en el tier gratuito.

### Habilitar API en Google Cloud

Si ves el error "API not enabled":

1. Ve a: [https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com)
2. Haz clic en **"Enable"**
3. Espera 1-2 minutos y vuelve a intentar

---

## ❓ Troubleshooting

### Error: "API key not valid"

**Causa**: Key incorrecta o API no habilitada.

**Solución**:
1. Verifica que la key empiece con `AIzaSy`
2. Habilita Generative Language API (ver arriba)
3. Asegúrate de no tener espacios extras en `.env`

### Error: "Rate limit exceeded"

**Causa**: Excediste el límite de 15 requests/minuto.

**Solución**:
1. Espera 1 minuto
2. Procesa menos CVs simultáneamente
3. Considera upgradear a tier pago ($0.02/1K requests)

### La app no reconoce GEMINI_API_KEY

**Causa**: Probablemente la key está comentada en `.env`.

**Solución**:
```bash
# Mal:
# GEMINI_API_KEY=AIzaSy...  ← Comentada con #

# Bien:
GEMINI_API_KEY=AIzaSy...  ← Sin #
```

---

## 📚 Recursos Adicionales

- **Google AI Studio**: [https://aistudio.google.com](https://aistudio.google.com)
- **Documentación Gemini**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **Pricing**: [https://ai.google.dev/pricing](https://ai.google.dev/pricing)
- **LiteLLM + Gemini**: [https://docs.litellm.ai/docs/providers/gemini](https://docs.litellm.ai/docs/providers/gemini)

---

## 🎯 Casos de Uso Recomendados

### Para alto volumen (>50 CVs/día)
→ **gemini-1.5-flash-8b** (más económico)

### Para uso general
→ **gemini-1.5-flash** (equilibrado)

### Para CVs técnicos complejos
→ **gemini-1.5-pro** (máxima precisión)

### Para experimentar con lo último
→ **gemini-2.0-flash-exp** (experimental)

---

**¿Dudas?** Consulta [API_KEY_SETUP.md](./API_KEY_SETUP.md) para más información sobre configuración general.
