# MCP RAG con LangGraph y OpenAI

Servidor MCP para sistema RAG (Retrieval Augmented Generation) usando **LangGraph** para orquestar el flujo de consultas con grafos de estado. Utiliza **OpenAI** para embeddings y generación de respuestas.

## Características

- ✅ RAG con arquitectura de grafos (LangGraph)
- ✅ Embeddings con OpenAI (text-embedding-3-small)
- ✅ LLM con GPT-4 Turbo
- ✅ Vector store con ChromaDB
- ✅ Razonamiento multi-paso
- ✅ Soporte para historial de chat
- ✅ Soporte para múltiples formatos (TXT, PDF, Markdown)
- ✅ Búsqueda semántica avanzada
- ✅ Consultas con fuentes citadas

## Arquitectura con LangGraph

```
┌──────────────────────────────────────────────────┐
│                  LangGraph Workflow               │
│                                                   │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐ │
│  │ Retrieve │───→│  Prepare  │───→│ Generate  │ │
│  │Documents │    │  Context  │    │  Answer   │ │
│  └──────────┘    └───────────┘    └───────────┘ │
│                                                   │
│  State: { question, documents, context, answer } │
└──────────────────────────────────────────────────┘
           │                           │
           ▼                           ▼
    ┌─────────────┐            ┌────────────┐
    │  ChromaDB   │            │   OpenAI   │
    │(Vectorstore)│            │   GPT-4    │
    └─────────────┘            └────────────┘
```

### ¿Por qué LangGraph?

LangGraph permite crear flujos complejos mediante grafos de estado:
- **Nodos**: Funciones que transforman el estado
- **Edges**: Conexiones entre nodos
- **Estado**: Diccionario compartido entre nodos
- **Condicionales**: Rutas dinámicas basadas en el estado

## Instalación

### 1. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 2. Configurar OpenAI API Key

```bash
cp .env.example .env
# Editar .env y agregar tu API key de OpenAI
```

`.env`:
```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
```

### 3. (Opcional) Iniciar PostgreSQL

Si quieres almacenar metadata adicional:
```bash
docker-compose up -d
```

## Uso

### Iniciar el servidor MCP

```bash
python server.py
```

### Herramientas disponibles

#### 1. `load_documents` - Cargar documentos
```python
load_documents(
    directory_path="./documents",
    file_types=["txt", "pdf", "md"],
    chunk_size=1000,
    chunk_overlap=200
)
```

**Respuesta**:
```json
{
  "success": true,
  "documents_loaded": 10,
  "chunks_created": 45,
  "directory": "./documents",
  "file_types": ["txt", "pdf", "md"]
}
```

#### 2. `add_text_document` - Agregar texto directo
```python
add_text_document(
    text="LangGraph es un framework...",
    metadata={"source": "manual", "category": "documentation"},
    chunk_size=1000
)
```

#### 3. `query_rag` - Consultar con LangGraph ⭐
```python
query_rag(
    question="¿Qué es LangGraph y cómo funciona?",
    num_sources=3,
    return_sources=True,
    chat_history=[
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
    ]
)
```

**Flujo interno del grafo**:
1. **Nodo Retrieve**: Busca 3 documentos similares en ChromaDB
2. **Nodo Prepare Context**: Formatea los documentos como contexto
3. **Nodo Generate**: GPT-4 genera respuesta basada en contexto

**Respuesta**:
```json
{
  "success": true,
  "question": "¿Qué es LangGraph?",
  "answer": "LangGraph es un framework para crear aplicaciones con grafos de estado...",
  "sources": [
    {
      "content": "LangGraph permite...",
      "metadata": {"source": "example.txt"},
      "source": "example.txt"
    }
  ],
  "num_sources": 3
}
```

#### 4. `multi_step_reasoning` - Razonamiento multi-paso ⭐⭐

Para preguntas complejas que requieren múltiples pasos:

```python
multi_step_reasoning(
    question="Compara las ventajas de LangGraph vs cadenas tradicionales de LangChain",
    max_steps=3
)
```

**Flujo interno**:
```
Paso 1: "Necesito buscar información sobre LangGraph"
        → Busca en vectorstore → Obtiene contexto

Paso 2: "Necesito buscar información sobre cadenas tradicionales"
        → Busca en vectorstore → Obtiene contexto

Paso 3: "Necesito comparar ambos enfoques"
        → Busca en vectorstore → Obtiene contexto

Final: Genera respuesta basada en todos los pasos
```

