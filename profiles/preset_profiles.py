"""
Perfiles de reclutamiento predefinidos.

Incluye perfiles para: Industrial (4), IT (10), Kiosko (3), General (1).
"""

from profiles.profile_model import (
    ExtraField,
    PositionConfig,
    RecruiterProfile,
    TechStackConfig,
)

# =============================================================================
# Scoring criteria reutilizables
# =============================================================================

INDUSTRIAL_SCORE_CRITERIA = """Criterios para el score (1-10):

Educación relevante (hasta 2 puntos):
• +1 si culminó el secundario
• +1 si el secundario es técnico

Experiencia (hasta 4 puntos):
• +1 si tiene más de 2 años
• +1 si tiene más de 3 años
• +1 si trabajó en fábricas industriales y rubros afines
• +1 si tuvo responsabilidades específicas o lideró tareas

Claridad y presentación del CV (hasta 1 punto):
• 1 punto si está bien organizado, con fechas y descripciones claras

Conocimientos técnicos (hasta 2 puntos):
• Presencia de conocimientos relevantes para la posición

Ubicación geográfica (hasta 1 punto):
• +1 si reside en la zona objetivo o radio cercano

Penalizaciones:
• -2 puntos si el candidato tiene 2 o más oficios NO relacionados"""

IT_SCORE_CRITERIA = """Criterios para el score (1-10):

Stack tecnológico (hasta 4 puntos):
• +1 por cada tecnología requerida que domina (hasta 4)
• Si domina más de 4 tecnologías requeridas, igual se asignan 4 puntos

Experiencia (hasta 3 puntos):
• +1 si tiene más de 1 año de experiencia relevante
• +1 si tiene más de 3 años de experiencia relevante
• +1 si trabajó en empresas de tecnología o en roles similares

Educación (hasta 1 punto):
• +1 si tiene título universitario o terciario en sistemas/informática/ingeniería

Idioma inglés (hasta 1 punto):
• +1 si tiene nivel intermedio o superior de inglés

Claridad y presentación del CV (hasta 1 punto):
• 1 punto si está bien organizado, con fechas y descripciones claras"""

KIOSKO_SCORE_CRITERIA = """Criterios para el score (1-10):

Experiencia en el rubro (hasta 4 puntos):
• +1 si tiene experiencia en atención al público
• +1 si tiene más de 1 año de experiencia en comercio/retail
• +1 si tiene más de 2 años de experiencia relevante
• +1 si tuvo responsabilidades o cargo de confianza

Educación (hasta 2 puntos):
• +1 si culminó el secundario
• +1 si tiene estudios terciarios o universitarios

Habilidades relevantes (hasta 2 puntos):
• +1 si maneja herramientas informáticas básicas (Excel, sistemas de caja, etc.)
• +1 si tiene habilidades de comunicación o liderazgo evidentes

Ubicación geográfica (hasta 1 punto):
• +1 si reside en la zona objetivo o radio cercano

Disponibilidad y presentación (hasta 1 punto):
• +1 si el CV está bien presentado y muestra disponibilidad"""

# =============================================================================
# Perfiles Industriales
# =============================================================================

ELECTRICISTA = RecruiterProfile(
    id="electricista",
    name="Electricista de Mantenimiento Industrial",
    category="industrial",
    position=PositionConfig(
        titulo="Electricista de Mantenimiento Industrial",
        experiencia_campo="experiencia_electricista_confirmada",
        descripcion_experiencia="trabajo previo con tareas de mantenimiento eléctrico, electricidad industrial, electrónica industrial",
        exclusiones="electricidad de obra de construcción",
        rango_edad="25-45",
        conocimientos_relevantes="PLC, electricidad industrial, neumática, electrónica",
        industrias_relevantes="fábricas industriales y rubros afines alimenticio",
    ),
    scoring_criteria=INDUSTRIAL_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_electricista_confirmada",
        "hay_foto_en_cv",
        "secundaria_tecnica",
    ],
)

