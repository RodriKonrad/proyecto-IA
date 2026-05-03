"""
rag/vectorstore.py
Módulo de embeddings y base de datos vectorial.
Vectoriza los chunks con Google Generative AI Embeddings
y los persiste en ChromaDB de forma local.
"""

import os
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Directorio donde ChromaDB persiste los vectores en disco
VECTOR_DIR       = str(Path(__file__).resolve().parent.parent / "chroma_db")
COLLECTION_NAME  = "asesor_transito"
EMBEDDING_MODEL  = "gemini-embedding-001"


def get_embeddings_model(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """Devuelve el modelo de embeddings de Google configurado."""
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=api_key,
    )


def build_vector_store(
    chunks: list[Document],
    api_key: str,
    force_rebuild: bool = False,
) -> Chroma:
    """
    Construye (o reutiliza) la base vectorial ChromaDB en disco.

    Si ya existe la base y force_rebuild=False, la carga directamente
    para evitar re-vectorizar en cada inicio.

    Args:
        chunks:        fragmentos a indexar.
        api_key:       clave de la API de Google.
        force_rebuild: si True, borra y reconstruye la base aunque exista.

    Returns:
        Instancia de Chroma lista para búsquedas.
    """
    embeddings = get_embeddings_model(api_key)

    if os.path.exists(VECTOR_DIR) and not force_rebuild:
        print(f"\n{'='*60}")
        print("BASE VECTORIAL — Cargando desde disco (ya existente)")
        print(f"  Directorio: {VECTOR_DIR}")
        store = Chroma(
            persist_directory=VECTOR_DIR,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )
        total = store._collection.count()
        print(f"  Fragmentos indexados: {total}")
        print(f"{'='*60}\n")
        return store

    # Borrar base anterior si existe (reconstrucción forzada)
    if os.path.exists(VECTOR_DIR):
        shutil.rmtree(VECTOR_DIR)
        print(f"  Base anterior eliminada para reconstrucción.")

    print(f"\n{'='*60}")
    print(f"BASE VECTORIAL — Indexando {len(chunks)} fragmentos…")
    print(f"  Modelo embeddings: {EMBEDDING_MODEL}")
    print(f"  Directorio       : {VECTOR_DIR}")
    print(f"  (Este proceso puede tardar según la cantidad de PDFs)")
    print(f"{'='*60}")

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DIR,
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"},
    )

    total = store._collection.count()
    print(f"\n  ✔ Base vectorial creada con {total} fragmentos.")
    print(f"{'='*60}\n")

    return store


def get_retriever(store: Chroma, k: int = 5):
    """
    Devuelve un retriever configurado para búsqueda por similitud coseno.

    Args:
        store: instancia de Chroma.
        k:     número de fragmentos a recuperar por consulta.

    Returns:
        Retriever de LangChain.
    """
    return store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )