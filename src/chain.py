from pathlib import Path

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

        Responde ÚNICAMENTE con un JSON que cumpla este formato:
        {format_instructions}
        """),
        ("human","Contexto:{context}\nPregunta del empleado: {input}")
    ]
).partial(format_instructions=parser_json.get_format_instructions())

DOCUMENT_LABELS = {
    "1b414aa2-c5ca-40d4-8e9c-8d9e4dcdc955.pdf": "Protocolo de Respuesta a Incidentes y Post-Mortems",
    "359dda5d-7daa-4aa1-832e-fb2843fcf70d.pdf": "Manual de Onboarding para Nuevos Desarrolladores",
    "4a531743-36de-4b0b-b532-b5447b2c1ba7.pdf": "Guía Oficial de Ingeniería Back-end",
    "a4266faf-77bf-4932-99b3-72e452051be2.pdf": "Guía Oficial de Ingeniería Front-end",
    "ddb400f4-475a-4ddc-9ef3-a0cbb2789447.pdf": "Arquitectura de Microservicios y Mapa de Dominios",
}


def _citaciones_desde_documentos(documentos) -> List[dict]:
    vistas = set()
    citas = []
    for doc in documentos:
        nombre_archivo = Path(doc.metadata.get("source", "")).name
        etiqueta_archivo = DOCUMENT_LABELS.get(nombre_archivo, nombre_archivo or "documento desconocido")
        pagina = doc.metadata.get("page")
        clave = (etiqueta_archivo, pagina)
        if clave in vistas:
            continue
        vistas.add(clave)
        etiqueta = f"{etiqueta_archivo} · pág. {pagina + 1}" if pagina is not None else etiqueta_archivo
        citas.append({"etiqueta": etiqueta, "contenido": doc.page_content})
    return citas

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
            "pregunta": pregunta,
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
                "pregunta": pregunta,
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