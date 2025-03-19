import streamlit as st
import pandas as pd
import datetime
import pytz
from itables.streamlit import interactive_table
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import io
import requests
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import seaborn as sns
import plotly.express as px
import funciones_generales as fg

# Set page config
st.set_page_config(page_title="Streamlit Dashboard", layout="wide")
# Define function to get today's date in Lima timezone
def fecha_peru_hoy():
    lima_timezone = pytz.timezone('America/Lima')
    lima_time = datetime.datetime.now(lima_timezone)
    return lima_time.date()

today_string = fecha_peru_hoy().strftime('%y%m%d')

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



st.set_page_config(page_title="Streamlit Dashboard", layout="wide")

@st.cache_data
def load_data():
    folder_id = '17E4c2ShTX0jbH3_4REOv5oCTY2_ypSxZ'
    archivos_descargados = fg.obtener_archivos_drive(folder_id)
    data_pago=pd.read_excel('Master_Pagos.xlsx')
    df, data2, data3 = None, None, None
    for archivo_name, archivo_content in archivos_descargados:
        try:    
            print(f"Procesando archivo: {archivo_name}...")
            if archivo_name.endswith('.xlsx') and df is None:
                df = pd.read_excel(io.BytesIO(archivo_content), engine='openpyxl')
                print("Archivo Excel cargado correctamente.")
                
            elif 'bbdd_ucal2' in archivo_name:
                data2 = pd.read_csv(io.BytesIO(archivo_content), dtype=str)
                data2.columns = data2.columns.str.strip().str.replace(' ', '_')
            elif 'bbdd_ucal3' in archivo_name:
                data3 = pd.read_csv(io.BytesIO(archivo_content), dtype=str)
                data3.columns = data3.columns.str.strip().str.replace(' ', '_')
            elif archivo_content.startswith(b'<!DOCTYPE html>'):
                print("Error: Se intentó descargar una página en lugar de un CSV")
        except Exception as e:
            
            
            print(f"Error al procesar {archivo_name}: {e}")
    return df, data2, data3,data_pago 
# Cargar datos
df, data2, data3 ,data_pago= load_data()
# Verificar si los datos se cargaron correctamente
if df is None or data2 is None or data3 is None:
    st.error("Hubo un problema al cargar los datos. Por favor, revisa los archivos en Google Drive.")
