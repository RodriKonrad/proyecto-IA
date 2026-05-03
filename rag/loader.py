"""
rag/loader.py
Módulo de carga de documentos PDF desde la carpeta local del proyecto.
Los documentos son fijos y definidos por el desarrollador en /data.
"""

import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


# Ruta fija de documentos — NUNCA se carga dinámicamente por el usuario
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_pdfs() -> list[Document]:
    """
    Carga todos los archivos PDF presentes en la carpeta /data del proyecto.
    La carga es automática: no requiere input del usuario.

    Returns:
        Lista de objetos Document de LangChain (una entrada por página).

    Raises:
        FileNotFoundError: si la carpeta /data no existe.
        RuntimeError: si no se encontraron PDFs en la carpeta.
    """
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"[ERROR] La carpeta de documentos no existe: {DATA_DIR}\n"
            "Crea la carpeta 'data/' en la raíz del proyecto y agrega tus PDFs."
        )

    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise RuntimeError(
            f"[ERROR] No se encontraron archivos PDF en: {DATA_DIR}\n"
            "Agrega al menos un PDF a la carpeta 'data/' y vuelve a iniciar."
        )

    print(f"\n{'='*60}")
    print(f"CARGA DE DOCUMENTOS — {len(pdf_files)} PDF(s) encontrados")
    print(f"Directorio: {DATA_DIR}")
    print(f"{'='*60}")

    documents: list[Document] = []

    for pdf_path in pdf_files:
        size_kb = pdf_path.stat().st_size // 1024
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        documents.extend(pages)
        print(f"  ✔ {pdf_path.name:<45} ({size_kb} KB — {len(pages)} páginas)")

    print(f"\nTotal páginas cargadas: {len(documents)}")
    print(f"{'='*60}\n")

    return documents