ELECTROMECANICO = RecruiterProfile(
    id="electromecanico",
    name="Electromecánico de Mantenimiento Industrial",
    category="industrial",
    position=PositionConfig(
        titulo="Electromecánico de Mantenimiento Industrial",
        experiencia_campo="experiencia_electromecanico_confirmada",
        descripcion_experiencia="trabajo previo con tareas de mantenimiento electromecánico industrial",
        exclusiones="electricidad de obra de construcción",
        rango_edad="25-45",
        conocimientos_relevantes="PLC, electricidad industrial, neumática, electromecánica",
        industrias_relevantes="fábricas industriales y rubros afines alimenticio",
    ),
    scoring_criteria=INDUSTRIAL_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_electromecanico_confirmada",
        "hay_foto_en_cv",
        "secundaria_tecnica",
    ],
)

MECANICO = RecruiterProfile(
    id="mecanico",
    name="Mecánico Industrial",
    category="industrial",
    position=PositionConfig(
        titulo="Mecánico Industrial",
        experiencia_campo="experiencia_mecanico_industrial_confirmada",
        descripcion_experiencia="trabajo previo con tareas de mantenimiento mecánico, soldador industrial",
        exclusiones="mecánico de obra de construcción",
        rango_edad="25-45",
        conocimientos_relevantes="soldadura de caños pequeñas medidas, soldaduras piping",
        industrias_relevantes="fábricas industriales",
    ),
    scoring_criteria=INDUSTRIAL_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_mecanico_industrial_confirmada",
        "hay_foto_en_cv",
        "secundaria_tecnica",
    ],
)

PANOLERO = RecruiterProfile(
    id="panolero",
    name="Pañolero Industrial",
    category="industrial",
    position=PositionConfig(
        titulo="Pañolero Industrial",
        experiencia_campo="experiencia_pañol_depositos_confirmada",
        descripcion_experiencia="trabajo previo con tareas de pañol industrial, depósitos",
        exclusiones="ninguna",
        rango_edad="25-50",
        conocimientos_relevantes="PLC, electricidad industrial, neumática, electrónica, hidráulica",
        industrias_relevantes="fábricas industriales y rubros afines alimenticio",
    ),
    scoring_criteria=INDUSTRIAL_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_pañol_depositos_confirmada",
        "hay_foto_en_cv",
        "secundaria_tecnica",
    ],
)

# =============================================================================
# Perfiles IT
# =============================================================================

