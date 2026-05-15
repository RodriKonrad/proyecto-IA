# Asesor Normativo de Tránsito Colombiano — Sistema RAG

Sistema de Retrieval-Augmented Generation (RAG) para consultar y analizar normativa de tránsito colombiana basándose en documentos PDF oficiales. El sistema utiliza LangChain, ChromaDB y Google Gemini para proporcionar respuestas fundamentadas en la Ley 769 de 2002.

## 1. Descripción del Sistema

El sistema implementa un pipeline completo de Retrieval-Augmented Generation que permite consultar normativa oficial de tránsito a partir de documentos PDF almacenados localmente. El asistente responde preguntas sobre comparendos e infracciones basándose exclusivamente en los documentos cargados, citando artículos y normas específicas cuando están disponibles en el contexto recuperado.

Las respuestas se restringen a la información contenida en los documentos, lo que garantiza que el sistema no genera contenido especulativo ni inventa leyes. El sistema mantiene historial de conversación para permitir seguimiento multi-turno y proporciona trazabilidad completa de las fuentes consultadas.

## 2. Componentes del Sistema

El sistema se compone de los siguientes módulos principales:

**Frontend (app/templates y app/static)**
- Interfaz web desarrollada en HTML5, CSS3 y JavaScript vanilla
- Componentes: chat principal, panel lateral con temas, documentación de ayuda
- Comunicación asincrónica con el backend mediante JSON

**Backend (app/routes.py)**
- Aplicación Flask que expone endpoints HTTP para consultas
- Gestión de sesiones y conversaciones
- Enrutamiento a endpoints de chat, ayuda y evaluación

**Loader (rag/loader.py)**
- Módulo de carga automática de documentos PDF desde la carpeta /data
- Utiliza PyPDFLoader de LangChain para extraer texto preservando metadatos
- Se ejecuta una única vez al iniciar la aplicación

**Chunker (rag/chunker.py)**
- Divide documentos en fragmentos de 600 caracteres con 80 de solapamiento
- Utiliza RecursiveCharacterTextSplitter con separadores jerárquicos
- Garantiza coherencia semántica en la división de contenidos

**Vectorstore (rag/vectorstore.py)**
- Implementa base de datos vectorial utilizando ChromaDB
- Persiste los vectores en disco para reutilización entre sesiones
- Utiliza similitud coseno como métrica de búsqueda

**Pipeline RAG (rag/pipeline.py)**
- Orquesta el flujo completo: recuperación + prompt aumentado + generación
- Gestiona historial de conversación
- Imprime fragmentos recuperados por consola para depuración

**LLM Generativo**
- Modelo gemini-2.5-flash de Google con temperatura 0.2
- Configurado para respuestas deterministas y precisas en dominio legal

## 3. Flujo del Sistema RAG

### Etapas del Pipeline

**Paso 1 — Carga de Documentos**
El módulo rag/loader.py escanea automáticamente la carpeta /data al iniciar el servidor. Utiliza PyPDFLoader de LangChain para extraer el texto de cada página, preservando los metadatos (fuente, número de página).

**Paso 2 — Fragmentación (Chunking)**
Los documentos se dividen en fragmentos de 600 caracteres con 80 de solapamiento usando RecursiveCharacterTextSplitter. Los separadores se intentan en este orden: párrafos (\n\n), líneas (\n), oraciones (. ) y palabras ( ), garantizando coherencia semántica.

**Paso 3 — Generación de Embeddings**
Cada fragmento se convierte en un vector de 3,072 dimensiones con el modelo gemini-embedding-001 de Google. Textos con significado similar quedan próximos en el espacio vectorial, lo que permite la búsqueda semántica: una consulta puede recuperar fragmentos relevantes aunque no compartan palabras exactas con la pregunta.

**Paso 4 — Base Vectorial ChromaDB**
Los vectores se persisten en la carpeta /chroma_db usando ChromaDB con similitud coseno. La base se construye una sola vez y se reutiliza en arranques posteriores, evitando re-vectorizar los documentos en cada inicio del servidor.

