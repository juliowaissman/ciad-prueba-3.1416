import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


df = pd.read_csv("Autores.csv")


investigadores = df["Nombre"].unique().tolist()
instituciones = df["Institución"].unique().tolist()


seleccionado = st.sidebar.radio("Selecciona la vista", ("Investigador", "Institución"))

if seleccionado == "Institución":

    institucion_seleccionada = st.sidebar.selectbox("Selecciona una institución", instituciones)

    investigadores_institucion = df[df["Institución"] == institucion_seleccionada]

    st.write(f"Investigadores de la institución {institucion_seleccionada}")
    st.dataframe(investigadores_institucion[["Nombre"]])

    columnas_proyectos = df.columns[4:-1] 

    proyectos_institucion = investigadores_institucion[columnas_proyectos]
    proyectos_institucion_suma = proyectos_institucion.sum()

    proyectos_institucion_suma = proyectos_institucion_suma[proyectos_institucion_suma > 0]

    proyectos_institucion_suma.index = proyectos_institucion_suma.index.str.replace("No. ", "")

    proyectos_institucion_suma = proyectos_institucion_suma.sort_values(ascending=False)

    st.write(f"Proyectos por tipo en la institución {institucion_seleccionada}")
    st.bar_chart(proyectos_institucion_suma)

else:
    investigador_seleccionado = st.sidebar.selectbox("Selecciona un investigador", ["Todos"] + investigadores)

    if investigador_seleccionado != "Todos":
        st.write(f"Análisis del investigador: {investigador_seleccionado}")

        institucion_investigador = df.loc[df["Nombre"] == investigador_seleccionado, "Institución"].values[0]
        st.write(f"Este investigador pertenece a: {institucion_investigador}")

        columnas_proyectos = df.columns[4:-1]  # Excluye "Nombre", "Institución", "No. Documentos AC" y "No. Documentos No AC"
        proyectos_investigador = df.loc[df["Nombre"] == investigador_seleccionado, columnas_proyectos].values[0]

        proyectos_investigador = dict(zip(columnas_proyectos, proyectos_investigador))
        proyectos_investigador = {k: v for k, v in proyectos_investigador.items() if v > 0}

        proyectos_investigador = dict(sorted(proyectos_investigador.items(), key=lambda item: item[1], reverse=True))

        proyectos_investigador = {k.replace("No. ", ""): v for k, v in proyectos_investigador.items()}

        st.write(f"Proyectos realizados por {investigador_seleccionado}")
        for tipo, cantidad in proyectos_investigador.items():
            st.write(f"{tipo}: {cantidad}")

        st.write("Red de colaboración")
        colaboraciones = eval(df.loc[df["Nombre"] == investigador_seleccionado, "Colaboradores"].values[0])

        G = nx.Graph()
        G.add_node(investigador_seleccionado)  # Nodo principal

        for colaborador, cantidad in colaboraciones.items():
            G.add_node(colaborador)
            G.add_edge(investigador_seleccionado, colaborador, weight=cantidad)

        plt.figure(figsize=(8, 6))
        pos = nx.spring_layout(G)

        edge_widths = [G[u][v]["weight"] for u, v in G.edges()]

        node_size = 5000  

        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color="gray")

        for node, (x, y) in pos.items():
            plt.scatter(x, y, s=node_size, color="lightblue", marker='o')  # Aquí puedes modificar la forma

        nx.draw_networkx_labels(G, pos, font_size=10)

        st.pyplot(plt)

        st.write("Lista de artículos escritos por este investigador (ejemplo)")
        st.write("- Artículo 1")
        st.write("- Artículo 2")
        st.write("- Artículo 3")
