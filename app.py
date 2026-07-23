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


MAX_CITAS_POR_FILA = 4


def render_citas(citas: list) -> None:
    if not citas:
        return
    for inicio in range(0, len(citas), MAX_CITAS_POR_FILA):
        fila = citas[inicio:inicio + MAX_CITAS_POR_FILA]
        columnas = st.columns(MAX_CITAS_POR_FILA)
        for columna, cita in zip(columnas, fila):
            with columna:
                with st.popover(cita["etiqueta"], icon=":material/link:", use_container_width=True):
                    st.caption("Fragmento citado")
                    st.write(cita["contenido"])


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

if "messages" not in st.session_state:
    st.session_state.messages = []

for mensaje in st.session_state.messages:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])
        if mensaje["role"] == "assistant":
            if mensaje.get("documentos_encontrados"):
                render_citas(mensaje.get("citaciones", []))
            else:
                st.markdown(
                    '<span class="no-answer-badge">Sin coincidencias en la documentación.</span>',
                    unsafe_allow_html=True,
                )

pregunta = st.chat_input("Escribe tu pregunta...")

if pregunta:
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en la documentación..."):
            resultado = agente.busqueda_de_respuestas_RAG(pregunta)
        st.write(resultado["respuesta"])
        if resultado["documentos_encontrados"]:
            render_citas(resultado["citaciones"])
        else:
            st.markdown(
                '<span class="no-answer-badge">Sin coincidencias en la documentación.</span>',
                unsafe_allow_html=True,
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resultado["respuesta"],
            "citaciones": resultado.get("citaciones", []),
            "documentos_encontrados": resultado.get("documentos_encontrados", False),
        }
    )
