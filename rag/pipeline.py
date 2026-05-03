"""
rag/pipeline.py
Pipeline RAG completo: consulta → recuperación → prompt aumentado → respuesta.

Este módulo orquesta todos los pasos del flujo RAG e imprime
los fragmentos recuperados por consola (debug obligatorio).
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma

from rag.prompt_config import (
    SYSTEM_INSTRUCTION,
    build_prompt_template,
    format_context,
    format_history,
)


# Parámetros del LLM
LLM_MODEL       = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.2          # Baja temperatura → respuestas más deterministas
LLM_MAX_TOKENS  = 2048


class RAGPipeline:
    """
    Pipeline RAG completo para el Asesor Normativo de Tránsito.

    Encapsula:
      - Retriever (búsqueda vectorial)
      - Prompt aumentado (context injection)
      - LLM (generación de respuesta)
      - Historial de conversación
    """

    def __init__(self, vector_store: Chroma, api_key: str, k: int = 5):
        """
        Args:
            vector_store : base vectorial ChromaDB ya construida.
            api_key      : clave de la API de Google.
            k            : número de fragmentos a recuperar por consulta.
        """
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_output_tokens=LLM_MAX_TOKENS,
            google_api_key=api_key,
        )
        self.prompt_template = build_prompt_template()
        self.conversation_history: list[dict] = []
        self.k = k

    def query(self, user_question: str) -> str:
        """
        Ejecuta el pipeline RAG completo para una consulta del usuario.

        Pasos:
          1. Recuperar fragmentos relevantes del vector store
          2. Imprimir fragmentos por consola (debug)
          3. Formatear contexto
          4. Construir prompt aumentado
          5. Invocar el LLM
          6. Guardar en historial
          7. Retornar respuesta

        Args:
            user_question: consulta en lenguaje natural del usuario.

        Returns:
            Respuesta generada por el LLM como string.
        """

        # ── PASO 1: Recuperar fragmentos relevantes ────────────────────────
        retrieved_docs = self.retriever.invoke(user_question)

        # ── PASO 2: Debug obligatorio — imprimir fragmentos en consola ─────
        self._print_retrieved_fragments(user_question, retrieved_docs)

        # ── PASO 3: Formatear contexto ────────────────────────────────────
        context = format_context(retrieved_docs)

        # ── PASO 4: Formatear historial y construir prompt aumentado ──────
        history_text = format_history(self.conversation_history)

        prompt = self.prompt_template.invoke({
            "system_instruction": SYSTEM_INSTRUCTION,
            "context":            context,
            "history":            history_text,
            "question":           user_question,
        })

        # ── PASO 5: Invocar el LLM ────────────────────────────────────────
        response = self.llm.invoke(prompt)

        # Extraer texto de la respuesta
        if isinstance(response.content, list):
            answer = " ".join(
                block.get("text", "") for block in response.content
                if isinstance(block, dict)
            ).strip()
        else:
            answer = str(response.content).strip()

        # ── PASO 6: Guardar en historial de conversación ──────────────────
        self.conversation_history.append({"role": "user",      "content": user_question})
        self.conversation_history.append({"role": "assistant", "content": answer})

        return answer

    # ─────────────────────────────────────────────────────────────────────
    # Métodos internos
    # ─────────────────────────────────────────────────────────────────────

    def _print_retrieved_fragments(self, question: str, docs: list) -> None:
        """
        Imprime por consola los fragmentos recuperados (debug obligatorio).
        Permite verificar la relevancia de la recuperación vectorial.
        """
        print("\n" + "█" * 60)
        print("DEBUG RAG — FRAGMENTOS RECUPERADOS")
        print("█" * 60)
        print(f"  Consulta : {question[:80]}{'…' if len(question)>80 else ''}")
        print(f"  K        : {self.k} fragmentos solicitados")
        print(f"  Obtenidos: {len(docs)} fragmentos")
        print("─" * 60)

        for i, doc in enumerate(docs, 1):
            fuente = os.path.basename(doc.metadata.get("source", "desconocido"))
            pagina = doc.metadata.get("page", "?")
            longitud = len(doc.page_content)
            preview = doc.page_content[:200].replace("\n", " ").strip()

            print(f"\n  [{i}] {fuente}  |  Pág. {pagina}  |  {longitud} chars")
            print(f"      {preview}{'…' if longitud > 200 else ''}")

        print("\n" + "█" * 60 + "\n")

    def clear_history(self) -> None:
        """Reinicia el historial de conversación."""
        self.conversation_history = []
        print("[INFO] Historial de conversación reiniciado.")