else:
    # Título del dashboard con formato de Streamlit
    st.markdown(
        """   
        <h1 style="background: linear-gradient(90deg, #1E90FF, #8A2BE2, #4169E1); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            font-size: 50px; 
            text-align: center; 
            font-weight: bold; 
            margin-bottom: 20px;">
            Dashboard UCAL 25.1
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Resumen de métricas de conversión
    st.markdown(
        '<h3 style="color:#7E57C2;">Resumen de métricas CONVERSIÓN</h3>',
        unsafe_allow_html=True
    )

    # Selección de la base de datos
    col1, col2 = st.columns(2)
    with col1:
        agrupaciones = ["Real", "Espejo"]
        agrupacion_seleccionada = st.selectbox("Seleccione Base", options=agrupaciones)
        if agrupacion_seleccionada == "Real":
            data2 = data2
        else:
            data2 = data3
# Helper function to format numbers with commas
def format_with_commas(number):
    return f"{number:,}"

# Define logic to classify careers into worlds
def clasificar_mundo(ult_programa_interes):
    if ult_programa_interes in [
        "COMUNICACIÓN", "COMUNICACIÓN AUDIOVISUAL Y CINE", "COMUNICACIÓN Y PUBLICIDAD TRANSMEDIA"
    ]:
        return "MUNDO COMUNICACIONES"
    elif ult_programa_interes in ["ARQUITECTURA", "ARQUITECTURA DE INTERIORES"]:
        return "MUNDO ARQUITECTURA"
    elif ult_programa_interes == "DISEÑO GRÁFICO PUBLICITARIO":
        return "MUNDO DISEÑO"
    elif ult_programa_interes in [
        "ADMINISTRACION", "ADMINISTRACIÓN Y MARKETING", "MARKETING E INNOVACIÓN",
        "ADMINISTRACIÓN Y NEGOCIOS INTERNACIONALES"
    ]:
        return "MUNDO NEGOCIOS"
    elif ult_programa_interes == "PSICOLOGÍA":
        return "MUNDO PSICOLOGIA"
    elif ult_programa_interes in ["DISEÑO ESTRATÉGICO", "INGENIERIA INDUSTRIAL"]:
        return "PORTAFOLIO ANTIGUO"
    elif ult_programa_interes == "SIN CARRERA":
        return "SIN CARRERA"


# Add a calculated column for Mundo
# Asignar 'SIN CARRERA' a las celdas vacías o nulas
df['ult_programa_interes'] = df['ult_programa_interes'].fillna('SIN CARRERA')
data2['ult_programa_interes'] = data2['ult_programa_interes'].fillna('SIN CARRERA')

df['MUNDO_CALCULADO'] = df['ult_programa_interes'].apply(clasificar_mundo)
data2['MUNDO_CALCULADO'] = data2['ult_programa_interes'].apply(clasificar_mundo)


df['flg_traslados'] = df['flg_traslados'].replace({0: 'Nuevo', 1: 'Traslado'})

df['flg_convocatoria'] = df['flg_convocatoria'].replace({0: 'No Convo', 1: 'Convo'})


with st.sidebar:
    st.header("Filtros")
    
    # Filtro de mundos
    mundos_disponibles = ["TODAS LAS CARRERAS"] + df['MUNDO_CALCULADO'].dropna().unique().tolist()
    mundo_seleccionado = st.selectbox("Selecciona un mundo", options=mundos_disponibles)
    
    # Filtro de carreras dinámico según el mundo seleccionado
    if mundo_seleccionado == "TODAS LAS CARRERAS":
        carreras_disponibles = df['ult_programa_interes'].dropna().unique()
        carreras_disponibles = data2['ult_programa_interes'].dropna().unique()
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["Todas"] + list(carreras_disponibles))

    elif mundo_seleccionado != "SIN CARRERA":
        carreras_disponibles = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]['ult_programa_interes'].dropna().unique()
        carreras_disponibles = data2[data2['MUNDO_CALCULADO'] == mundo_seleccionado]['ult_programa_interes'].dropna().unique()
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["Todas"] + list(carreras_disponibles))

    else:
        carrera_seleccionada = None


filtered_df = df.copy()
filtered_df_2 = data2.copy()

# Filtrar por mundo
if mundo_seleccionado != "TODAS LAS CARRERAS":
    filtered_df = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]
    filtered_df_2=data2[data2['MUNDO_CALCULADO'] == mundo_seleccionado]
    
# Filtrar por mundo
if carrera_seleccionada != "Todas":
    filtered_df = df[(df['MUNDO_CALCULADO'] == mundo_seleccionado) & (df['ult_programa_interes'] == carrera_seleccionada) ]
    filtered_df_2 = data2[(data2['MUNDO_CALCULADO'] == mundo_seleccionado) & (data2['ult_programa_interes'] == carrera_seleccionada) ]

# Filtrar por carrera
if mundo_seleccionado == "SIN CARRERA":

    filtered_df = df[
        (df['MUNDO_CALCULADO'] == "SIN CARRERA") 
    ]
    filtered_df_2 = data2[
        (data2['MUNDO_CALCULADO'] == "SIN CARRERA") 
    ]
# Mostrar resultados filtrados
with st.sidebar:
    try:
            # Asegurarse de que la columna sea numérica
            filtered_df['dias_sin_contacto'] = pd.to_numeric(filtered_df['dias_sin_contacto'], errors='coerce')

            # Calcular el mínimo y el máximo
            min_dias = int(filtered_df['dias_sin_contacto'].min())
            max_dias = int(filtered_df['dias_sin_contacto'].max())

            # Configurar el slider para seleccionar el rango de días sin contacto
            rango_dias = st.slider(
                "Selecciona el rango de días sin contacto",
                min_dias,
                max_dias,
                (min_dias, max_dias)  # Rango por defecto: mínimo a máximo
            )

            # Filtrar los datos según el rango seleccionado
            filtered_df = filtered_df[
                (filtered_df['dias_sin_contacto'] >= rango_dias[0]) &
                (filtered_df['dias_sin_contacto'] <= rango_dias[1])
            ]
    except ValueError as e:
                st.error(f"Error al procesar la columna 'dias_sin_contacto': {e}")   
    tipo_ingreso =["Todos"] + filtered_df['flg_traslados'].unique().tolist()
    tipo_select= st.selectbox("Tipo Ingreso", options=tipo_ingreso)
    if tipo_select != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['flg_traslados'] == tipo_select]
     # Filtrar los IDs con flg_traslados = 1
     traslados_ids = filtered_df.loc[filtered_df['flg_traslados'] == tipo_select, 'id_prometeo']
    
    # Cruzar los IDs con filtered_df_2
     filtered_df_2 = filtered_df_2[filtered_df_2['id_prometeo'].isin(traslados_ids)]
    
 

    modalidad =["Todos"] + filtered_df['modalidad_programa'].unique().tolist()
    moda_selec= st.selectbox("Modalidad", options=modalidad)
    if moda_selec != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['modalidad_programa'] == moda_selec]
     filtered_df_2 = filtered_df_2[filtered_df_2['modalidad_programa'] == moda_selec]
    
    canales_disponibles =["Todos"] + filtered_df['canal_atribucion'].unique().tolist()
    canal_seleccionado= st.selectbox("Canal", options=canales_disponibles)
    if canal_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['canal_atribucion'] == canal_seleccionado]
     filtered_df_2 = filtered_df_2[filtered_df_2['canal_atribucion'] == canal_seleccionado]
     
     
    subcanales_disponibles =["Todos"] + filtered_df['subcanal'].unique().tolist()
    subcanal_seleccionado= st.selectbox("Subcanal", options=subcanales_disponibles)
    if subcanal_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['subcanal'] == subcanal_seleccionado]
     
     

    Convo =["Todos"] + filtered_df['flg_convocatoria'].unique().tolist()
    Convo_seleccionado= st.selectbox("Convo", options=Convo)
    if Convo_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['flg_convocatoria'] == Convo_seleccionado]
     filtered_df_2 = filtered_df_2[filtered_df_2['flg_convocatoria'] == Convo_seleccionado]
     

col1, col2, col3, col4, col5,col6,col7,col8= st.columns(8)

def calcular_metricas(df):
    """Calcular métricas clave del DataFrame filtrado."""
    sin_contacto = df[df["agrupacion_tipificacion_actual"] == "Sin contacto"].shape[0]
    contactados = df[df["agrupacion_tipificacion_actual"] == "Contactado"].shape[0]
    otros = df[df["agrupacion_tipificacion_actual"] == "Otro"].shape[0]
    total_leads = df["id_prometeo"].nunique()
    return {
        "Sin contacto": sin_contacto,
        "Contactados": contactados,
        "Otros": otros,
        "Total Leads": total_leads,
    }
def mostrar_metricas(metricas):
    """Mostrar métricas clave en la interfaz."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sin contacto", metricas["Sin contacto"])
    col2.metric("Contactados", metricas["Contactados"])
    col3.metric("Otros", metricas["Otros"])
    col4.metric("Total Leads", metricas["Total Leads"])