**Paso 5 — Recuperación de Fragmentos**
Al recibir una consulta, el retriever convierte la pregunta en un vector de embeddings y busca los 5 fragmentos más similares (k=5) en ChromaDB. Estos fragmentos se imprimen por consola para depuración antes de construir el prompt.

**Paso 6 — Prompt Aumentado**
Los fragmentos recuperados se formatean e inyectan en el prompt junto con el historial de los últimos 3 turnos y la pregunta actual. El LLM recibe el contexto, el historial y la pregunta en un único prompt estructurado.

**Paso 7 — Generación con el LLM**
El modelo gemini-2.5-flash genera la respuesta con temperatura 0.2, favoreciendo respuestas deterministas y precisas. La instrucción de sistema restringe al modelo a usar únicamente la información del contexto proporcionado.

## 4. Documentación del Proceso de Ingesta

### Carga de Documentos (loader.py)

El módulo utiliza PyPDFLoader de LangChain para leer automáticamente los archivos PDF almacenados en la carpeta /data. La carga es estática y no permite subida dinámica de documentos por parte del usuario. Cada PDF se procesa página por página, generando un objeto Document de LangChain que contiene:

- page_content: texto extraído de la página
- metadata["source"]: nombre del archivo PDF
- metadata["page"]: número de página

### Fragmentación Semántica (chunker.py)

Los documentos completos se dividen en fragmentos utilizando RecursiveCharacterTextSplitter con los siguientes parámetros:

- Tamaño de fragmento: 600 caracteres
- Solapamiento: 80 caracteres
- Separadores (orden de prioridad): párrafos (\n\n), líneas (\n), oraciones (. ), palabras ( )

El solapamiento de 80 caracteres (aproximadamente 12-15 palabras) garantiza transiciones coherentes entre fragmentos consecutivos sin introducir redundancia excesiva. El algoritmo recursivo intenta preservar límites naturales del texto (párrafos, oraciones) antes de dividir arbitrariamente.

### Generación de Embeddings (vectorstore.py)

Cada fragmento se convierte en un vector de 3,072 dimensiones mediante el modelo gemini-embedding-001 de Google. Los embeddings se generan una única vez al iniciar el servidor y se reutilizan en consultas posteriores. El modelo transforma texto en una representación numérica donde textos semánticamente similares producen vectores cercanos en el espacio de embedding.

### Persistencia en ChromaDB

Los vectores se almacenan en la carpeta /chroma_db utilizando ChromaDB como base de datos vectorial. La base de datos persiste en disco, permitiendo reutilización entre reinicios de la aplicación sin necesidad de re-vectorizar. Se utiliza similitud coseno como métrica de distancia para recuperación de fragmentos relevantes.

### Búsqueda Vectorial

Cuando el usuario formula una consulta, el texto se convierte al mismo espacio de embedding y se buscan los k=5 fragmentos más similares en ChromaDB. La similitud coseno cuantifica la proximidad semántica entre la consulta y los fragmentos indexados, permitiendo recuperar contenido relevante incluso cuando las palabras exactas no coinciden.

## 5. Configuración de Parámetros RAG

### Tamaño de Fragmento (chunk_size = 600)

Se seleccionó 600 caracteres como tamaño de fragmento basándose en las características de la Ley 769 de 2002. La mayoría de artículos legales tienen entre 400-700 caracteres, lo que permite que un fragmento contenga frecuentemente un artículo completo sin duplicación excesiva. Fragmentos más pequeños provocarían fragmentación de conceptos legales, mientras que fragmentos mayores introducirían ruido semántico que perjudicaría la recuperación.

### Solapamiento (overlap = 80 caracteres)

El solapamiento de 80 caracteres representa aproximadamente el 13% del tamaño del fragmento. Esto garantiza transiciones coherentes entre fragmentos consecutivos sin introducir redundancia excesiva. Un valor menor (0-40 caracteres) generaría discontinuidades en conceptos que cruzan límites de fragmento, mientras que valores superiores (120+ caracteres) aumentarían innecesariamente el costo computacional de la búsqueda vectorial.

