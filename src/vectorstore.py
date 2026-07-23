from pathlib import Path

from helper import EMBEDDINGS_MODEL
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from ingest import DocsIngestor

FAISS_INDEX_DIR = Path(__file__).resolve().parent.parent / "data" / "faiss_index"


class VectorStore():
    def __init__(self):
        self.vectorstore = None
        self.embeddings_model = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

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

        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})
        return retriever