with col1:
    # Contar la cantidad de leads por ID
    total_leads = filtered_df['id_prometeo'].nunique()
    st.metric("Total Leads", format_with_commas(total_leads))
   
with col2:
     #Contar la cantidad de leads por ID
     convo = filtered_df[filtered_df['flg_convocatoria'] == 'Convo']['id_prometeo'].nunique()
     st.metric("Convo", format_with_commas(convo))
with col3:
    # Contar la cantidad de leads sin contacto
    sin_contacto = filtered_df[filtered_df['agrupacion_tipificacion_actual'] == "VALORES_SIN_CONTACTO"]['id_prometeo'].nunique()
    st.metric("Sin Contacto", format_with_commas(sin_contacto))
with col4:
    # Contar la cantidad de leads volver a llamar
    valp_condition = (
        (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") &
        (filtered_df['ult_tipf_dif_sin_contacto'].isin(["Volver a llamar"]))
    )
    # Contar la cantidad de leads valp
    leads_vll = filtered_df[valp_condition]['id_prometeo'].nunique()
    st.metric("Volver a llamar", format_with_commas(leads_vll))
with col5:
    # Contar la cantidad de leads valp
    valp_condition = (
        (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") &
        (filtered_df['ult_tipf_dif_sin_contacto'].isin(["Interesado", "Evaluando","Volver a llamar"])) &
        (filtered_df['cant_val_pos-vall'] > 0)
    )
    # Contar la cantidad de leads valp
    leads_valp = filtered_df[valp_condition]['id_prometeo'].nunique()
    st.metric("Valp", format_with_commas(leads_valp))
with col6:
    # Contar la cantidad de leads PP
    leads_pp = filtered_df[filtered_df['agrupacion_tipificacion_actual'] == "VALORES_PROMESA_DE_PAGO"]['id_prometeo'].nunique()
    st.metric("PP", format_with_commas(leads_pp))


with col7:
    # Contar la cantidad de leads pagantes
    leads_pagantes = data_pago['ID PROMETEO'].nunique()
    st.metric("Pagantes", format_with_commas(leads_pagantes))


with col8:
    # Contar la cantidad de leads BL
    leads_bl = filtered_df[filtered_df['agrupacion_tipificacion_actual'] == "VALORES_BLACK_LIST"]['id_prometeo'].nunique()
    st.metric("BlackList", format_with_commas(leads_bl))

st.write("")
# Calcular los leads de convocatoria (Convo) para cada categoría
convo_sin_contacto = filtered_df[
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_SIN_CONTACTO") & 
    (filtered_df['flg_convocatoria'] == "Convo")
]['id_prometeo'].nunique()

convo_vll = filtered_df[
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") & 
    (filtered_df['ult_tipf_dif_sin_contacto'].isin(["Volver a llamar"])) & 
    (filtered_df['flg_convocatoria'] == "Convo")
]['id_prometeo'].nunique()

convo_valp = filtered_df[
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") & 
    (filtered_df['ult_tipf_dif_sin_contacto'].isin(["Interesado", "Evaluando", "Volver a llamar"])) & 
    (filtered_df['cant_val_pos-vall'] > 0) & 
    (filtered_df['flg_convocatoria'] == "Convo")
]['id_prometeo'].nunique()

convo_pp = filtered_df[
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_PROMESA_DE_PAGO") & 
    (filtered_df['flg_convocatoria'] == "Convo")
]['id_prometeo'].nunique()

convo_pagantes = filtered_df[
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_PAGANTE") & 
    (filtered_df['flg_convocatoria'] == "Convo")
]['id_prometeo'].nunique()

convo_bl = filtered_df[
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_BLACK_LIST") & 
    (filtered_df['flg_convocatoria'] == "Convo")
]['id_prometeo'].nunique()

# Calcular el total de métricas
total_metrica = sin_contacto + leads_vll + leads_valp + leads_pp + leads_pagantes + leads_bl
total_conv =convo_sin_contacto+convo_vll+convo_valp+convo_pp+convo_pagantes+convo_bl
# Crear un DataFrame con las métricas y sus porcentajes
metricas = {
    "Tipificación":  ["Sin Contacto", "Volver a Llamar", "Val+", "PP", "Pagantes", "Perdidos/BlackList", "Total"],
    "Valor": [sin_contacto, leads_vll, leads_valp, leads_pp, leads_pagantes, leads_bl, total_metrica],
    "Convo": [convo_sin_contacto, convo_vll, convo_valp, convo_pp, convo_pagantes, convo_bl, total_conv],
    "%": [
          f"{(sin_contacto / total_metrica) * 100:.1f}%",
    f"{(leads_vll / total_metrica) * 100:.1f}%",
    f"{(leads_valp / total_metrica) * 100:.1f}%",
    f"{(leads_pp / total_metrica) * 100:.1f}%",
    f"{(leads_pagantes / total_metrica) * 100:.1f}%",
    f"{(leads_bl / total_metrica) * 100:.1f}%",
    "100%"  # Total siempre es 100%
]
}

tabla_metricas = pd.DataFrame(metricas)

# Mostrar la tabla en Streamlit
st.write("")
st.markdown('<h5 style="color:#003399;">Tabla - STATUS DE BASES</h5>', unsafe_allow_html=True)

 # Configurar opciones de la tabla
gb = GridOptionsBuilder.from_dataframe(tabla_metricas)
gb.configure_side_bar()
    # Aplicar estilo al índice (columna "ID")
gb.configure_column("Tipificación", header_name="TIPIFICACION 🔹", cellStyle={'fontWeight': 'bold'})  
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True)
grid_options = gb.build()

col1,col2,col3=st.columns([2.3, 0.5,2])
with col1:
    AgGrid(tabla_metricas, gridOptions=grid_options, fit_columns_on_grid_load=False, height=250, theme="blue", width='100%')

with col2:
   st.write("")