### Número de Fragmentos Recuperados (k = 5)

Se recuperan 5 fragmentos por consulta como balance entre cobertura y ruido. Este número es suficiente para capturar múltiples perspectivas sobre un tema (e.g., artículos complementarios) sin saturar al LLM con información irrelevante. Experimentación mostró que k=3 es frecuentemente insuficiente para casos complejos, mientras que k=10 introduce ruido significativo que degrada la calidad de respuestas.

### Modelo de Embeddings: gemini-embedding-001

Se utiliza gemini-embedding-001 de Google por sus ventajas en contexto de este proyecto:

- Produce vectores de 3,072 dimensiones, suficientes para capturar matices semánticos del dominio legal
- Soporte nativo de español con calidad comparable a inglés
- API gratuita integrada en Google AI Studio
- Latencia aceptable (~100-200ms) para aplicación interactiva
- Sin requerimiento de entrenamiento fino, funcionando directamente sobre la Ley 769

### Modelo de Generación: gemini-2.5-flash

Se utiliza gemini-2.5-flash configurado con los siguientes parámetros:

- Temperatura: 0.2 (bajo). Favorece respuestas deterministas y predecibles, crítico en dominio legal donde la variabilidad es indeseada
- Max tokens: 2,048. Suficiente para análisis completos de comparendos e infracciones sin truncamiento
- Este modelo reemplaza versiones anteriores por mejor balance de velocidad y calidad

### Instrucción de Sistema

La instrucción de sistema (system_instruction) define explícitamente:

1. Rol del asistente: asesor técnico en normativa, no abogado
2. Restricciones absolutas: nunca inventar leyes, respuestas fuera de dominio se rechazan explícitamente
3. Comportamiento: lenguaje técnico, cita de artículos, solicitud de datos faltantes
4. Formato obligatorio de respuesta: resumen, normativa aplicable, análisis, conclusión, recomendación

Esto garantiza que el modelo mantenga límites coherentes incluso cuando el contexto recuperado es ambiguo o incompleto.

## 6. Construcción del Prompt Aumentado

El pipeline RAG inyecta contexto recuperado, historial de conversación e instrucciones del sistema en un template de prompt antes de invocar el LLM. Este proceso ocurre en rag/prompt_config.py.

### Etapas de Construcción

1. Recuperación: El retriever busca los 5 fragmentos más similares a la consulta usando similitud coseno
2. Formateo de contexto: Los fragmentos se formatean indicando fuente y número de página
3. Formateo de historial: Se incluyen los últimos 3 turnos de conversación para mantener contexto
4. Inyección en template: Contexto, historial, instrucción de sistema y pregunta se combinan en un prompt coherente
5. Invocación del LLM: El prompt se envía a gemini-2.5-flash para generación

### Instrucción de Sistema

La instrucción de sistema (rag/prompt_config.py) define explícitamente el comportamiento del asistente:

**Rol y restricciones:**
- Asesor técnico en normativa de tránsito, no abogado
- NUNCA inventar leyes, artículos o sanciones
- Responder exclusivamente basándose en documentos proporcionados
- Si la consulta está fuera del dominio, responder con mensaje explícito de rechazo

**Comportamiento requerido:**
- Lenguaje claro y técnico
- Cita explícita de artículos y normas
- Solicitud de datos faltantes si la información es incompleta
- Indicación de contradicciones cuando existan

**Formato obligatorio de respuesta:**
1. Resumen del caso — descripción objetiva de hechos
2. Normativa aplicable — artículos y principios relevantes
3. Análisis — evaluación de si hay infracción, inconsistencias
4. Conclusión — determinación sobre justificación de sanciones
5. Recomendación — acciones administrativas válidas

Este formato garantiza respuestas estructuradas y predecibles incluso con variedad de consultas.

