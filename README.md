# Pegasus Agente

Agente de inteligencia artificial (RAG) para consultar la documentación interna
de **Santos Pegasus Soluciones**: manual de onboarding, guías de ingeniería
back-end y front-end, protocolo de incidentes y arquitectura de microservicios.

## Arquitectura

- **Ingesta** (`src/ingest.py`): carga los PDFs con `PyMuPDFLoader` y los
  divide en chunks con `RecursiveCharacterTextSplitter` (1000 chars, 150 de
  overlap).
- **Vectorstore** (`src/vectorstore.py`): genera embeddings localmente con
  `HuggingFaceEmbeddings` (`paraphrase-multilingual-MiniLM-L12-v2`, sin costo
  ni límite de requests) y construye un índice FAISS. El índice se persiste en
  `data/faiss_index/` — se calcula una sola vez y queda commiteado en el repo;
  tanto en local como en el deploy se carga directo desde disco, sin volver a
  generar embeddings. Expone un retriever de similitud (`k=4`); la relevancia
  final la decide el LLM según el prompt.
- **Agente** (`src/chain.py`): arma una cadena LCEL
  (`create_stuff_documents_chain`) con Gemini y un `JsonOutputParser` para que
  la respuesta siempre llegue en el formato:
  ```json
  {
    "pregunta": "...",
    "respuesta": "...",
    "citaciones": ["archivo1.pdf", "archivo2.pdf"],
    "documentos_encontrados": true
  }
  ```
- **Frontend** (`app.py`): interfaz de chat en Streamlit, con historial de
  conversación y citas de fuente visibles bajo cada respuesta.

## Tecnologías

Python, LangChain (`langchain-classic`, `langchain-google-genai`), FAISS,
PyMuPDF, Gemini (`gemini-flash-lite-latest`), Streamlit, HuggingFaceEmbeddings

## Cómo ejecutarlo localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # agrega tu GEMINI_API_KEY
streamlit run app.py
```

La primera vez que se ejecuta, se leen los PDFs de `data/docs/` y se construye
el índice FAISS (puede tardar unos segundos); las siguientes ejecuciones
cargan el índice ya guardado en `data/faiss_index/`.

## Ejemplos de preguntas y respuestas

<!-- debo agregar capturas aca -->


## Deploy

<!-- agregar aquí el link público final y una captura de la app corriendo -->