**Respuesta**:
```json
{
  "success": true,
  "question": "Compara...",
  "reasoning_steps": [
    {
      "step": 1,
      "reasoning": "Investigar características de LangGraph",
      "context": "..."
    },
    {
      "step": 2,
      "reasoning": "Investigar cadenas LangChain",
      "context": "..."
    },
    {
      "step": 3,
      "reasoning": "Comparar ambos enfoques",
      "context": "..."
    }
  ],
  "final_answer": "LangGraph ofrece... mientras que las cadenas..."
}
```

#### 5. `search_similar_documents` - Búsqueda semántica
```python
search_similar_documents(
    query="grafos de estado",
    k=5,
    filter_metadata={"category": "documentation"}
)
```

#### 6. `get_vectorstore_stats` - Estadísticas
```python
get_vectorstore_stats()
```

**Respuesta**:
```json
{
  "success": true,
  "total_documents": 45,
  "vectorstore_path": "./chroma_db",
  "embedding_model": "text-embedding-3-small",
  "llm_model": "gpt-4-turbo-preview"
}
```

## Ejemplo de uso con LLM

El LLM puede interactuar naturalmente:

**Usuario**: "Carga los documentos de la carpeta ./docs"
→ Llama a `load_documents(directory_path="./docs")`

**Usuario**: "¿Qué es LangGraph?"
→ Llama a `query_rag(question="¿Qué es LangGraph?")`
→ **Grafo ejecuta**: Retrieve → Prepare → Generate

**Usuario**: "Explícame paso a paso cómo funciona el razonamiento multi-paso"
→ Llama a `multi_step_reasoning(question="...")`
→ **Grafo ejecuta**: Reasoning Step 1 → Step 2 → Step 3 → Generate Final

**Usuario**: "Cuántos documentos tengo?"
→ Llama a `get_vectorstore_stats()`

## Ventajas de LangGraph vs Cadenas Tradicionales

### Cadenas Tradicionales (RetrievalQA)
```
Question → Retrieve → Format → LLM → Answer
(Flujo lineal fijo)
```

### LangGraph
```
          ┌─→ Route A ─→ Process ─┐
Question ─┤              ↓         ├─→ Answer
          └─→ Route B ─→ Enhance ─┘
(Flujo dinámico con condicionales)
```

**Ventajas de LangGraph**:
- ✅ Flujos condicionales basados en estado
- ✅ Ciclos y repeticiones (ej: retry, refinement)
- ✅ Paralelización de nodos
- ✅ Estado compartido entre nodos
- ✅ Debugging más fácil (cada nodo es una función)
- ✅ Composición de grafos complejos

## Estructura del Proyecto

```
mcp-rag-langchain/
├── server.py              # Servidor MCP con LangGraph
├── requirements.txt       # Dependencias (incluye langgraph)
├── docker-compose.yml     # PostgreSQL opcional
├── .env.example          # Variables de entorno
├── documents/            # Documentos fuente
│   └── example.txt
├── chroma_db/           # Vector store (generado)
└── README.md
```

## Modelos OpenAI Recomendados

### Para Embeddings:
```bash
# Más económico y rápido
EMBEDDING_MODEL=text-embedding-3-small

# Mejor calidad
EMBEDDING_MODEL=text-embedding-3-large
```

### Para LLM:
```bash
# Mejor calidad/velocidad
OPENAI_MODEL=gpt-4-turbo-preview

# Más económico
OPENAI_MODEL=gpt-3.5-turbo

# Máxima calidad
OPENAI_MODEL=gpt-4
```

## Personalización del Grafo RAG

Puedes modificar el grafo en `server.py`:

```python
def create_rag_graph() -> StateGraph:
    """Crea el grafo de estado para RAG"""
    workflow = StateGraph(RAGState)

    # Agregar más nodos
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("rerank", rerank_documents)  # Nuevo
    workflow.add_node("prepare_context", prepare_context)
    workflow.add_node("generate", generate_answer)

    # Modificar flujo
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "rerank")  # Nuevo
    workflow.add_edge("rerank", "prepare_context")
    workflow.add_edge("prepare_context", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
```

## Ejemplo: Agregar Re-ranking