IT_FULLSTACK = RecruiterProfile(
    id="it_fullstack",
    name="IT - Full Stack Developer",
    category="it",
    position=PositionConfig(
        titulo="Full Stack Developer",
        experiencia_campo="experiencia_desarrollo_confirmada",
        descripcion_experiencia="desarrollo web full stack con frameworks frontend y backend, APIs REST, bases de datos",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="React, Angular, Vue, Node.js, Python, Java, SQL, NoSQL, Docker, Git",
        industrias_relevantes="tecnología, fintech, startups, software houses, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["JavaScript", "React", "Node.js", "SQL"],
        preferred=["TypeScript", "Docker", "AWS", "MongoDB", "Git"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_desarrollo_confirmada"],
)

IT_FRONTEND = RecruiterProfile(
    id="it_frontend",
    name="IT - Frontend Developer",
    category="it",
    position=PositionConfig(
        titulo="Frontend Developer",
        experiencia_campo="experiencia_desarrollo_confirmada",
        descripcion_experiencia="desarrollo de interfaces web con frameworks modernos, maquetado, UX/UI",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="React, Angular, Vue, HTML, CSS, JavaScript, TypeScript, responsive design",
        industrias_relevantes="tecnología, fintech, startups, software houses, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["JavaScript", "React", "HTML", "CSS"],
        preferred=["TypeScript", "Next.js", "Tailwind", "Figma", "Git"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_desarrollo_confirmada"],
)

IT_BACKEND = RecruiterProfile(
    id="it_backend",
    name="IT - Backend Developer",
    category="it",
    position=PositionConfig(
        titulo="Backend Developer",
        experiencia_campo="experiencia_desarrollo_confirmada",
        descripcion_experiencia="desarrollo de APIs, microservicios, lógica de negocio, bases de datos",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="Python, Java, Node.js, Go, SQL, NoSQL, APIs REST, microservicios",
        industrias_relevantes="tecnología, fintech, startups, software houses, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["Python", "SQL", "APIs REST"],
        preferred=["Java", "Docker", "AWS", "PostgreSQL", "Redis", "Git"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_desarrollo_confirmada"],
)

IT_DATA_ENGINEER = RecruiterProfile(
    id="it_data_engineer",
    name="IT - Data Engineer",
    category="it",
    position=PositionConfig(
        titulo="Data Engineer",
        experiencia_campo="experiencia_datos_confirmada",
        descripcion_experiencia="diseño y mantenimiento de pipelines de datos, ETL/ELT, data warehousing, procesamiento batch y streaming",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="Python, SQL, Spark, Airflow, dbt, data warehousing, ETL, cloud platforms",
        industrias_relevantes="tecnología, fintech, bancos, retail, telecomunicaciones",
    ),
    tech_stack=TechStackConfig(
        required=["Python", "SQL", "ETL/ELT"],
        preferred=["Spark", "Airflow", "dbt", "AWS", "GCP", "Kafka", "Docker"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_datos_confirmada"],
)

IT_DATA_SCIENTIST = RecruiterProfile(
    id="it_data_scientist",
    name="IT - Data Scientist",
    category="it",
    position=PositionConfig(
        titulo="Data Scientist",
        experiencia_campo="experiencia_datos_confirmada",
        descripcion_experiencia="análisis estadístico, machine learning, modelos predictivos, experimentación A/B",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="Python, R, machine learning, estadística, deep learning, NLP, SQL",
        industrias_relevantes="tecnología, fintech, bancos, retail, salud, telecomunicaciones",
    ),
    tech_stack=TechStackConfig(
        required=["Python", "Machine Learning", "SQL", "Estadística"],
        preferred=["TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "Jupyter", "R"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_datos_confirmada"],
)

IT_DATA_ANALYST = RecruiterProfile(
    id="it_data_analyst",
    name="IT - Data Analyst",
    category="it",
    position=PositionConfig(
        titulo="Data Analyst",
        experiencia_campo="experiencia_datos_confirmada",
        descripcion_experiencia="análisis de datos, reportes, dashboards, visualización de datos, SQL",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="SQL, Excel, Power BI, Tableau, Python, Google Analytics, estadística básica",
        industrias_relevantes="cualquier industria con necesidades de análisis de datos",
    ),
    tech_stack=TechStackConfig(
        required=["SQL", "Excel", "Power BI"],
        preferred=["Python", "Tableau", "Google Analytics", "Looker", "dbt"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_datos_confirmada"],
)

IT_QA = RecruiterProfile(
    id="it_qa",
    name="IT - QA Engineer",
    category="it",
    position=PositionConfig(
        titulo="QA Engineer",
        experiencia_campo="experiencia_qa_confirmada",
        descripcion_experiencia="testing manual y/o automatizado, aseguramiento de calidad de software, test plans",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="testing manual, automation, Selenium, Cypress, Postman, CI/CD, metodologías ágiles",
        industrias_relevantes="tecnología, fintech, startups, software houses, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["Testing Manual", "Selenium", "Postman"],
        preferred=["Cypress", "Python", "JavaScript", "CI/CD", "Jira", "Git"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_qa_confirmada"],
)

IT_SOLUTION_ARCHITECT = RecruiterProfile(
    id="it_solution_architect",
    name="IT - Solution Architect",
    category="it",
    position=PositionConfig(
        titulo="Solution Architect",
        experiencia_campo="experiencia_arquitectura_confirmada",
        descripcion_experiencia="diseño de arquitecturas de software, integraciones, liderazgo técnico, toma de decisiones de stack",
        exclusiones="",
        rango_edad="28-55",
        conocimientos_relevantes="microservicios, cloud architecture, APIs, system design, liderazgo técnico",
        industrias_relevantes="tecnología, fintech, bancos, grandes empresas, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["Cloud (AWS/GCP/Azure)", "Microservicios", "APIs REST", "System Design"],
        preferred=["Docker", "Kubernetes", "Terraform", "CI/CD", "Event-driven architecture"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_arquitectura_confirmada"],
)

IT_DEVOPS = RecruiterProfile(
    id="it_devops",
    name="IT - DevOps Engineer",
    category="it",
    position=PositionConfig(
        titulo="DevOps Engineer",
        experiencia_campo="experiencia_devops_confirmada",
        descripcion_experiencia="CI/CD, automatización de infraestructura, contenedores, orquestación, monitoreo",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="Docker, Kubernetes, CI/CD, Terraform, Linux, scripting, monitoreo",
        industrias_relevantes="tecnología, fintech, startups, software houses, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["Docker", "CI/CD", "Linux", "Git"],
        preferred=["Kubernetes", "Terraform", "AWS", "Jenkins", "GitHub Actions", "Ansible"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_devops_confirmada"],
)

IT_CLOUD_ENGINEER = RecruiterProfile(
    id="it_cloud_engineer",
    name="IT - Cloud Engineer",
    category="it",
    position=PositionConfig(
        titulo="Cloud Engineer",
        experiencia_campo="experiencia_cloud_confirmada",
        descripcion_experiencia="diseño e implementación de infraestructura cloud, migraciones, optimización de costos cloud",
        exclusiones="",
        rango_edad="22-45",
        conocimientos_relevantes="AWS, GCP, Azure, Terraform, networking, seguridad cloud, serverless",
        industrias_relevantes="tecnología, fintech, bancos, grandes empresas, consultoras IT",
    ),
    tech_stack=TechStackConfig(
        required=["AWS", "Terraform", "Linux"],
        preferred=["GCP", "Azure", "Kubernetes", "Docker", "Python", "Networking"],
    ),
    scoring_criteria=IT_SCORE_CRITERIA,
    preaprobado_conditions=["experiencia_cloud_confirmada"],
)

# =============================================================================
# Perfiles Kiosko
# =============================================================================

KIOSKO_ENCARGADO = RecruiterProfile(
    id="kiosko_encargado",
    name="Encargado de Local",
    category="kiosko",
    position=PositionConfig(
        titulo="Encargado de Local / Sucursal",
        experiencia_campo="experiencia_encargado_confirmada",
        descripcion_experiencia="gestión de local, manejo de personal, control de stock, atención al cliente, apertura y cierre",
        exclusiones="",
        rango_edad="25-50",
        conocimientos_relevantes="liderazgo, manejo de caja, control de stock, atención al cliente, Excel básico",
        industrias_relevantes="comercio, retail, gastronomía, kioscos, franquicias",
    ),
    scoring_criteria=KIOSKO_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_encargado_confirmada",
        "secundaria_completa",
    ],
)

KIOSKO_ADMINISTRATIVO = RecruiterProfile(
    id="kiosko_administrativo",
    name="Administrativo",
    category="kiosko",
    position=PositionConfig(
        titulo="Administrativo / Asistente Administrativo",
        experiencia_campo="experiencia_administrativa_confirmada",
        descripcion_experiencia="tareas administrativas, facturación, atención telefónica, manejo de archivos, correspondencia",
        exclusiones="",
        rango_edad="22-50",
        conocimientos_relevantes="Excel, Word, facturación, atención al cliente, organización, sistemas administrativos",
        industrias_relevantes="comercio, servicios, estudios contables, pymes, oficinas",
    ),
    scoring_criteria=KIOSKO_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_administrativa_confirmada",
        "secundaria_completa",
    ],
)

KIOSKO_CAJERO = RecruiterProfile(
    id="kiosko_cajero",
    name="Cajero/a",
    category="kiosko",
    position=PositionConfig(
        titulo="Cajero/a",
        experiencia_campo="experiencia_cajero_confirmada",
        descripcion_experiencia="manejo de caja, cobros, atención al cliente, arqueo de caja, medios de pago",
        exclusiones="",
        rango_edad="18-45",
        conocimientos_relevantes="manejo de caja, atención al cliente, medios de pago, matemática básica",
        industrias_relevantes="supermercados, comercio, retail, gastronomía, kioscos",
    ),
    scoring_criteria=KIOSKO_SCORE_CRITERIA,
    preaprobado_conditions=[
        "edad_en_rango",
        "experiencia_cajero_confirmada",
        "secundaria_completa",
    ],
)

# =============================================================================
# Perfil General
# =============================================================================

GENERAL = RecruiterProfile(
    id="general",
    name="Perfil General",
    category="general",
    position=PositionConfig(
        titulo="Perfil General",
        experiencia_campo="experiencia_confirmada",
        descripcion_experiencia="experiencia laboral relevante para la posición",
        exclusiones="",
        rango_edad="18-65",
        conocimientos_relevantes="",
        industrias_relevantes="",
    ),
    scoring_criteria="""Criterios para el score (1-10):

Experiencia relevante (hasta 4 puntos):
• +1 por cada año de experiencia relevante (hasta 4)

Educación (hasta 2 puntos):
• +1 si culminó el secundario
• +1 si tiene estudios terciarios o universitarios

Habilidades y conocimientos (hasta 2 puntos):
• Presencia de habilidades relevantes para la posición

Ubicación geográfica (hasta 1 punto):
• +1 si reside en la zona objetivo o radio cercano

Presentación del CV (hasta 1 punto):
• +1 si está bien organizado y es claro""",
    preaprobado_conditions=["experiencia_confirmada"],
)

# =============================================================================
# Registro de todos los presets
# =============================================================================

ALL_PRESETS = [
    # Industrial
    ELECTRICISTA,
    ELECTROMECANICO,
    MECANICO,
    PANOLERO,
    # IT
    IT_FULLSTACK,
    IT_FRONTEND,
    IT_BACKEND,
    IT_DATA_ENGINEER,
    IT_DATA_SCIENTIST,
    IT_DATA_ANALYST,
    IT_QA,
    IT_SOLUTION_ARCHITECT,
    IT_DEVOPS,
    IT_CLOUD_ENGINEER,
    # Kiosko
    KIOSKO_ENCARGADO,
    KIOSKO_ADMINISTRATIVO,
    KIOSKO_CAJERO,
    # General
    GENERAL,
]

PRESETS_BY_ID = {p.id: p for p in ALL_PRESETS}

PRESETS_BY_CATEGORY = {
    "industrial": [ELECTRICISTA, ELECTROMECANICO, MECANICO, PANOLERO],
    "it": [
        IT_FULLSTACK,
        IT_FRONTEND,
        IT_BACKEND,
        IT_DATA_ENGINEER,
        IT_DATA_SCIENTIST,
        IT_DATA_ANALYST,
        IT_QA,
        IT_SOLUTION_ARCHITECT,
        IT_DEVOPS,
        IT_CLOUD_ENGINEER,
    ],
    "kiosko": [KIOSKO_ENCARGADO, KIOSKO_ADMINISTRATIVO, KIOSKO_CAJERO],
    "general": [GENERAL],
}

CATEGORY_LABELS = {
    "industrial": "🏭 Industrial",
    "it": "💻 IT",
    "kiosko": "🏪 Kiosko / Comercio",
    "general": "📋 General",
}
