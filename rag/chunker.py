"""
rag/chunker.py
Módulo de fragmentación (chunking) de documentos.
Divide los documentos en fragmentos semánticamente coherentes
para su posterior vectorización.
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Parámetros de chunking — ajustar según el tipo de documentos
CHUNK_SIZE    = 600   # Máximo de caracteres por fragmento
CHUNK_OVERLAP = 80    # Solapamiento entre fragmentos consecutivos


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Divide una lista de Documents en fragmentos más pequeños usando
    RecursiveCharacterTextSplitter.

    Estrategia de separación (orden de prioridad):
      1. Párrafos    (\\n\\n)
      2. Líneas      (\\n)
      3. Oraciones   (. )
      4. Palabras    ( )

    Args:
        documents: lista de Documents cargados desde los PDFs.

    Returns:
        Lista de fragmentos (chunks) como objetos Document.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)

    print(f"\n{'='*60}")
    print("CHUNKING DE DOCUMENTOS")
    print(f"{'='*60}")
    print(f"  Páginas originales :  {len(documents)}")
    print(f"  Fragmentos creados :  {len(chunks)}")
    print(f"  Factor expansión   :  {len(chunks)/max(len(documents),1):.1f}x")
    print(f"  Tamaño chunk       :  {CHUNK_SIZE} caracteres")
    print(f"  Solapamiento       :  {CHUNK_OVERLAP} caracteres")

    # Estadísticas de longitud
    lengths = [len(c.page_content) for c in chunks]
    print(f"  Longitud media     :  {sum(lengths)//len(lengths)} chars")
    print(f"  Longitud mínima    :  {min(lengths)} chars")
    print(f"  Longitud máxima    :  {max(lengths)} chars")
    print(f"{'='*60}\n")

    return chunks