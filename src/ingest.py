from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"

class DocsIngestor():
    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.docs_dir = docs_dir

    def ingest_docs(self):
        docs = []
        for pdf in self.docs_dir.glob("*.pdf"):
            try:
                loader = PyMuPDFLoader(str(pdf))
                docs.extend(loader.load())
                print(f"PDF {pdf.name} Exitosamente cargado con {len(docs)} páginas.")
            except Exception as e:
                print(f"Error al cargar el PDF {pdf.name}: {e}")

        #split y chunking de los docs, dejamos 150 de overlap para que el modelo pueda entender el contexto en documentos con tablas largas
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(docs)
        return chunks
