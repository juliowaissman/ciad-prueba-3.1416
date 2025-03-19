import streamlit as st

# 📌 Configurar pantalla completa (DEBE SER LA PRIMERA INSTRUCCIÓN)
st.set_page_config(
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_title="Análisis de Productos 2024",
    page_icon="📚"
)

# 📌 Importar módulos después de configurar Streamlit
import sankey
import erdos

st.title("Ejemplo de análisis de datos de producción científica")

tab1, tab2 = st.tabs([
    "**📚 Agregados por tipo y por coordinación**", 
    "**🔗 Grafo de Colaboraciones**"
])

with tab1:
    sankey.sankey_chart()

with tab2:
    erdos.erdos_graph()
