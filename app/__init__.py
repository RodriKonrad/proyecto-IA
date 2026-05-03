"""
app/__init__.py
Factory de la aplicación Flask.
Inicializa el sistema RAG automáticamente al arrancar el servidor.
"""

import os
from flask import Flask
from dotenv import load_dotenv

from rag.loader import load_pdfs
from rag.chunker import split_documents
from rag.vectorstore import build_vector_store
from rag.pipeline import RAGPipeline


def create_app() -> Flask:
    """
    Crea y configura la aplicación Flask.
    Inicializa el pipeline RAG completo al arrancar:
      1. Carga PDFs desde /data
      2. Divide en chunks
      3. Vectoriza y persiste en ChromaDB
      4. Crea el pipeline de consulta
    """
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)
    app.config["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

    api_key = app.config["GEMINI_API_KEY"]
    if not api_key:
        raise EnvironmentError(
            "[ERROR CRÍTICO] GEMINI_API_KEY no encontrada.\n"
            "Crea un archivo .env en la raíz del proyecto con:\n"
            "  GEMINI_API_KEY=tu_clave_aqui"
        )

    # ── Inicialización del sistema RAG ────────────────────────────────────
    print("\n" + "=" * 60)
    print("  INICIALIZANDO SISTEMA RAG — Asesor Normativo de Tránsito")
    print("=" * 60)

    # Paso 1 & 2: Carga y fragmentación de documentos
    documents = load_pdfs()
    chunks    = split_documents(documents)

    # Paso 3: Base vectorial (reutiliza si ya existe)
    vector_store = build_vector_store(chunks, api_key, force_rebuild=False)

    # Paso 4: Pipeline RAG
    rag_pipeline = RAGPipeline(vector_store=vector_store, api_key=api_key, k=5)

    # Disponibilizar el pipeline en la app
    app.config["RAG_PIPELINE"] = rag_pipeline

    print("  ✔ Sistema RAG listo. Iniciando servidor Flask…\n")

    # Registrar blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app