from helper import GEMINI_API_KEY, GEMINI_EMBBEDINGS_MODEL, GEMINI_MODEL
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from ingest import chunks

modelo_embbedings = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBBEDINGS_MODEL, google_api_key=GEMINI_API_KEY)
vectorstore = FAISS.from_documents(chunks, modelo_embbedings)