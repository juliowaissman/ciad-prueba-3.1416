import streamlit as st

# 📌 Configurar pantalla completa (DEBE SER LA PRIMERA INSTRUCCIÓN)
st.set_page_config(layout="wide", page_title="Análisis de Productos Validados 2024")

# 📌 Importar módulos después de configurar Streamlit
import sankey
import erdos

st.title("📊 Productos por tipo y por coordinación")

tab1, tab2 = st.tabs(["📊 Diagrama de Sankey", "🔗 Grafo de Colaboraciones (Erdős)"])

with tab1:
    sankey.sankey_chart()

with tab2:
    erdos.erdos_graph()
