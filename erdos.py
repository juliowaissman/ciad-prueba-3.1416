import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import re

@st.cache_data
def load_data():
    """Carga los datos desde CSV y filtra solo los tipos de producto permitidos"""
    file_path = "productos_validados.csv"
    df = pd.read_csv(file_path)

    # Definir los tipos de producto permitidos
    tipos_permitidos = [
        'Artículo científico', 'Capítulo de libro', 'Libro',
        'Publicaciones derivadas de eventos colectivos',
        'Subcapítulo o artículo de libro', 'Informe interno anual de actividades'
    ]

    # Filtrar el DataFrame para incluir solo los productos válidos
    df = df[df["tipo_producto"].isin(tipos_permitidos)]

    return df

def erdos_graph():
    df = load_data()

    # Extraer solo los nombres de *Autores de correspondencia sin instituciones y sin separaciones incorrectas
    def extraer_autores_correspondencia(texto):
        if isinstance(texto, str):
            texto_limpio = re.sub(r"\(.*?\)", "", texto)  
            autores_limpios = [autor.strip().lstrip("*") for autor in texto_limpio.split(";") if autor.strip()]
            return autores_limpios
        return []

    df["autores_correspondencia"] = df["*Autor de correspondencia"].apply(extraer_autores_correspondencia)

    # Lista única de autores de correspondencia para la selección
    autores_correspondencia_unicos = sorted(set(df["autores_correspondencia"].explode().dropna()))

    st.subheader("Red de Colaboraciones basada en el Número de Erdős")

    # Selección de autor base
    selected_author = st.selectbox("Selecciona un investigador base:", autores_correspondencia_unicos)

    # Lista completa de todos los tipos de productos posibles
    all_product_types = df["tipo_producto"].dropna().unique()

    # Filtrar los productos en los que ha participado el autor seleccionado
    productos_participacion = df[df["autores_correspondencia"].apply(lambda autores: selected_author in autores)]["tipo_producto"]

    # Contar la cantidad de productos por tipo
    productos_count = productos_participacion.value_counts().reindex(all_product_types, fill_value=0).reset_index()
    productos_count.columns = ["Tipo de Producto", "Cantidad"]

    # Filtrar solo los tipos de productos con al menos 1 participación
    productos_count = productos_count[productos_count["Cantidad"] > 0]

    # Mostrar tabla y gráfica solo si hay datos
    if not productos_count.empty:
        st.write(f"Productos en los que ha participado {selected_author}:")
        st.dataframe(productos_count)

        # Crear la gráfica de barras
        fig_bar = px.bar(productos_count, x="Tipo de Producto", y="Cantidad", 
                         title=f"Distribución de Tipos de Producto para {selected_author}",
                         labels={"Cantidad": "Número de Productos", "Tipo de Producto": "Tipo de Producto"},
                         text="Cantidad")

        # Mostrar gráfica
        st.plotly_chart(fig_bar, use_container_width=True)

    # Filtrar los proyectos en los que ha participado
    proyectos_participacion = df[df["autores_correspondencia"].apply(lambda autores: selected_author in autores)][["titulo", "Autores | *Autor de correspondencia | ªEstudiante"]].dropna()

    # Mostrar lista de proyectos solo si existen
    if not proyectos_participacion.empty:
        st.write(f"Productos en los que ha participado {selected_author}:")
        for _, row in proyectos_participacion.iterrows():
            titulo = row["titulo"]
            autores = row["Autores | *Autor de correspondencia | ªEstudiante"]

            # Verificar si el autor fue "Autor de correspondencia" y agregar * al inicio del título
            if any(persona.strip().lstrip("*") == selected_author and persona.startswith("*") for persona in autores.split(";")):
                st.write(f"🔹 *{titulo}")  # Agregar * al inicio del título
            else:
                st.write(f"🔹 {titulo}")

    # Extraer todos los nombres de la columna "Autores | *Autor de correspondencia | ªEstudiante"
    def extraer_todos_autores(texto):
        autores, estudiantes = [], []
        if isinstance(texto, str):
            for persona in texto.split(";"):
                persona = persona.strip().lstrip("*")
                if "ª" in persona:
                    persona = persona.replace("ª", "").strip()
                    estudiantes.append(persona)
                else:
                    autores.append(persona)
        return autores, estudiantes

    df["autores"], df["estudiantes"] = zip(*df["Autores | *Autor de correspondencia | ªEstudiante"].apply(extraer_todos_autores))

    # Construcción del grafo considerando solo los autores de la columna "Autores | *Autor de correspondencia | ªEstudiante"
    G = nx.Graph()
    for _, row in df.iterrows():
        todos_participantes = row["autores"] + row["estudiantes"]
        for i in range(len(todos_participantes)):
            for j in range(i + 1, len(todos_participantes)):
                G.add_edge(todos_participantes[i], todos_participantes[j])

    # Cálculo del número de Erdős (máx. 2 niveles)
    erdos_numbers = nx.single_source_shortest_path_length(G, selected_author) if selected_author in G else {}
    max_erdos = min(max(erdos_numbers.values(), default=1), 2)
    erdos_options = list(range(1, max_erdos + 1)) if max_erdos > 0 else []

    if not erdos_options:
        st.warning("Este investigador no tiene conexiones más allá de sí mismo.")
    else:
        selected_erdos = st.selectbox("Selecciona el número de Erdős (máx. 2):", erdos_options)

        # Filtrar nodos dentro del número de Erdős seleccionado
        filtered_nodes = {node: distance for node, distance in erdos_numbers.items() if distance <= selected_erdos}
        G_filtered = nx.Graph()

        # Construcción del grafo con restricciones de conexión
        for node, level in filtered_nodes.items():
            if level == 1:
                G_filtered.add_edge(selected_author, node)
            elif level > 1:
                for neighbor in G.neighbors(node):
                    if neighbor in filtered_nodes and erdos_numbers[neighbor] == level - 1:
                        G_filtered.add_edge(node, neighbor)

        pos = nx.spring_layout(G_filtered, seed=42)

        edge_x, edge_y, node_x, node_y, node_color, node_text = [], [], [], [], [], []
        estudiantes_list = set(df["estudiantes"].explode().dropna())

        for edge in G_filtered.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        for node in G_filtered.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            if node == selected_author:
                node_color.append("yellow")
            elif node in estudiantes_list:
                node_color.append("red")
            else:
                node_color.append("blue")

        fig_graph = go.Figure()
        fig_graph.add_trace(go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='white'), mode='lines'))
        fig_graph.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers', marker=dict(size=10, color=node_color), text=node_text, hoverinfo='text'))

        # Fondo personalizado y sin ejes
        fig_graph.update_layout(
            title="Grafo de Colaboraciones con Número de Erdős",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            plot_bgcolor="#0f1116",
            paper_bgcolor="#0f1116",
            font=dict(color="white")
        )

        st.plotly_chart(fig_graph, use_container_width=True)



