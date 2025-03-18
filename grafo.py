import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import re

# 📌 Configurar la página en modo ancho
st.set_page_config(layout="wide")

# 📂 Cargar los datos
@st.cache_data
def load_data():
    file_path = "productos_validados.csv"
    df = pd.read_csv(file_path)
    return df

df = load_data()

# 📌 Función para extraer nombres sin asteriscos e incluir "*Pendiente"
def extraer_nombres(autores_str):
    if not isinstance(autores_str, str):
        return []
    
    nombres = []
    for autor in autores_str.split(";"):
        autor = autor.strip()
        autor = re.sub(r"\(.*$", "", autor).strip()  # Remover institución
        autor = autor.lstrip("*")  # Quitar asteriscos
        
        if autor.lower() == "pendiente":  # Si aparece "Pendiente", incluirlo
            nombres.append("Pendiente")

        elif autor:
            nombres.append(autor)
    
    return nombres

df["autores_correspondencia"] = df["*Autor de correspondencia"].apply(extraer_nombres)

# 📌 Crear Grafo de Colaboraciones (Incluir "Pendiente")
G = nx.Graph()
for autores in df["autores_correspondencia"]:
    if len(autores) > 1:
        for i in range(len(autores)):
            for j in range(i + 1, len(autores)):
                G.add_edge(autores[i], autores[j])

# 📌 Interfaz con Tabs en Streamlit
tab1, tab2, tab3 = st.tabs(["📊 Gráfico Sankey", "🔗 Grafo de Colaboraciones (Erdős)", "🌐 Grafo Completo de Colaboraciones"])

with tab3:
    st.subheader("🌐 Grafo Completo de Colaboraciones")

    pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    fig_full_graph = go.Figure()
    fig_full_graph.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#aaa'), hoverinfo='none', mode='lines'))
    fig_full_graph.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers', marker=dict(size=10, color='blue'), text=node_text, hoverinfo='text'))

    fig_full_graph.update_layout(
        title="🌐 Grafo Completo de Colaboraciones entre Investigadores",
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Oculta números en eje X
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Oculta números en eje Y
        margin=dict(b=0, l=0, r=0, t=40),
        height=800,
        width=1200
    )

    st.plotly_chart(fig_full_graph, use_container_width=True)
