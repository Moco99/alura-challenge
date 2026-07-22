import time
from pathlib import Path

from helper import GEMINI_API_KEY, GEMINI_EMBBEDINGS_MODEL, GEMINI_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from ingest import DocsIngestor

FAISS_INDEX_DIR = Path(__file__).resolve().parent.parent / "data" / "faiss_index"

#despues de que no me dejara hacer el embed tuve que agregar que se haga por partes para no superar el limite

EMBED_BATCH_SIZE = 5
EMBED_BATCH_DELAY_SECONDS = 10
EMBED_MAX_REINTENTOS = 5
EMBED_REINTENTO_ESPERA_SEGUNDOS = 30


class VectorStore():
    def __init__(self):
        self.vectorstore = None
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBBEDINGS_MODEL, google_api_key=GEMINI_API_KEY)

    def _embeder_con_reintentos(self, vectorstore, lote):
        for intento in range(1, EMBED_MAX_REINTENTOS + 1):
            try:
                if vectorstore is None:
                    return FAISS.from_documents(lote, self.embeddings_model)
                vectorstore.add_documents(lote)
                return vectorstore
            except Exception as error:
                if "RESOURCE_EXHAUSTED" not in str(error) or intento == EMBED_MAX_REINTENTOS:
                    raise
                print(f"Cupo agotado, reintento {intento}/{EMBED_MAX_REINTENTOS} en {EMBED_REINTENTO_ESPERA_SEGUNDOS}s...")
                time.sleep(EMBED_REINTENTO_ESPERA_SEGUNDOS)

    def _construir_indice(self, chunks):
        vectorstore = None
        for inicio in range(0, len(chunks), EMBED_BATCH_SIZE):
            lote = chunks[inicio:inicio + EMBED_BATCH_SIZE]
            vectorstore = self._embeder_con_reintentos(vectorstore, lote)
            if inicio + EMBED_BATCH_SIZE < len(chunks):
                time.sleep(EMBED_BATCH_DELAY_SECONDS)
        return vectorstore

    def retrieve(self):
        if (FAISS_INDEX_DIR / "index.faiss").exists():
            self.vectorstore = FAISS.load_local(
                str(FAISS_INDEX_DIR),
                self.embeddings_model,
                allow_dangerous_deserialization=True,
            )
        else:
            chunks = DocsIngestor().ingest_docs()
            self.vectorstore = self._construir_indice(chunks)
            FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
            self.vectorstore.save_local(str(FAISS_INDEX_DIR))

        retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold",
                                                 search_kwargs={"score_threshold": 0.3,"k":4}
                                                )
        return retriever