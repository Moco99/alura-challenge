from helper import GEMINI_API_KEY, GEMINI_EMBBEDINGS_MODEL, GEMINI_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from ingest import DocsIngestor

class VectorStore():
    def __init__(self):
        self.chunks = DocsIngestor().ingest_docs()
        self.vectorstore = None
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBBEDINGS_MODEL, google_api_key=GEMINI_API_KEY)

    def retrieve(self):
        self.vectorstore = FAISS.from_documents(self.chunks, self.embeddings_model)
        retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold", 
                                                 search_kwargs={"score_threshold": 0.3,"k":4} 
                                                )
        return retriever