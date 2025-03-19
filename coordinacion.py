import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

@st.cache_data
def load_data():
    file_path = "productos_validados.csv"
    df = pd.read_csv(file_path)
    return df

def graficos():
    df = load_data()
    
    # Filtro de Coordinaciones 
    seleccionadas = st.multiselect(
        "Seleccionar Coordinaciones", 
        sorted(df["coordinacion"].dropna().unique()),
        help="Selecciona una o más coordinaciones para filtrar los productos"
    )
    if seleccionadas:
        df_coord = df[df["coordinacion"].isin(seleccionadas)] 
    else:
        st.warning("Selecciona al menos una coordinación para visualizar los datos") 
        return None
    
    st.subheader("Relación de productos validados por coordinación")

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
    cat_labels = {
        'Publicaciones': 'tipos_publicación',
        'Editor/Revisor': 'tipos_editor_revisor',
        'Reconocimientos obtenidos': 'tipo_reconocimiento',
        'Organización de eventos': 'tipo_eventos'
    }
    categoria_seleccionada = st.selectbox(
        "Selecciona una categoría:", list(cat_labels.keys()), index=0
    ) 
    lista_tipos = categorias[cat_labels[categoria_seleccionada]]

    # Filtrar el dataframe para que solo muestre productos de la categoría seleccionada
    df_filtrado = df_coord[df_coord["tipo_producto"].isin(lista_tipos)]
    

    # Construcción del Sankey con subcategorías de la categoría seleccionada
    source, target, values = [], [], []
    
    if categoria_seleccionada == "Publicaciones":
        labels = (seleccionadas + lista_tipos 
                  + ["Corresp. CIAD", "Corresp. no CIAD"] 
                  + ["Con estudiantes", "Sin estudiantes"])
        label2idx = {label: idx for idx, label in enumerate(labels)}
        
        # de Coordinaciones a tipo de publicación
        serie_CT = df_filtrado.groupby(
            ['coordinacion', 'tipo_producto'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CT.index)
        target.extend(label2idx[x[1]] for x in serie_CT.index)
        values.extend(serie_CT.tolist())
        
        # de tipo de publicación a Corresp. CIAD o Corresp. no CIAD 
        df_filtrado['provCA'] = (
            df_filtrado['*Autor de correspondencia']
            .str.extract(r'(\([^\*]*\))')
            .replace({r'\(|\)': ''}, regex=True)
            .isin(df['coordinacion'].unique())
        )
        df_filtrado['CA'] = 'Corresp. no CIAD'
        df_filtrado.loc[df_filtrado['provCA'], 'CA'] = 'Corresp. CIAD'
        serie_CC = df_filtrado.groupby(['tipo_producto', 'CA'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CC.index)
        target.extend(label2idx[x[1]] for x in serie_CC.index)
        values.extend(serie_CC.tolist())
        
        # de tipo CIAD a colaboración de estudiantes
        str_choro = 'Autores | *Autor de correspondencia | ªEstudiante'
        df_filtrado['estudiante'] = df_filtrado[str_choro].str.contains('ª')
        df_filtrado['est'] = 'Sin estudiantes'
        df_filtrado.loc[df_filtrado['estudiante'], 'est'] = 'Con estudiantes'
        serie_CE = df_filtrado.groupby(['CA', 'est'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CE.index)
        target.extend(label2idx[x[1]] for x in serie_CE.index)
        values.extend(serie_CE.tolist())
        
    elif categoria_seleccionada == "Editor/Revisor" and df_filtrado.shape[0] > 0:
        subtipos = ['indizada (ISI, CYT)', 'indizada (otros indices)',
                    'no indizada', 'por solicitud de estancias externas',
                    'institución o asociación académica', 'editorial reconocida']
        labels = seleccionadas + lista_tipos + subtipos
        label2idx = {label: idx for idx, label in enumerate(labels)}
        
        # de Coordinaciones a tipo de editor/revisor
        serie_CT = df_filtrado.groupby(
            ['coordinacion', 'tipo_producto'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CT.index)
        target.extend(label2idx[x[1]] for x in serie_CT.index)
        values.extend(serie_CT.tolist())
        
        # de tipo de editor/revisor a indización
        df_filtrado['sub'] = 'Otro'
        for subtipo in subtipos:
            df_filtrado \
             .loc[df_filtrado['subtipo_producto'] \
             .str.contains(subtipo, regex=False), 'sub'] = subtipo
        serie_CC = df_filtrado.groupby(['tipo_producto', 'sub'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CC.index)
        target.extend(label2idx[x[1]] for x in serie_CC.index)
        values.extend(serie_CC.tolist())
    
    elif categoria_seleccionada == "Reconocimientos obtenidos" and df_filtrado.shape[0] > 0:
        labels = (seleccionadas + lista_tipos 
                  + ['Nivel 1', 'Nivel 2', 'Nivel 3']
                  + ['Nacional', 'Internacional'])
        label2idx = {label: idx for idx, label in enumerate(labels)}
        
        # de Coordinaciones a tipo de reconocimiento
        serie_CT = df_filtrado.groupby(
            ['coordinacion', 'tipo_producto'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CT.index)
        target.extend(label2idx[x[1]] for x in serie_CT.index)
        values.extend(serie_CT.tolist())
        
        # Nivel de SNI
        if 'Sistema Nacional de Investigadores' in df_filtrado['tipo_producto'].unique(): 
            df_SNI = df_filtrado[df_filtrado['tipo_producto'] == 'Sistema Nacional de Investigadores']
            serie_SNI = df_SNI.groupby(['tipo_producto', 'subtipo_producto'])['id_producto'].count()
            source.extend(label2idx[x[0]] for x in serie_SNI.index)
            target.extend(label2idx[x[1]] for x in serie_SNI.index)
            values.extend(serie_SNI.tolist())
        if 'Premios' in df_filtrado['tipo_producto'].unique():
            df_premios = df_filtrado[df_filtrado['tipo_producto'] == 'Premios']
            serie_premios = df_premios.groupby(['tipo_producto', 'ambito'])['id_producto'].count()
            source.extend(label2idx[x[0]] for x in serie_premios.index)
            target.extend(label2idx[x[1]] for x in serie_premios.index)
            values.extend(serie_premios.tolist())
    elif categoria_seleccionada == "Organización de eventos" and df_filtrado.shape[0] > 0:
        labels = seleccionadas + lista_tipos + ['Regional', 'Nacional', 'Internacional']
        label2idx = {label: idx for idx, label in enumerate(labels)}
        
        # de Coordinaciones a tipo de evento
        serie_CT = df_filtrado.groupby(
            ['coordinacion', 'tipo_producto'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CT.index)
        target.extend(label2idx[x[1]] for x in serie_CT.index)
        values.extend(serie_CT.tolist())
        
        # de tipo de evento a ámbito
        serie_CC = df_filtrado.groupby(['tipo_producto', 'ambito'])['id_producto'].count()
        source.extend(label2idx[x[0]] for x in serie_CC.index)
        target.extend(label2idx[x[1]] for x in serie_CC.index)
        values.extend(serie_CC.tolist())
        
        
    if source:
        fig_sankey = go.Figure(
            go.Sankey(
                node=dict(
                    pad=15, thickness=15, label=labels
                ),
                link=dict(
                    source=source, target=target, value=values, #color="lightsalmon"
                )
            )
        )
        fig_sankey.update_layout( 
            font=dict(color = 'red', size = 16, shadow='off')
        )
        st.plotly_chart(fig_sankey, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar en el gráfico Sankey") 
           
    st.subheader("Impacto de artículos por coordinación")
    
    df_articulos = df[df['tipo_producto'] == 'Artículo científico']
    fig_box = px.box(
        df_articulos, x='coordinacion', y='factor_impacto',
        points="all",
        labels={
            "factor_impacto": "Factor de Impacto", 
            "coordinacion": "Coordinación"}
    )
    fig_box.update_traces(quartilemethod="exclusive") 
    # "exclusive", "inclusive", "linear" 
    st.plotly_chart(fig_box, use_container_width=True)
    