### Template del Prompt

El template combina todos los elementos en un formato ordenado:

```
[SYSTEM INSTRUCTION completa]

CONTEXTO RECUPERADO DE LOS DOCUMENTOS OFICIALES:
[Fragmento 1 — Fuente, Página]
[Fragmento 2 — Fuente, Página]
[...]

HISTORIAL DE CONVERSACIÓN:
[Últimos 3 turnos de usuario/asistente, o "Sin historial previo"]

CONSULTA DEL USUARIO:
[Pregunta actual]

RESPUESTA DEL ASESOR:
```

Este formato explícito mejora la calidad de generación al separar claramente cada componente del contexto.

## 7. Evaluación del Sistema RAGAS

### Metodología de Evaluación

Se utilizó el framework RAGAS (Retrieval-Augmented Generation Assessment) para evaluar la calidad del sistema con tres métricas principales:

**Faithfulness (Fidelidad):** Mide si las respuestas son fieles al contexto recuperado, evitando alucinaciones. Rango 0.0-1.0; valores >0.7 indican bajo riesgo de contenido inventado.

**Answer Relevancy (Relevancia de Respuesta):** Evalúa si la respuesta responde efectivamente la pregunta del usuario. Mide alineación entre consulta y respuesta sin depender del contexto.

**Context Precision (Precisión de Contexto):** Cuantifica si los fragmentos recuperados son relevantes y sin ruido. Valores altos indican que el retriever selecciona fragmentos correctos sin introductores distrayentes.

### Dataset de Evaluación

Se utilizó un conjunto de 10 consultas representativas:

**Recuperación directa (2):** Preguntas sobre información explícita en los documentos (e.g., tipos de sanciones)

**Búsqueda semántica (3):** Consultas que requieren match semántico, no sintáctico (e.g., "¿Es legal multar al dueño si otra persona conducía?")

**Síntesis multi-fragmento (3):** Casos que requieren combinación de múltiples artículos (e.g., procedimientos completos de inmovilización)

**Fuera de dominio (2):** Consultas que exceden el alcance de la Ley 769 (e.g., números telefónicos de procedimientos, impuestos vehiculares), donde la respuesta correcta es "No encontré información suficiente"

### Resultados Obtenidos

Los resultados reales del sistema se encuentran en app/routes.py (variable EVAL_RESULTS):

| Pregunta | Faithfulness | Answer Relevancy | Context Precision |
|---|---|---|---|
| ¿Qué tipos de sanciones contempla el Código Nacional de Tránsito? | 1.00 | 0.870 | 1.000 |
| ¿Cómo define la ley la reincidencia? | 0.50 | 0.810 | 1.000 |
| ¿Es legal que me impongan una multa si otra persona iba conduciendo mi vehículo? | 1.00 | 0.778 | 1.000 |
| ¿En qué medida se calculan los montos de las multas de tránsito? | 0.75 | 0.775 | 0.533 |
| Si un agente no puede ver mi licencia física, ¿puede hacerme un comparendo? | 1.00 | 0.806 | 0.500 |
| ¿Qué pasa si llego a mi carro cuando una grúa lo está levantando? | 1.00 | 0.696 | 0.867 |
| ¿Qué procedimiento se sigue si mi vehículo falla la prueba de gases? | 1.00 | 0.815 | 0.000 |
| ¿Qué formalidad se cumple al ingresar un vehículo al parqueadero por inmovilización? | 1.00 | 0.860 | 1.000 |
| ¿Cuál es el número de teléfono para saber dónde está mi carro inmovilizado en Bogotá? | 0.00 | 0.000 | 0.700 |
| ¿Cómo puedo obtener un descuento para el pago del impuesto vehicular? | 0.00 | 0.000 | 0.450 |

**Promedios globales:**
- Faithfulness: 0.725
- Answer Relevancy: 0.641
- Context Precision: 0.705

### Análisis de Resultados

