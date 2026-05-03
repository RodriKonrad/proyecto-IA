# Asesor Normativo de Tránsito — Sistema RAG

Asistente experto en normativa de tránsito colombiana basado en **Retrieval Augmented Generation (RAG)**.
El sistema responde consultas sobre comparendos e infracciones utilizando **exclusivamente** los documentos PDF cargados en el proyecto.

---

## 🧠 Arquitectura del Sistema RAG

```
📄 PDFs en /data/
       │
       ▼
  ✂️  PASO 1 — Carga automática de documentos (PyPDFLoader)
       │           rag/loader.py
       ▼
  🧩  PASO 2 — División en chunks (RecursiveCharacterTextSplitter)
       │           rag/chunker.py  |  chunk_size=600, overlap=80
       ▼
  🔢  PASO 3 — Generación de embeddings (gemini-embedding-001)
       │           rag/vectorstore.py
       ▼
  🗄️  PASO 4 — Base vectorial local (ChromaDB en /chroma_db)
       │           rag/vectorstore.py  |  similitud coseno
       ▼
  ❓  Consulta del usuario (interfaz web Flask)
       │
       ▼
  🔍  PASO 5 — Búsqueda vectorial → k=5 fragmentos más relevantes
       │           rag/pipeline.py  [DEBUG: imprime fragmentos en consola]
       ▼
  📝  PASO 6 — Prompt aumentado (contexto + historial + pregunta)
       │           rag/prompt_config.py
       ▼
  🤖  PASO 7 — LLM genera respuesta (gemini-2.5-flash, temp=0.2)
       │           rag/pipeline.py
       ▼
  💬  Respuesta estructurada al usuario
```

### Flujo resumido

1. **PDF → chunks**: los documentos se dividen en fragmentos de ~600 caracteres con 80 de solapamiento para preservar el contexto entre fragmentos.
2. **Chunks → embeddings**: cada fragmento se convierte en un vector de 3072 dimensiones con el modelo `gemini-embedding-001`.
3. **Embeddings → ChromaDB**: los vectores se persisten en disco (carpeta `chroma_db/`) con similitud coseno. Solo se reconstruyen si los documentos cambian.
4. **Consulta → recuperación**: la pregunta del usuario se vectoriza y se buscan los 5 fragmentos más similares.
5. **Prompt aumentado → respuesta**: los fragmentos se inyectan en el prompt junto con el historial y se envían al LLM.

---

## 🛠️ Requisitos Previos

- Python 3.10 o superior
- Una **API Key de Google AI Studio (Gemini)** → [aistudio.google.com](https://aistudio.google.com/)

---

## 🚀 Configuración del Entorno

### 1. Clonar el repositorio

```bash
git clone https://github.com/RodriKonrad/proyecto-IA.git proyecto-IA
cd proyecto-IA
```

### 2. Crear y activar el entorno virtual

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la API Key

```bash
cp .env.example .env
# Editar .env y agregar tu clave:
# GEMINI_API_KEY=tu_clave_aqui
```

### 5. Agregar documentos PDF

Coloca los archivos PDF en la carpeta `data/`:

```
proyecto-IA/
└── data/
    ├── codigo_transito_colombiano.pdf
    ├── manual_infracciones.pdf
    └── ...   ← agrega aquí los PDFs
```

> **Importante:** El sistema carga automáticamente todos los PDFs de esta carpeta.
> No se permite ni se necesita carga dinámica por parte del usuario.

---

## 💻 Ejecución

```bash
python run.py
```

Al iniciar, el sistema:
1. Carga y fragmenta todos los PDFs de `/data`
2. Vectoriza los fragmentos (o carga la base existente si ya fue creada)
3. Inicia el servidor Flask en `http://127.0.0.1:5000`

---

## 📚 Rutas disponibles

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/` | GET | Interfaz principal del asesor |
| `/ayuda` | GET | Página de ayuda y documentación |
| `/chat/send` | POST | Endpoint RAG: recibe `{ "message": "..." }` y devuelve `{ "response": "..." }` |
| `/chat/reset` | POST | Reinicia el historial de conversación |

---

## 🔍 Debug de fragmentos recuperados

Cada consulta imprime en la consola del servidor los fragmentos recuperados:

```
████████████████████████████████████████████████████████████
DEBUG RAG — FRAGMENTOS RECUPERADOS
████████████████████████████████████████████████████████████
  Consulta : ¿Qué dice la ley sobre cruzar en semáforo rojo?
  K        : 5 fragmentos solicitados
  Obtenidos: 5 fragmentos
────────────────────────────────────────────────────────────

  [1] codigo_transito.pdf  |  Pág. 12  |  487 chars
      Artículo 60. Señales de tránsito. El semáforo en rojo…

  [2] manual_infracciones.pdf  |  Pág. 3  |  412 chars
      La infracción C14 corresponde a…
```

---

## ➕ Agregar nuevos documentos

1. Copia el PDF a la carpeta `data/`
2. Elimina la base vectorial existente: `rm -rf chroma_db/`
3. Reinicia el servidor: `python run.py`

El sistema reconstruirá automáticamente la base vectorial con los nuevos documentos.

---

## 🗒️ Estructura del proyecto

```
proyecto-IA/
├── run.py                    ← Punto de entrada
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/                     ← PDFs de la base de conocimiento (fijos)
│   └── *.pdf
│
├── chroma_db/                ← Base vectorial (generada automáticamente)
│
├── rag/                      ← Módulos del pipeline RAG
│   ├── __init__.py
│   ├── loader.py             ← Carga de PDFs
│   ├── chunker.py            ← Fragmentación
│   ├── vectorstore.py        ← Embeddings + ChromaDB
│   ├── prompt_config.py      ← Prompt engineering
│   └── pipeline.py           ← Pipeline RAG completo
│
└── app/                      ← Aplicación Flask
    ├── __init__.py           ← Factory + inicialización RAG
    ├── routes.py             ← Endpoints
    ├── templates/
    │   ├── index.html
    │   └── ayuda.html
    └── static/
        ├── style.css
        └── script.js
```

---

## ✅ Ejemplo de ejecución

1. Arranca el servidor: `python run.py`
2. Abre `http://127.0.0.1:5000`
3. Escribe tu consulta sobre el comparendo
4. Observa en la terminal los fragmentos recuperados (debug)
5. Recibe el análisis estructurado basado en la normativa oficial