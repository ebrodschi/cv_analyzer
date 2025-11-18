# 💰 Costos de Procesamiento de CVs

Esta guía detalla los costos estimados de procesamiento de CVs usando diferentes proveedores de LLM.

---

## 📊 Estimación de Tokens por CV

### **INPUT TOKENS** (lo que enviamos al LLM)

Cada análisis de CV envía al modelo:

| Componente | Tokens |
|------------|--------|
| System prompt | ~45 tokens |
| User prompt (template + schema) | ~591 tokens |
| **CV texto (corto, ~750 palabras)** | ~750 tokens |
| **CV texto (largo, ~2000 palabras)** | ~2,000 tokens |

**📌 TOTAL INPUT: 1,386 - 2,636 tokens por CV**

> **Nota**: El límite actual del código es 8,000 caracteres de CV (~2,000 tokens). La mayoría de CVs están en el rango de 750-1,500 palabras.

---

### **OUTPUT TOKENS** (lo que recibimos del LLM)

El JSON estructurado que devuelve el modelo incluye:

- Datos de contacto (nombre, email, teléfono)
- Información educativa (primaria, secundaria, terciario)
- Experiencia laboral (años, confirmación de experiencia)
- Datos demográficos (edad, localidad, proximidad)
- Score general (1-10)
- Observaciones (resumen del perfil)
- Stack tecnológico (lista de habilidades)
- Idiomas (lista con niveles)

**📌 TOTAL OUTPUT: ~201 tokens por CV**

---

### **TOTAL GENERAL**

**~1,587 - 2,837 tokens por CV**

Para cálculos, usamos el promedio: **~2,011 input + 201 output tokens**

---

## 💰 Comparación de Costos por Proveedor

### Tabla de Costos

| Proveedor | Precio Input (por 1M tokens) | Precio Output (por 1M tokens) | 1 CV | 100 CVs | 1,000 CVs |
|-----------|------------------------------|-------------------------------|------|---------|-----------|
| **Gemini 1.5 Flash 8B** ⭐ | $0.04 | $0.15 | $0.0001 | **$0.01** | **$0.11** |
| **Gemini 1.5 Flash** | $0.075 | $0.30 | $0.0002 | $0.02 | $0.21 |
| **GPT-4.1-nano** | $0.10 | $0.40 | $0.0003 | $0.03 | $0.28 |
| **GPT-4o-mini** | $0.15 | $0.60 | $0.0004 | **$0.04** | $0.42 |
| **GPT-4.1-mini** | $0.20 | $0.80 | $0.0006 | $0.06 | $0.56 |
| **Gemini 1.5 Pro** | $1.25 | $5.00 | $0.0035 | $0.35 | $3.51 |
| **GPT-4.1** | $2.00 | $8.00 | $0.0056 | $0.56 | $5.63 |
| **GPT-4o** | $2.50 | $10.00 | $0.0070 | $0.70 | $7.03 |

> **Cálculo**: Costo = (input_tokens / 1M × precio_input) + (output_tokens / 1M × precio_output)

---

## 💡 Recomendaciones por Volumen

### 🔹 **Bajo Volumen (<100 CVs)**

**Cualquier modelo funciona bien** - el costo es insignificante ($0.01 - $0.06)

Recomendación: **GPT-4o-mini** o **Gemini 1.5 Flash**
- Excelente calidad de análisis
- Mejor comprensión de contexto
- Costo total: ~$0.04 para 100 CVs

---

### 🔹 **Volumen Medio (100-1,000 CVs)**

**Equilibrio entre costo y calidad**

Opciones recomendadas:

1. **Gemini 1.5 Flash 8B** (más económico)
   - Costo: $0.11 por 1,000 CVs
   - Velocidad: ⚡⚡⚡ Muy rápido
   - Calidad: ⭐⭐⭐ Buena

2. **GPT-4.1-nano**
   - Costo: $0.28 por 1,000 CVs
   - Velocidad: ⚡⚡⚡ Muy rápido
   - Calidad: ⭐⭐⭐ Buena

3. **Gemini 1.5 Flash** (mejor calidad)
   - Costo: $0.21 por 1,000 CVs
   - Velocidad: ⚡⚡ Rápido
   - Calidad: ⭐⭐⭐⭐ Muy buena

---

### 🔹 **Alto Volumen (>1,000 CVs)**

**Optimización de costos importante**

**Recomendación:** **Gemini 1.5 Flash 8B**
- Costo por 1,000 CVs: **$0.11**
- Costo por 10,000 CVs: **$1.10**
- Costo por 100,000 CVs: **$11.00**

Alternativa de mayor calidad: **Gemini 1.5 Flash** ($0.21 por 1K)

---

### 🔹 **Máxima Calidad (casos especiales)**

Para posiciones críticas o análisis detallados:

1. **GPT-4o-mini**: $0.42 por 1,000 CVs
   - Mejor comprensión de matices
   - Análisis más profundo
   - Observaciones más elaboradas

2. **Gemini 1.5 Flash**: $0.21 por 1,000 CVs
   - Excelente relación calidad/precio
   - Muy buena comprensión de contexto
   - Respuestas consistentes

