import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from chain import RagAgent

st.set_page_config(
    page_title="Pegasus Agente",
    layout="centered",
)


#vamos a darle formato bonito a nuestro agente de RAG ;)

PALETTE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 700;
    color: #1F3B4D;
}

.stChatMessage {
    border: 1px solid #D8D2C2;
    border-radius: 10px;
}

.citation-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #B5652D;
    background-color: #F1E4D8;
    border-radius: 4px;
    padding: 2px 6px;
    margin-right: 4px;
    display: inline-block;
}

.no-answer-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #8A8578;
}
</style>
"""
st.markdown(PALETTE_CSS, unsafe_allow_html=True)


@st.cache_resource
def cargar_agente() -> RagAgent:
    return RagAgent()


agente = cargar_agente()

with st.sidebar:
    st.markdown("### Pegasus Agente")
    st.write(
        "Asistente interno de **Santos Pegasus Soluciones** para consultar "
        "el manual de onboarding, las guías de ingeniería back-end y "
        "front-end, el protocolo de incidentes y la arquitectura de "
        "microservicios."
    )
    st.markdown("**Ejemplos de preguntas:**")
    st.markdown(
        "- ¿Qué debo hacer si hay un incidente en producción?\n"
        "- ¿Qué lenguajes se usan en el back-end?\n"
        "- ¿Cómo está organizada la arquitectura de microservicios?"
    )

st.title("Pegasus Agente")
st.caption("Preguntas sobre documentación interna de Santos Pegasus Soluciones.")