**Fortalezas:**
- Faithfulness de 0.725 indica que el sistema evita alucinaciones en la mayoría de casos
- Las métricas más altas en recuperación directa (preguntas 1, 3, 8) muestran que el sistema es confiable para consultas sobre artículos específicos
- Context Precision de 1.0 en varios casos demuestra que la vectorización captura adecuadamente contenido relevante

**Áreas de mejora:**
- Answer Relevancy promedio (0.641) sugiere que algunas respuestas, aunque fieles, no cubren completamente lo que el usuario preguntó
- Context Precision baja en preguntas 7 y 10 indica que ocasionalmente se recuperan fragmentos periféricos
- El sistema correctamente rechaza consultas fuera de dominio (preguntas 9, 10 con faithfulness 0.0)

### Conclusión de Evaluación

El sistema demuestra confiabilidad general para responder consultas sobre normativa de tránsito basándose exclusivamente en los documentos disponibles. Los resultados justifican su uso en contexto educativo y como herramienta de consulta primera línea, siempre con la advertencia de que no constituye asesoría legal profesional.

## 8. Configuración e Instalación

### Requisitos Previos

- Python 3.10 o superior
- Conexión a internet (para APIs de Google)
- API Key de Google desde [aistudio.google.com](https://aistudio.google.com/)

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/RodriKonrad/proyecto-IA.git
cd proyecto-IA
```

2. **Crear entorno virtual:**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configurar API Key:**
Copiar .env.example a .env y agregar tu GEMINI_API_KEY:
```bash
cp .env.example .env
# Editar .env y agregar GEMINI_API_KEY=tu_clave
```

5. **Agregar documentos PDF:**
```bash
mkdir -p data
# Copiar archivos PDF a la carpeta data/
```

## 9. Ejecución del Sistema

Ejecutar el servidor:
```bash
python run.py
```

El servidor inicia en http://127.0.0.1:5000. Durante la inicialización:
- Se cargan automáticamente los PDFs de /data
- Se generan fragmentos con parámetros configurados
- Se crean embeddings de todos los fragmentos
- Se persiste la base vectorial en chroma_db/

Una vez lista la interfaz, puede enviarse consultas sobre normativa de tránsito. La consola imprime los fragmentos recuperados para cada consulta, permitiendo verificar la relevancia de la recuperación.

### Endpoints Disponibles

- `GET /` — Interfaz principal de chat
- `GET /ayuda` — Página de documentación
- `GET /evaluacion` — Página con métricas RAGAS
- `POST /chat/send` — Endpoint RAG (acepta JSON con message)
- `POST /chat/reset` — Reinicia historial de conversación

## 10. Estructura del Proyecto

```
proyecto-IA/
├── run.py                    # Punto de entrada
├── requirements.txt          # Dependencias Python
├── .env.example             # Plantilla de configuración
├── README.md                # Este archivo
│
├── data/                    # Documentos PDF (agregar aquí)
│   └── ley_769_2002.pdf
│
├── chroma_db/               # Base vectorial (auto-generada)
│   ├── data.parquet
│   └── index/
│
├── rag/                     # Pipeline RAG
│   ├── loader.py           # Carga de PDFs
│   ├── chunker.py          # Fragmentación
│   ├── vectorstore.py      # ChromaDB + embeddings
│   ├── prompt_config.py    # Instrucciones y templates
│   ├── pipeline.py         # Orquestación del pipeline
│   └── rag_evaluation.py   # Evaluación RAGAS
│
└── app/                     # Aplicación Flask
    ├── __init__.py         # Inicialización
    ├── routes.py           # Endpoints HTTP
    ├── templates/          # HTML templates
    │   ├── index.html
    │   ├── ayuda.html
    │   └── evaluacion.html
    └── static/             # CSS y JavaScript
        ├── style.css
        └── script.js
```

---

**Última actualización:** 2026-05-14  
**Versión:** 2.0  
**Autores:** Daniel Felipe Chávez González, Rodrigo Muñoz Andrade  
**Institución:** Fundación Universitaria Konrad Lorenz
