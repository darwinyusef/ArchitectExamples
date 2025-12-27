"""
MCP Server para RAG (Retrieval Augmented Generation) con LangGraph
Permite consultar documentos y obtener respuestas contextualizadas usando grafos de estado
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional, TypedDict, Annotated
import json
import os
from pathlib import Path
import operator

# LangChain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    TextLoader,
    PDFMinerLoader,
    DirectoryLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import Document, HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.tools import Tool

# Crear servidor MCP
mcp = FastMCP("RAG-LangGraph")

# Configuración
VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", "./chroma_db")
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "./documents")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no está configurada. Por favor configura tu API key de OpenAI.")

# Variables globales
vectorstore = None
embeddings = None


# Estado para LangGraph
class RAGState(TypedDict):
    """Estado del grafo RAG"""
    question: str
    documents: List[Document]
    context: str
    answer: str
    sources: List[Dict[str, Any]]
    num_sources: int
    chat_history: Annotated[List, operator.add]


def initialize_embeddings():
    """Inicializa el modelo de embeddings de OpenAI"""
    global embeddings
    if embeddings is None:
        embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
    return embeddings


def initialize_vectorstore():
    """Inicializa o carga el vectorstore"""
    global vectorstore
    if vectorstore is None:
        emb = initialize_embeddings()

        # Crear directorio si no existe
        Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)

        # Intentar cargar vectorstore existente
        try:
            vectorstore = Chroma(
                persist_directory=VECTORSTORE_PATH,
                embedding_function=emb
            )
        except:
            # Crear nuevo vectorstore si no existe
            vectorstore = Chroma(
                persist_directory=VECTORSTORE_PATH,
                embedding_function=emb
            )
    return vectorstore


def retrieve_documents(state: RAGState) -> RAGState:
    """Nodo: Recupera documentos relevantes del vectorstore"""
    vs = initialize_vectorstore()

    # Buscar documentos similares
    docs = vs.similarity_search(
        state["question"],
        k=state.get("num_sources", 3)
    )

    state["documents"] = docs
    return state


def prepare_context(state: RAGState) -> RAGState:
    """Nodo: Prepara el contexto a partir de los documentos recuperados"""
    context_parts = []
    sources = []

    for i, doc in enumerate(state["documents"], 1):
        context_parts.append(f"[Documento {i}]\n{doc.page_content}\n")
        sources.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "source": doc.metadata.get("source", "Unknown")
        })

    state["context"] = "\n".join(context_parts)
    state["sources"] = sources
    return state


def generate_answer(state: RAGState) -> RAGState:
    """Nodo: Genera la respuesta usando el LLM"""
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Eres un asistente experto que responde preguntas basándote en el contexto proporcionado.

Reglas importantes:
1. Solo usa información del contexto proporcionado
2. Si no sabes la respuesta, di claramente que no tienes esa información
3. Cita los documentos cuando sea relevante usando [Documento X]
4. Sé conciso pero completo
5. Usa un tono profesional y amigable

Contexto:
{context}
"""),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{question}")
    ])

    chain = prompt | llm

    response = chain.invoke({
        "context": state["context"],
        "question": state["question"],
        "chat_history": state.get("chat_history", [])
    })

    state["answer"] = response.content

    # Actualizar historial de chat
    if "chat_history" not in state:
        state["chat_history"] = []
    state["chat_history"].append(HumanMessage(content=state["question"]))
    state["chat_history"].append(AIMessage(content=state["answer"]))

    return state