3. **Gemini 1.5 Pro**: $3.51 por 1,000 CVs
   - Máxima capacidad de razonamiento
   - Análisis muy detallado
   - Para casos donde el costo no es factor

4. **GPT-4.1** o **GPT-4o**: $5.63 - $7.03 por 1,000 CVs
   - Los modelos más avanzados
   - Solo para casos muy específicos
   - Generalmente innecesario para CVs

---

## 📈 Ejemplos de Escenarios Reales

### Escenario 1: Startup pequeña
- **Volumen**: 50 CVs/mes
- **Modelo recomendado**: GPT-4o-mini
- **Costo mensual**: $0.02
- **Costo anual**: $0.24

### Escenario 2: Empresa mediana
- **Volumen**: 500 CVs/mes
- **Modelo recomendado**: Gemini 1.5 Flash
- **Costo mensual**: $0.11
- **Costo anual**: $1.26

### Escenario 3: Agencia de RRHH
- **Volumen**: 5,000 CVs/mes
- **Modelo recomendado**: Gemini 1.5 Flash 8B
- **Costo mensual**: $0.55
- **Costo anual**: $6.60

### Escenario 4: Plataforma de empleo
- **Volumen**: 50,000 CVs/mes
- **Modelo recomendado**: Gemini 1.5 Flash 8B
- **Costo mensual**: $5.50
- **Costo anual**: $66.00

---

## 🎯 Estrategia Híbrida

Para optimizar costos y calidad, puedes usar una **estrategia de dos niveles**:

### Nivel 1: Filtrado inicial (80% de CVs)
- **Modelo**: Gemini 1.5 Flash 8B (más económico)
- **Objetivo**: Identificar candidatos viables rápidamente
- **Costo**: $0.11 por 1,000 CVs

### Nivel 2: Análisis profundo (20% top candidates)
- **Modelo**: GPT-4o-mini o Gemini 1.5 Flash (mayor calidad)
- **Objetivo**: Evaluación detallada de mejores candidatos
- **Costo**: $0.08 por 200 CVs

**Costo total híbrido**: $0.19 por 1,000 CVs (vs $0.42 usando solo GPT-4o-mini)

**Ahorro**: 55% con mejor eficiencia

---

## 🔧 Cómo Calcular tus Costos

### Fórmula Simple

```
Costo Total = (Número de CVs) × (Costo por CV del proveedor)
```

### Calculadora Rápida

1. **Estima tu volumen mensual de CVs**: ______
2. **Elige un proveedor de la tabla arriba**
3. **Multiplica**: volumen × costo_por_cv × 1000

**Ejemplo**:
- Volumen: 200 CVs/mes
- Proveedor: Gemini 1.5 Flash ($0.21 por 1,000)
- Cálculo: 200 × ($0.21 / 1000) = **$0.042/mes**

---

## 📊 Comparación con Soluciones Alternativas

### vs. Análisis Manual
- **Analista humano**: $20-50/hora
- **Tiempo por CV**: 10-15 minutos
- **Costo por CV**: $3-12
- **100 CVs**: $300-1,200

**Con LLM (Gemini Flash 8B)**: $0.01 para 100 CVs
**Ahorro**: 99.99%

### vs. Otros servicios de parsing
- **HireAbility**: ~$0.50/CV
- **Sovren**: ~$0.30/CV
- **Textkernel**: ~$0.40/CV

**Con esta solución**: $0.0001-0.0006/CV
**Ahorro**: 99.8%+

---

## 💳 Límites y Cuotas Gratuitas

### OpenAI
- **Sin tier gratuito permanente**
- Tier 1: $5 de crédito para nuevos usuarios (expira en 3 meses)
- Límite: 500,000 tokens/min (Tier 1)

### Google Gemini
- **Free tier**: 15 requests/min, 1M tokens/min
- **Ideal para**: hasta ~30,000 CVs/mes gratis
- Sin tarjeta de crédito requerida inicialmente

### Anthropic (Claude)
- **Sin tier gratuito**
- Requiere tarjeta de crédito desde el inicio

---

## 🚀 Recomendación Final

Para la mayoría de casos de uso:

1. **Empieza con Gemini 1.5 Flash 8B** (gratis hasta 30K CVs/mes)
2. Si necesitas mejor calidad: **GPT-4o-mini** (~$0.04 por 100 CVs)
3. Para volumen alto y costos mínimos: sigue con **Gemini Flash 8B**

**El costo NO debería ser un factor limitante** - procesar CVs con LLMs es extremadamente económico comparado con cualquier alternativa.

---

## 📚 Recursos Adicionales

- [Calculadora de Tokens en línea](https://platform.openai.com/tokenizer)
- [Pricing de OpenAI](https://openai.com/pricing)
- [Pricing de Google Gemini](https://ai.google.dev/pricing)
- [Pricing de Anthropic](https://www.anthropic.com/pricing)

---

**Última actualización**: Octubre 2025

> **Nota**: Los precios pueden cambiar. Verifica siempre los precios actuales en los sitios oficiales de cada proveedor.
