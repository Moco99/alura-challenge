from helper import GEMINI_API_KEY, GEMINI_EMBBEDINGS_MODEL, GEMINI_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = []
for pdf in Path("../data/docs").glob("*.pdf"):
    try:
        loader = PyMuPDFLoader(str(pdf))
        docs.extend(loader.load())
        print(f"PDF {pdf.name} Exitosamente cargado con {len(docs)} páginas.")
    except Exception as e:
        print(f"Error al cargar el PDF {pdf.name}: {e}")