def create_rag_graph() -> StateGraph:
    """Crea el grafo de estado para RAG"""
    workflow = StateGraph(RAGState)

    # Agregar nodos
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("prepare_context", prepare_context)
    workflow.add_node("generate", generate_answer)

    # Definir flujo
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "prepare_context")
    workflow.add_edge("prepare_context", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


@mcp.tool()
def load_documents(
    directory_path: str,
    file_types: Optional[List[str]] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> Dict[str, Any]:
    """
    Carga documentos desde un directorio y los procesa para el RAG.

    Args:
        directory_path: Ruta al directorio con documentos
        file_types: Lista de tipos de archivo a cargar (ej: ['txt', 'pdf', 'md'])
        chunk_size: Tamaño de los chunks de texto
        chunk_overlap: Superposición entre chunks

    Returns:
        Resultado de la carga y procesamiento
    """
    try:
        file_types = file_types or ['txt', 'pdf', 'md']
        documents = []

        # Cargar documentos según tipo
        for file_type in file_types:
            if file_type == 'txt':
                loader = DirectoryLoader(
                    directory_path,
                    glob=f"**/*.txt",
                    loader_cls=TextLoader,
                    show_progress=True
                )
            elif file_type == 'pdf':
                loader = DirectoryLoader(
                    directory_path,
                    glob=f"**/*.pdf",
                    loader_cls=PDFMinerLoader,
                    show_progress=True
                )
            elif file_type == 'md':
                loader = DirectoryLoader(
                    directory_path,
                    glob=f"**/*.md",
                    loader_cls=UnstructuredMarkdownLoader,
                    show_progress=True
                )
            else:
                continue

            docs = loader.load()
            documents.extend(docs)

        if not documents:
            return {
                "success": False,
                "error": f"No se encontraron documentos en {directory_path}"
            }

        # Dividir documentos en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)

        # Agregar a vectorstore
        vs = initialize_vectorstore()
        vs.add_documents(chunks)
        vs.persist()

        return {
            "success": True,
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "directory": directory_path,
            "file_types": file_types
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


@mcp.tool()
def add_text_document(
    text: str,
    metadata: Optional[Dict[str, Any]] = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> Dict[str, Any]:
    """
    Agrega un documento de texto directamente al RAG.

    Args:
        text: Texto del documento
        metadata: Metadatos opcionales del documento
        chunk_size: Tamaño de los chunks
        chunk_overlap: Superposición entre chunks

    Returns:
        Resultado de la operación
    """
    try:
        # Crear documento
        doc = Document(
            page_content=text,
            metadata=metadata or {}
        )

        # Dividir en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents([doc])

        # Agregar a vectorstore
        vs = initialize_vectorstore()
        vs.add_documents(chunks)
        vs.persist()

        return {
            "success": True,
            "chunks_created": len(chunks),
            "metadata": metadata
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def query_rag(
    question: str,
    num_sources: int = 3,
    return_sources: bool = True,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Hace una pregunta al sistema RAG usando LangGraph y obtiene una respuesta contextualizada.

    Args:
        question: Pregunta a responder
        num_sources: Número de documentos fuente a recuperar
        return_sources: Si se deben retornar los documentos fuente
        chat_history: Historial de conversación previo (opcional)

    Returns:
        Respuesta con documentos fuente opcionales
    """
    try:
        # Crear grafo RAG
        graph = create_rag_graph()

        # Convertir historial de chat a formato LangChain
        lc_history = []
        if chat_history:
            for msg in chat_history:
                if msg.get("role") == "user":
                    lc_history.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    lc_history.append(AIMessage(content=msg["content"]))

        # Estado inicial
        initial_state = {
            "question": question,
            "num_sources": num_sources,
            "documents": [],
            "context": "",
            "answer": "",
            "sources": [],
            "chat_history": lc_history
        }

        # Ejecutar grafo
        result = graph.invoke(initial_state)

        response = {
            "success": True,
            "question": question,
            "answer": result["answer"]
        }

        # Agregar fuentes si se solicitan
        if return_sources:
            response["sources"] = result["sources"]
            response["num_sources"] = len(result["sources"])

        return response

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


@mcp.tool()
def search_similar_documents(
    query: str,
    k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Busca documentos similares en el vectorstore.

    Args:
        query: Texto de búsqueda
        k: Número de documentos a retornar
        filter_metadata: Filtros opcionales por metadata

    Returns:
        Documentos similares con scores de similitud
    """
    try:
        vs = initialize_vectorstore()

        # Buscar documentos similares
        if filter_metadata:
            results = vs.similarity_search_with_score(
                query,
                k=k,
                filter=filter_metadata
            )
        else:
            results = vs.similarity_search_with_score(query, k=k)

        documents = []
        for doc, score in results:
            documents.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score)
            })

        return {
            "success": True,
            "query": query,
            "documents": documents,
            "num_results": len(documents)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_vectorstore_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del vectorstore.

    Returns:
        Estadísticas del vectorstore
    """
    try:
        vs = initialize_vectorstore()

        # Obtener colección
        collection = vs._collection

        return {
            "success": True,
            "total_documents": collection.count(),
            "vectorstore_path": VECTORSTORE_PATH,
            "embedding_model": EMBEDDING_MODEL,
            "llm_model": OPENAI_MODEL
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def multi_step_reasoning(
    question: str,
    max_steps: int = 3
) -> Dict[str, Any]:
    """
    Realiza razonamiento multi-paso usando LangGraph.
    Útil para preguntas complejas que requieren múltiples consultas.

    Args:
        question: Pregunta compleja a responder
        max_steps: Número máximo de pasos de razonamiento

    Returns:
        Respuesta con pasos de razonamiento
    """
    try:
        class ReasoningState(TypedDict):
            question: str
            steps: Annotated[List[Dict[str, str]], operator.add]
            current_step: int
            max_steps: int
            final_answer: str

        def reasoning_step(state: ReasoningState) -> ReasoningState:
            """Ejecuta un paso de razonamiento"""
            llm = ChatOpenAI(
                model=OPENAI_MODEL,
                temperature=0.3,
                openai_api_key=OPENAI_API_KEY
            )

            prompt = f"""Estás resolviendo la pregunta: {state['question']}

Pasos previos:
{chr(10).join([f"{i+1}. {s['reasoning']}" for i, s in enumerate(state['steps'])])}

Realiza el siguiente paso de razonamiento. ¿Qué necesitas investigar o analizar?
Sé específico y conciso."""

            response = llm.invoke(prompt)

            # Buscar información relevante
            vs = initialize_vectorstore()
            docs = vs.similarity_search(response.content, k=2)
            context = "\n".join([doc.page_content for doc in docs])

            state["steps"].append({
                "step": state["current_step"],
                "reasoning": response.content,
                "context": context
            })

            state["current_step"] += 1
            return state

        def generate_final_answer(state: ReasoningState) -> ReasoningState:
            """Genera la respuesta final basada en todos los pasos"""
            llm = ChatOpenAI(
                model=OPENAI_MODEL,
                temperature=0.7,
                openai_api_key=OPENAI_API_KEY
            )

            steps_summary = "\n\n".join([
                f"Paso {s['step']}: {s['reasoning']}\nContexto: {s['context']}"
                for s in state["steps"]
            ])

            prompt = f"""Basándote en el siguiente razonamiento multi-paso, responde la pregunta original.

Pregunta: {state['question']}

Razonamiento:
{steps_summary}

Proporciona una respuesta completa y bien fundamentada:"""

            response = llm.invoke(prompt)
            state["final_answer"] = response.content
            return state

        def should_continue(state: ReasoningState) -> str:
            """Decide si continuar razonando o terminar"""
            if state["current_step"] >= state["max_steps"]:
                return "generate"
            return "reason"

        # Crear grafo de razonamiento
        workflow = StateGraph(ReasoningState)
        workflow.add_node("reason", reasoning_step)
        workflow.add_node("generate", generate_final_answer)

        workflow.set_entry_point("reason")
        workflow.add_conditional_edges(
            "reason",
            should_continue,
            {
                "reason": "reason",
                "generate": "generate"
            }
        )
        workflow.add_edge("generate", END)

        graph = workflow.compile()

        # Ejecutar
        initial_state = {
            "question": question,
            "steps": [],
            "current_step": 1,
            "max_steps": max_steps,
            "final_answer": ""
        }

        result = graph.invoke(initial_state)

        return {
            "success": True,
            "question": question,
            "reasoning_steps": result["steps"],
            "final_answer": result["final_answer"]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def clear_vectorstore() -> Dict[str, Any]:
    """
    Limpia completamente el vectorstore.

    Returns:
        Resultado de la operación
    """
    try:
        global vectorstore

        # Eliminar el vectorstore existente
        if os.path.exists(VECTORSTORE_PATH):
            import shutil
            shutil.rmtree(VECTORSTORE_PATH)

        # Reinicializar
        vectorstore = None
        initialize_vectorstore()

        return {
            "success": True,
            "message": "Vectorstore limpiado exitosamente"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.resource("rag://stats")
def get_stats_resource() -> str:
    """Resource que provee estadísticas del RAG"""
    stats = get_vectorstore_stats()
    return json.dumps(stats, indent=2)


@mcp.resource("rag://config")
def get_config_resource() -> str:
    """Resource que provee la configuración actual"""
    config = {
        "vectorstore_path": VECTORSTORE_PATH,
        "documents_path": DOCUMENTS_PATH,
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": OPENAI_MODEL,
        "api_configured": bool(OPENAI_API_KEY)
    }
    return json.dumps(config, indent=2)


if __name__ == "__main__":
    # Crear directorios necesarios
    Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)
    Path(DOCUMENTS_PATH).mkdir(parents=True, exist_ok=True)

    # Iniciar servidor
    mcp.run()