```python
def rerank_documents(state: RAGState) -> RAGState:
    """Nodo: Re-rankea documentos por relevancia"""
    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

    scored_docs = []
    for doc in state["documents"]:
        prompt = f"Del 1-10, qué tan relevante es este documento para: {state['question']}\n\n{doc.page_content}\n\nPuntaje:"
        score = llm.invoke(prompt)
        scored_docs.append((doc, int(score.content)))

    # Ordenar por puntaje descendente
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    state["documents"] = [doc for doc, _ in scored_docs[:3]]

    return state
```

## Costos de OpenAI

### Estimación de costos típicos:

**Embeddings** (text-embedding-3-small):
- $0.02 / 1M tokens
- 1000 documentos ≈ $0.02

**LLM** (gpt-4-turbo-preview):
- Input: $10 / 1M tokens
- Output: $30 / 1M tokens
- 100 queries ≈ $0.50

**Total mensual** (uso moderado): ~$10-20

### Tips para reducir costos:
- Usar `gpt-3.5-turbo` en lugar de GPT-4
- Reducir `chunk_size` y `num_sources`
- Cachear embeddings
- Usar `text-embedding-3-small`

## Troubleshooting

### Error: "OPENAI_API_KEY no está configurada"
```bash
# Verificar que .env existe
cat .env

# Exportar manualmente
export OPENAI_API_KEY=sk-...
python server.py
```

### Error: Rate limit OpenAI
```python
# Agregar reintentos en server.py
from openai import OpenAI
client = OpenAI(
    max_retries=3,
    timeout=60.0
)
```

### ChromaDB muy lento
```bash
# Limpiar y recrear
rm -rf chroma_db/
python server.py
# Recargar documentos
```

### Respuestas de baja calidad
```python
# Aumentar número de fuentes
query_rag(question="...", num_sources=5)

# Usar modelo más potente
OPENAI_MODEL=gpt-4
```

## Seguridad

⚠️ **IMPORTANTE**:

- Nunca commitear `.env` con tu API key
- Usar variables de entorno en producción
- Implementar rate limiting
- Validar inputs del usuario
- Monitorear costos de OpenAI

## Ejemplos de Grafos Avanzados

### 1. Grafo con Retry
```python
def should_retry(state):
    if state["answer_quality"] < 0.7:
        return "retrieve"  # Volver a buscar
    return END

workflow.add_conditional_edges("generate", should_retry)
```

### 2. Grafo con Paralelización
```python
# Buscar en múltiples fuentes en paralelo
workflow.add_node("retrieve_docs", retrieve_documents)
workflow.add_node("retrieve_web", retrieve_web_results)

# Ambos nodos se ejecutan en paralelo
workflow.set_entry_point("retrieve_docs")
workflow.set_entry_point("retrieve_web")

workflow.add_edge(["retrieve_docs", "retrieve_web"], "merge")
```

## Casos de Uso

### 1. Knowledge Base Empresarial
```python
# Cargar toda la documentación
load_documents("./company_docs", ["pdf", "md", "txt"])

# Consultar con contexto
query_rag("¿Cuál es la política de vacaciones?")
```

### 2. Análisis Multi-documento
```python
# Pregunta compleja que requiere múltiples pasos
multi_step_reasoning(
    "Compara las políticas de privacidad de nuestros productos A, B y C",
    max_steps=4
)
```

### 3. Chatbot Conversacional
```python
# Mantener historial de conversación
history = []
response1 = query_rag("¿Qué es LangGraph?", chat_history=history)
history.append({"role": "user", "content": "¿Qué es LangGraph?"})
history.append({"role": "assistant", "content": response1["answer"]})

response2 = query_rag("¿Cuáles son sus ventajas?", chat_history=history)
```

## Referencias

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [ChromaDB](https://www.trychroma.com/)
- [FastMCP](https://github.com/jlowin/fastmcp)

## Próximos Pasos

- [ ] Implementar re-ranking de documentos
- [ ] Agregar soporte para imágenes (GPT-4 Vision)
- [ ] Implementar cache de embeddings
- [ ] Agregar métricas de calidad de respuestas
- [ ] Soporte para streaming de respuestas
- [ ] Integración con bases de datos vectoriales en la nube

---

**¡LangGraph + OpenAI = RAG Profesional! 🚀**
