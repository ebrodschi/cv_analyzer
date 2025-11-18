#!/usr/bin/env python3
"""
Script para estimar tokens y costos de procesamiento de CVs
"""


def estimate_tokens(text):
    """Aproximación: 1 token ≈ 4 caracteres"""
    return len(text) // 4


# System prompt
system_prompt = """Sos un analista de recursos humanos especializado en perfiles técnicos.
Tu tarea es analizar el contenido de UN SOLO CV y devolver un JSON con información estructurada del candidato."""

# User prompt template (aproximado)
user_prompt_template = """Vas a analizar un CV para una posición de: Electricista
Ubicación de la posición: Buenos Aires, Argentina
Radio aceptable: 10 km

Esquema JSON requerido:
{
  "nombre": "string" [REQUERIDO],
  "mail": "string" [opcional, puede ser null],
  "telefono": "string" [opcional, puede ser null],
  "hay_foto_en_cv": true o false [opcional, puede ser null],
  "primaria_completa": true o false [REQUERIDO],
  "secundaria_completa": true o false [REQUERIDO],
  "terciario_completo": true o false [opcional, puede ser null],
  "experiencia_electricista_confirmada": true o false [REQUERIDO],
  "años_experiencia": number (entero) (min=0, max=50) [opcional, puede ser null],
  "edad": number (entero) (min=18, max=80) [opcional, puede ser null],
  "localidad_residencia": "string" [opcional, puede ser null],
  "lugar_residencia_proximo": true o false [opcional, puede ser null],
  "edad_en_rango": true o false [opcional, puede ser null],
  "score_general": number (entero) (min=1, max=10) [REQUERIDO],
  "observaciones": "string" [opcional, puede ser null],
  "stack_tecnologico": ["string", ...] [opcional, puede ser null],
  "idiomas": [{...}, ...] [opcional, puede ser null]
}

Definiciones para campos específicos:
• primaria_completa: true si se menciona finalización de estudios primarios
• secundaria_completa: true si terminó la secundaria (aclarar si es escuela técnica)
• terciario_completo: true si cursó y finalizó una tecnicatura relacionada
• experiencia_electricista_confirmada: true si se menciona trabajo previo con tareas de mantenimiento eléctrico...

score_general: Número del 1 al 10 según los siguientes criterios:

🎯 Criterios para el score (1-10):
Educación relevante (hasta 2 puntos)...
Experiencia (hasta 4 puntos)...
Claridad y presentación del CV (hasta 1 punto)...
Conocimientos técnicos (hasta 2 puntos)...
Ubicación geográfica (hasta 1 punto)...

Instrucciones adicionales:
• Para 'edad': extrae la edad en años si se menciona explícitamente
• Para 'localidad_residencia': extrae la localidad/ciudad donde reside
• Para 'años_experiencia': suma todos los años de experiencia laboral relevante
• Para 'observaciones': escribe un resumen del perfil en MÁXIMO 3 oraciones
• Si no encuentras información para un campo, usa null, false o []

Texto del CV a analizar:
---
[CV_TEXTO_AQUI]
---

Responde SOLO con el JSON, sin explicaciones adicionales."""

# Ejemplo de CV típico (750-1000 palabras)
cv_corto = "A" * 3000  # ~750 palabras

# Ejemplo de CV largo (2000 palabras)
cv_largo = "A" * 8000  # ~2000 palabras (límite del código)

# Output ejemplo
output_example = """{
  "nombre": "Juan Pérez",
  "mail": "juan.perez@email.com",
  "telefono": "+54 11 1234-5678",
  "hay_foto_en_cv": true,
  "primaria_completa": true,
  "secundaria_completa": true,
  "terciario_completo": false,
  "experiencia_electricista_confirmada": true,
  "años_experiencia": 5,
  "edad": 32,
  "localidad_residencia": "Lanús, Buenos Aires",
  "lugar_residencia_proximo": true,
  "edad_en_rango": true,
  "score_general": 8,
  "observaciones": "Candidato con sólida experiencia en mantenimiento industrial. Demuestra proactividad y capacidad de trabajo en equipo. Ha liderado proyectos de automatización.",
  "stack_tecnologico": ["PLC Siemens", "AutoCAD", "Electricidad industrial", "Neumática"],
  "idiomas": [{"idioma": "Español", "nivel": "nativo"}, {"idioma": "Inglés", "nivel": "intermedio"}]
}"""

