from vectorstore import VectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from helper import GEMINI_API_KEY, GEMINI_MODEL
from typing import List, TypedDict, Optional,Dict
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser


"""
pregunta : str
respuesta : str
citaciones : [str]
documentos_encontrados : bool


crear un:
document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

necesito un json parser para mantener formato de salida cosistente

"""
class LlmOut(BaseModel):
    pregunta : str
    respuesta: str
    citaciones: List[str]
    documentos_encontrados: bool

parser_json = JsonOutputParser(
    pydantic_object=LlmOut
)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system",
         """
        Eres el especialista en responder preguntas de la empresa Santos Pegasus Soluciones.
        Mas sobre la empresa:\n
        'Empresa de tecnología especializada en el desarrollo de software escalable bajo arquitectura de microservicios y soluciones de Inteligencia Artificial (RAG). 
        Se destaca por sus rigurosos estándares técnicos en ingeniería back-end y front-end, garantizando excelencia operativa y seguridad en infraestructuras de nube (OCI).'\n
        Respondes siempre utilizando los conocimientos del contexto pasado a ti.
        Si no hay informacion sobre la pregunta en el contexto, responde solo 'No lo se'.
        
        """),
        ("human","Contexto:{context}\nPregunta del empleado: {input}")
    ]
).partial(format_instructions=parser_json.get_format_instructions())

def _citaciones_desde_documentos(documentos) -> List[str]:
    return [
        doc.metadata.get("source", f"documento_{i}")
        for i, doc in enumerate(documentos)
    ]

class RagAgent():
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY)
        self.vectorstore = VectorStore()
        self.retriever = self.vectorstore.retrieve()
        self.document_chain = create_stuff_documents_chain(llm=self.llm, prompt=prompt_template,output_parser=parser_json)

    def busqueda_de_respuestas_RAG(self,pregunta)-> Dict:
        documentos_relacionados = self.retriever.invoke(pregunta)

        if not documentos_relacionados:
            return  {
            "respuesta":"No lo se",
            "citaciones": [],
            "documentos_encontrados":False
        }

        answer = self.document_chain.invoke({
            "input":pregunta,
            "context":documentos_relacionados
        })

        if answer["respuesta"].rstrip(".!?") == "No lo se":
            return {
                "respuesta": "No lo se",
                "citaciones": [],
                "documentos_encontrados": False
            }

        return {
            "pregunta": pregunta,
            "respuesta": answer["respuesta"],
            "citaciones": _citaciones_desde_documentos(documentos_relacionados),
            "documentos_encontrados": True
        }