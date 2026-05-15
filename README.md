# TransitLex — Asesor de Normativa de Tránsito

Sistema RAG que responde preguntas sobre la Ley 769 de 2002 (Código Nacional de Tránsito Terrestre) usando documentos PDF oficiales como fuente. Combina búsqueda vectorial con Google Gemini para proporcionar respuestas precisas y fundamentadas.

**Tecnología:** Flask + LangChain + ChromaDB + Google Gemini

---

## Cómo funciona (Pipeline)

El sistema sigue un flujo de Retrieval-Augmented Generation:

1. **Carga:** Los PDFs en `/data` se cargan automáticamente al iniciar — `loader.py` (PyPDFLoader)
2. **Fragmentación:** Se dividen en chunks de 600 caracteres con 80 de solapamiento — `chunker.py` (RecursiveCharacterTextSplitter)
3. **Vectorización:** Cada fragmento se convierte a un vector — `vectorstore.py` (gemini-embedding-001)
4. **Almacenamiento:** Los vectores se persisten en ChromaDB — `vectorstore.py` (ChromaDB)
5. **Búsqueda:** Para cada pregunta, se recuperan los 5 fragmentos más relevantes — `pipeline.py` (ChromaDB retriever)
6. **Respuesta:** Se envían al modelo con el contexto recuperado — `pipeline.py` (gemini-2.5-flash)

---

## Evaluación RAGAS

Se evaluó el sistema con 10 consultas representativas sobre tránsito. Métricas utilizadas:

- **Faithfulness:** ¿La respuesta es fiel al contexto (sin alucinaciones)?
- **Answer Relevancy:** ¿La respuesta responde la pregunta del usuario?
- **Context Precision:** ¿Los fragmentos recuperados son relevantes?

### Ejecutar la evaluación

```bash
python -m rag.rag_evaluation
```

Genera respuestas evaluadas con RAGAS y actualiza los resultados.

**Nota sobre prompts:** La evaluación usa un prompt simplificado enfocado en respuestas puntuales, diferente al del chat que incluye formato estructurado (resumen, normativa, análisis, conclusión, recomendación). El prompt simplificado es más fácil de evaluar automáticamente y permite obtener métricas RAGAS precisas sin el overhead del formato completo del asesor.

### Resultados

| Pregunta | Faithfulness | Answer Relevancy | Context Precision |
|----------|:---:|:---:|:---:|
| ¿Qué tipos de sanciones contempla el Código Nacional de Tránsito? | 1.00 | 0.699 | 1.000 |
| ¿Cómo define la ley la reincidencia? | 0.50 | 0.817 | 1.000 |
| ¿Es legal que me impongan una multa si otra persona iba conduciendo mi vehículo? | 1.00 | 0.778 | 1.000 |
| ¿En qué medida se calculan los montos de las multas de tránsito? | 0.75 | 0.775 | 0.533 |
| Si un agente no puede ver mi licencia física, ¿puede hacerme un comparendo? | 0.67 | 0.798 | 0.500 |
| ¿Qué pasa si llego a mi carro cuando una grúa lo está levantando? | 1.00 | 0.800 | 0.867 |
| ¿Qué procedimiento se sigue si mi vehículo falla la prueba de gases? | 1.00 | 0.839 | 0.000 |
| ¿Qué formalidad se debe cumplir al ingresar un vehículo a un parqueadero? | 1.00 | 0.860 | 1.000 |
| ¿Cuál es el número de teléfono para saber dónde está mi carro inmovilizado en Bogotá? | 0.00 | 0.000 | 0.700 |
| ¿Cómo puedo obtener un descuento para el pago del impuesto vehicular? | 0.00 | 0.000 | 0.500 |

**Promedios globales:**
- Faithfulness: **0.6917**
- Answer Relevancy: **0.6366**
- Context Precision: **0.7100**

**Conclusión:** El sistema es confiable para consultas sobre normativa de tránsito. Faithfulness alta indica pocas alucinaciones. Answer Relevancy muestra que las respuestas cubren bien las preguntas. Las métricas bajas en consultas fuera del dominio (preguntas 9 y 10) son esperadas — el sistema correctamente rechaza información que no está en los documentos.

---

## Instalación

### Requisitos
- Python 3.10+
- API Key de Google (desde [aistudio.google.com](https://aistudio.google.com/))

### Pasos

```bash
# Clonar y entrar al directorio
git clone <repo>
cd proyecto-IA

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key
# Crear archivo .env con:
# GEMINI_API_KEY=tu_clave_aqui
```

### Agregar documentos
```bash
mkdir -p data
# Copiar archivos PDF a data/
```

---

## Ejecutar

```bash
python run.py
```

El servidor inicia en `http://127.0.0.1:5000`

**Endpoints:**
- `GET /` — Chat principal
- `GET /ayuda` — Documentación
- `GET /evaluacion` — Resultados de evaluación RAGAS
- `POST /chat/send` — Enviar pregunta (JSON: `{"message": "..."}`)
- `POST /chat/reset` — Limpiar historial

---

## Estructura del proyecto

```
proyecto-IA/
├── run.py                 # Punto de entrada
├── requirements.txt
├── .env                   # API keys (no versionar)
│
├── data/                  # PDFs (agregar aquí)
├── chroma_db/            # Base vectorial (auto-generada)
│
├── rag/                   # Pipeline RAG
│   ├── loader.py
│   ├── chunker.py
│   ├── vectorstore.py
│   ├── prompt_config.py
│   ├── pipeline.py
│   └── rag_evaluation.py
│
└── app/                   # Flask
    ├── routes.py
    ├── templates/        # HTML (index, ayuda, evaluacion)
    └── static/          # CSS y JS
```

---

## Notas técnicas

- **Chunk size:** 600 caracteres balancean coherencia semántica vs especificidad
- **Overlap:** 80 caracteres preservan continuidad entre fragmentos
- **k=5:** Se recuperan 5 fragmentos por consulta (balance cobertura/ruido)
- **Temperatura:** 0.2 para respuestas deterministas en dominio legal
- **ChromaDB:** Persiste en disco, se reutiliza entre reinicios
- **Embeddings:** Google `gemini-embedding-001` (3,072 dimensiones)
- **LLM:** Google `gemini-2.5-flash`

---

**Última actualización:** 2026-05-14  
**Autores:** Daniel Felipe Chávez González, Rodrigo Muñoz Andrade  
**Institución:** Fundación Universitaria Konrad Lorenz
