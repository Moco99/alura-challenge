from pathlib import Path

from helper import GEMINI_API_KEY, GEMINI_EMBBEDINGS_MODEL, GEMINI_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from ingest import DocsIngestor

FAISS_INDEX_DIR = Path(__file__).resolve().parent.parent / "data" / "faiss_index"


class VectorStore():
    def __init__(self):
        self.vectorstore = None
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBBEDINGS_MODEL, google_api_key=GEMINI_API_KEY)

    def retrieve(self):
        if (FAISS_INDEX_DIR / "index.faiss").exists():
            self.vectorstore = FAISS.load_local(
                str(FAISS_INDEX_DIR),
                self.embeddings_model,
                allow_dangerous_deserialization=True,
            )
        else:
            chunks = DocsIngestor().ingest_docs()
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings_model)
            FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
            self.vectorstore.save_local(str(FAISS_INDEX_DIR))

        retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold",
                                                 search_kwargs={"score_threshold": 0.3,"k":4}
                                                )
        return retriever