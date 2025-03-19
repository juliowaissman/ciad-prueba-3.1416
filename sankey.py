import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_data():
    file_path = "productos_validados.csv"
    df = pd.read_csv(file_path)
    return df

def sankey_chart():
    df = load_data()

    # Diccionario de categorías y sus tipos de producto
    categorias = {
        'tipos_publicación': [
            'Artículo científico', 'Capítulo de libro', 'Libro',
            'Publicaciones derivadas de eventos colectivos',
            'Subcapítulo o artículo de libro', 'Informe interno anual de actividades'
        ],
        'tipos_editor_revisor': [
            'Árbitro de artículos de revista', 'Evaluador de proyectos',
            'Miembro de comité editorial', 'Editor asignado por artículo',
            'Árbitro o dictaminador de capítulo de libro',
            'Árbitro o dictaminador de libro', 'Editor de revista',
            'Coordinador de libro', 'Editor de libro', 'Editor asignado por número especial'
        ],
        'tipo_reconocimiento': [
            'Premios', 'Sistema Nacional de Investigadores',
            'Sistema Sinaloense de Investigadores y Tecnólogos', 'Academia Mexicana de Ciencias'
        ],
        'tipo_eventos': [
            'Conferencias/Congresos/Reuniones Cientificas',
            'Organización de eventos académicos, de extensión y difusión',
            'Otras participaciones en eventos'
        ]
    }

    # Selección de una de las 4 categorías
    cat_labels = {
        'Publicaciones': 'tipos_publicación',
        'Editor/Revisor': 'tipos_editor_revisor',
        'Reconocimientos obtenidos': 'tipo_reconocimiento',
        'Organización de eventos': 'tipo_eventos'
    }
    categoria_seleccionada = st.selectbox(
        "Selecciona una categoría:", list(cat_labels.keys()), index=0
    ) 
    
    # Obtener los tipos de producto asociados a la categoría seleccionada
    tipos_producto_seleccionados = categorias[cat_labels[categoria_seleccionada]]

    # Filtrar el dataframe para que solo muestre productos de la categoría seleccionada
    df_tipo = df[df["tipo_producto"].isin(tipos_producto_seleccionados)]

    # Filtro de Coordinaciones 
    seleccionadas = st.multiselect(
        "Seleccionar Coordinaciones", 
        sorted(df_tipo["coordinacion"].dropna().unique()),
        default=sorted(df_tipo["coordinacion"].dropna().unique()),
        help="Selecciona una o más coordinaciones para filtrar los productos"
    )
    if seleccionadas:
        df_filtrado = df_tipo[df_tipo["coordinacion"].isin(seleccionadas)] 
    else: 
        df_filtrado = df_tipo

    # Construcción del Sankey con subcategorías de la categoría seleccionada
    source, target, values = [], [], []
    subcategorias_unicas = df_filtrado["tipo_producto"].dropna().unique()

    labels = list(df_filtrado["coordinacion"].dropna().unique()) + list(subcategorias_unicas) + ["AC pertenece al CIAD", "AC no pertenece al CIAD", "Sí colaboró un estudiante", "No colaboró un estudiante"]
    label_to_index = {label: idx for idx, label in enumerate(labels)}

    for _, row in df_filtrado.iterrows():
        if row["coordinacion"] in label_to_index and row["tipo_producto"] in label_to_index:
            source.append(label_to_index[row["coordinacion"]])
            target.append(label_to_index[row["tipo_producto"]])
            values.append(1)

        # Asegurar que la columna *Autor de correspondencia tenga un valor válido antes de evaluar si pertenece al CIAD
        pertenece_ciad = "AC no pertenece al CIAD"
        if isinstance(row["*Autor de correspondencia"], str) and "(" in row["*Autor de correspondencia"]:
            pertenece_ciad = "AC pertenece al CIAD"

        if row["tipo_producto"] in label_to_index and pertenece_ciad in label_to_index:
            source.append(label_to_index[row["tipo_producto"]])
            target.append(label_to_index[pertenece_ciad])
            values.append(1)

        # Asegurar que la columna Autores | *Autor de correspondencia | ªEstudiante tenga un valor antes de verificar si colaboró un estudiante
        colaboro_estudiante = "No colaboró un estudiante"
        if isinstance(row["Autores | *Autor de correspondencia | ªEstudiante"], str) and "ª" in row["Autores | *Autor de correspondencia | ªEstudiante"]:
            colaboro_estudiante = "Sí colaboró un estudiante"

        if pertenece_ciad in label_to_index and colaboro_estudiante in label_to_index:
            source.append(label_to_index[pertenece_ciad])
            target.append(label_to_index[colaboro_estudiante])
            values.append(1)

    fig_sankey = go.Figure(
        go.Sankey(
            node=dict(
                pad=15, thickness=15, label=labels, 
                line = dict(color = "magenta", width = 0.5)
            ),
            link=dict(source=source, target=target, value=values)
        )
    )

    fig_sankey.update_layout(
        title_text="Flujo de Productos Validados", 
        font=dict(color = 'red', size = 16, shadow='off')
    )
    st.plotly_chart(fig_sankey, use_container_width=True)




