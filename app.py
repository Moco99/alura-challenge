import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from chain import RagAgent

st.set_page_config(
    page_title="Pegasus Agente",
    layout="centered",
)


@st.cache_resource
def cargar_agente() -> RagAgent:
    return RagAgent()


agente = cargar_agente()

st.title("Pegasus Agente")
st.caption("Preguntas sobre documentación interna de Santos Pegasus Soluciones.")