print("=" * 60)
print("📊 ESTIMACIÓN DE TOKENS POR CV")
print("=" * 60)

# Calcular tokens
system_tokens = estimate_tokens(system_prompt)
template_tokens = estimate_tokens(user_prompt_template)
cv_corto_tokens = estimate_tokens(cv_corto)
cv_largo_tokens = estimate_tokens(cv_largo)
output_tokens = estimate_tokens(output_example)

print("\n🔹 INPUT TOKENS (lo que enviamos al LLM):")
print(f"   - System prompt: ~{system_tokens} tokens")
print(f"   - User prompt (template + schema): ~{template_tokens} tokens")
print(f"   - CV texto (corto, ~750 palabras): ~{cv_corto_tokens} tokens")
print(f"   - CV texto (largo, ~2000 palabras): ~{cv_largo_tokens} tokens")

total_input_corto = system_tokens + template_tokens + cv_corto_tokens
total_input_largo = system_tokens + template_tokens + cv_largo_tokens

print(f"\n   📌 TOTAL INPUT (CV corto): ~{total_input_corto} tokens")
print(f"   📌 TOTAL INPUT (CV largo): ~{total_input_largo} tokens")

print("\n🔹 OUTPUT TOKENS (lo que el LLM responde):")
print(f"   - JSON estructurado: ~{output_tokens} tokens")

print("\n" + "=" * 60)
print("📊 RESUMEN POR CV")
print("=" * 60)
print(f"   INPUT:  {total_input_corto:,} - {total_input_largo:,} tokens")
print(f"   OUTPUT: ~{output_tokens} tokens")
print(
    f"   TOTAL:  ~{total_input_corto + output_tokens:,} - {total_input_largo + output_tokens:,} tokens/CV"
)

# Costos con diferentes proveedores
print("\n" + "=" * 60)
print("💰 COSTOS ESTIMADOS POR PROVEEDOR")
print("=" * 60)

proveedores = {
    "Gemini 1.5 Flash 8B": {"input": 0.04, "output": 0.15},
    "Gemini 1.5 Flash": {"input": 0.075, "output": 0.30},
    "GPT-4.1-nano": {"input": 0.10, "output": 0.40},
    "GPT-4o-mini": {"input": 0.15, "output": 0.60},
    "GPT-4.1-mini": {"input": 0.20, "output": 0.80},
}

# Usar promedio de input tokens
avg_input = (total_input_corto + total_input_largo) // 2

print(f"\nUsando promedio: {avg_input:,} input + {output_tokens} output tokens\n")

for nombre, costos in proveedores.items():
    input_cost_per_1m = costos["input"]
    output_cost_per_1m = costos["output"]

    costo_por_cv = (avg_input / 1_000_000 * input_cost_per_1m) + (
        output_tokens / 1_000_000 * output_cost_per_1m
    )

    print(f"{nombre}:")
    print(f"   • 1 CV:      ${costo_por_cv:.4f}")
    print(f"   • 100 CVs:   ${costo_por_cv * 100:.2f}")
    print(f"   • 1,000 CVs: ${costo_por_cv * 1000:.2f}")
    print()

print("=" * 60)
print("💡 RECOMENDACIONES:")
print("=" * 60)
print("   • Para bajo volumen (<100 CVs): cualquier modelo funciona bien")
print("   • Para volumen medio (100-1000 CVs): Gemini Flash 8B o GPT-4.1-nano")
print("   • Para alto volumen (>1000 CVs): Gemini Flash 8B (más económico)")
print("   • Para máxima calidad: GPT-4o-mini o Gemini 1.5 Flash")
print()
