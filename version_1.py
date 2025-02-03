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

def autenticar_drive():
    gauth = GoogleAuth()
    # Intenta cargar las credenciales almacenadas
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Autenticación si no hay credenciales guardadas
        gauth.LocalWebserverAuth()  # Esto abre un navegador para autorizar la app
        gauth.SaveCredentialsFile("mycreds.txt") 
    elif not gauth.credentials or gauth.access_token_expired:
        if gauth.access_token_expired:
            print("Access token expired. Refreshing...")
        # Solicitar acceso offline para obtener un refresh token
            gauth.LocalWebserverAuth()  # No es necesario el parámetro 'access_type'
            gauth.SaveCredentialsFile("mycreds.txt")  # Guardar las credenciales para la próxima vez
    else:
        # Autorizar con las credenciales guardadas
        gauth.Authorize()

    # Retorna el objeto GoogleDrive con las credenciales autorizadas
    drive = GoogleDrive(gauth)
    return drive

# Función para obtener archivos de una carpeta de Google Drive y descargarlos
def obtener_archivos_drive(folder_id):
    drive = autenticar_drive()
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents"}).GetList()
    archivos_descargados = []
    archivos_vistos = set()  # Evitar duplicados

    for file in file_list:
        file_name = file['title']
        file_id = file['id']
        
        # Verificar si es un archivo válido (CSV o Excel)
        if file_name.endswith(('.csv', '.xlsx')) and file_name not in archivos_vistos:
            print(f"Cargando archivo: {file_name}")
            file_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            try:
                file_content = requests.get(file_url).content
                archivos_descargados.append((file_name, file_content))
                archivos_vistos.add(file_name)
            except Exception as e:
                print(f"Error al descargar {file_name}: {e}")

    return archivos_descargados
# Llamada a la función con el folder ID de tu carpeta de Google Drive


# Función para cargar los datos
@st.cache_data
def load_data():
    folder_id = '17E4c2ShTX0jbH3_4REOv5oCTY2_ypSxZ'
    archivos_descargados = obtener_archivos_drive(folder_id)
    
    df, data2, data3 = None, None, None

    for archivo_name, archivo_content in archivos_descargados:
        try:
            print(f"Procesando archivo: {archivo_name}...")

            if archivo_name.endswith('.xlsx') and df is None:
                df = pd.read_excel(io.BytesIO(archivo_content), engine='openpyxl')
                print(f"Datos de excel cargados. Columnas: {df.columns.tolist()}")
                print("Archivo Excel cargado correctamente.")

            elif 'bbdd_ucal2' in archivo_name:
                data2 = pd.read_csv(io.BytesIO(archivo_content), dtype=str)
                data2.columns = data2.columns.str.strip().str.replace(' ', '_')
                print(f"Datos de data2 cargados. Columnas: {data2.columns.tolist()}")

            elif 'bbdd_ucal3' in archivo_name:
                data3 = pd.read_csv(io.BytesIO(archivo_content), dtype=str)
                data3.columns = data3.columns.str.strip().str.replace(' ', '_')
                print(f"Datos de data3 cargados. Columnas: {data3.columns.tolist()}")

            elif archivo_content.startswith(b'<!DOCTYPE html>'):
                print("Error: Se intentó descargar una página en lugar de un CSV")

        except Exception as e:
            print(f"Error al procesar {archivo_name}: {e}")

    return df, data2, data3

# Cargar datos
df, data2, data3 = load_data()

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
data2['flg_convocatoria'] = data2['flg_convocatoria'].replace({0: 'No Convo', 1: 'Convo'})

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
     traslados_ids = filtered_df[filtered_df['flg_traslados'] == tipo_select, 'id_prometeo']
     print(f"Datos de data3 cargados. Columnas: {traslados_ids.columns.tolist()}")
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
     


# Agrupar por 'sc_fecha' y contar los 'id_prometeo' únicos
id_prometeo_fechas = filtered_df_2.groupby('sc_fecha')['id_prometeo'].nunique()

# Convertir a DataFrame para mejor visualización
Leads_gestion_diaria = id_prometeo_fechas.reset_index()
Leads_gestion_diaria.columns = ['sc_fecha', 'unique_id_count']



# Filtrar los datos para excluir al "TI" Integrador
filtered_data = filtered_df_2[filtered_df_2['nombre_asesor'] != 'TI']
# Agrupar por 'nombre_asesor' y contar los 'id_prometeo' únicos por fecha
Leads_gestionados = (
    filtered_data.groupby('sc_fecha')['id_prometeo']
    .nunique()
)
Leads_gestionados = Leads_gestionados.reset_index()
# Renombrar columnas para claridad
Leads_gestionados.columns = ['sc_fecha','unique_id_count']
# Mostrar el resultad


filtered_data= filtered_df_2[(filtered_df_2['desc_resultado_1'] != 'Sin contacto')  & 
    (filtered_df_2['nombre_asesor'] != 'TI')]

Leads_contactos = (
    filtered_data.groupby('sc_fecha')['id_prometeo']
    .nunique()
)
Leads_contactos = Leads_contactos.reset_index()
# Renombrar columnas para claridad
Leads_contactos.columns = ['sc_fecha','unique_id_count']
# Mostrar el resultado


##------------------------------------------------filtro fecha --------------------------------------------
min_fecha =  "2025-01-01"
max_fecha = filtered_df_2['sc_fecha'].max()

with col2:
    rango_fechas = st.date_input(
                "Selecciona el rango de fechas",
                value=(pd.to_datetime(min_fecha).date(), pd.to_datetime(max_fecha).date()),  # Convertir str a datetime.date
                help="Selecciona las fechas para filtrar los datos de conversión ."
            )

    
rango_fechas_str = (
            rango_fechas[0].strftime("%Y-%m-%d"),
            rango_fechas[1].strftime("%Y-%m-%d")
        )

filtered_df_2 = filtered_df_2[
            (filtered_df_2['sc_fecha'] >= rango_fechas_str[0]) &
            (filtered_df_2['sc_fecha'] <= rango_fechas_str[1])
        ]
## ----------------------------------------------------------------------------------------------------

# Filtrar los datos según las condiciones proporcionadas
filtered_data = filtered_df_2[
    (filtered_df_2['desc_resultado_1'].isin(["Evaluando", "Interesado"])) & 
    (filtered_df_2['desc_resultado_1'] != 'Sin contacto') & 
    (filtered_df_2['nombre_asesor'] != 'TI') 
]
# Agrupar por 'sc_fecha' y contar los valores únicos de 'id_prometeo'
Leads_valp = (
    filtered_data.groupby('sc_fecha')['id_prometeo']
    .nunique()
    .reset_index(name='unique_id_count')  # Convertir a DataFrame y nombrar la columna
)



# Verificar si el DataFrame tiene datos válidos
if Leads_valp.empty:
    st.error("No se encontraron datos válidos para las condiciones proporcionadas.")
else:
    # Asegurar que las fechas estén en formato datetime y ordenadas

     # Realizar el merge de los tres DataFrames por 'sc_fecha'
    chart_data = pd.merge(
                        Leads_gestionados[['sc_fecha', 'unique_id_count']], 
                          Leads_contactos[['sc_fecha', 'unique_id_count']], 
                          on='sc_fecha', 
                          suffixes=('_Leads_Asesor', '_CONTACTOS'))
    chart_data = chart_data.rename(columns={'unique_id_count_Leads_Asesor': 'Leads_Asesor', 
                                        'unique_id_count_CONTACTOS': 'CONTACTOS'})


    chart_data = pd.merge(chart_data, 
                          Leads_valp[['sc_fecha', 'unique_id_count']], 
                          on='sc_fecha',
                          suffixes=('', '_VALP'))
    
    chart_data = chart_data.rename(columns={'unique_id_count': 'VALP'})
    
 
    # Ordenar por fecha
    chart_data = chart_data.sort_values('sc_fecha')
    # Crear el gráfico de línea
    
    st.write("Crecimiento de Conversión por Fecha")
    st.line_chart(chart_data.set_index('sc_fecha'))
    
    chart_data = pd.merge(chart_data, 
                          Leads_gestion_diaria[['sc_fecha', 'unique_id_count']], 
                          on='sc_fecha',
                          suffixes=('', '_Leads_Tocados'))

    chart_data = chart_data.rename(columns={'unique_id_count': 'Leads_Tocados'})
    
    
    chart_data['Lead a Contacto'] = (chart_data['CONTACTOS'] / chart_data['Leads_Tocados']) * 100
    chart_data['Contacto a VALP'] = (chart_data['VALP'] / chart_data['CONTACTOS']) * 100
        # Formatear los valores al formato porcentaje (xx.xx%) en el DataFrame original
    #chart_data['Lead a Contacto'] = chart_data['Lead a Contacto'].map("{:.2f}%".format)
    #chart_data['Contacto a VALP'] = chart_data['Contacto a VALP'].map("{:.2f}%".format)
            # Ordenar las columnas en el orden solicitado
    chart_data = chart_data[['sc_fecha', 
                            'Leads_Tocados', 
                            'Leads_Asesor', 
                            'CONTACTOS', 
                            'VALP', 
                            'Lead a Contacto', 
                            'Contacto a VALP']]
    chart_data = chart_data.set_index("sc_fecha")
    
    # Transponer el DataFrame original antes de aplicar estilo
    transposed_chart_data = chart_data.T  # Transpone el DataFrame

    # Definir los colores en función del valor de porcentaje

def format_as_percentage(df, rows_to_format):
    """
    Formatea solo las filas especificadas como porcentaje con 2 decimales,
    dejando las demás filas sin modificaciones.
    """
    for row_name in df.index:
        if row_name in rows_to_format:
            # Solo formateamos las filas seleccionadas como porcentaje
            df.loc[row_name] = df.loc[row_name].apply(
                lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) and pd.notnull(x) else x
            )
        # Si no está en rows_to_format, no se hace nada con la fila
        # No se cambia ni la conversión ni el formato de los otros valores
    return df
    
agrupaciones = ["Día", "Semana", "Mes"]
agrupacion_seleccionada = st.selectbox("Agrupar por", options=agrupaciones)

if not Leads_valp.empty:
 
    # Convertir 'sc_fecha' a datetime para facilitar la agrupación (sin modificar permanentemente)
    temp_chart_data = chart_data.reset_index()
    temp_chart_data['sc_fecha_temp'] = pd.to_datetime(temp_chart_data['sc_fecha'], errors='coerce')
    # Formatear la fecha para que muestre solo "Año-Mes-Día"
    
    # Realizar la agrupación según la selección
    if agrupacion_seleccionada == "Día":
        temp_chart_data['Agrupacion'] = temp_chart_data['sc_fecha_temp'].dt.strftime('%Y-%m-%d')
    elif agrupacion_seleccionada == "Semana":
        temp_chart_data['Agrupacion'] = temp_chart_data['sc_fecha_temp'].dt.to_period('W').apply(lambda r: r.start_time.strftime('%Y-%m-%d'))
    elif agrupacion_seleccionada == "Mes":
        temp_chart_data['Agrupacion'] = temp_chart_data['sc_fecha_temp'].dt.to_period('M').astype(str)
    
    # Agrupar por la columna seleccionada
    agrupado = temp_chart_data.groupby('Agrupacion').sum(numeric_only=True)
    
    # Calcular las métricas de conversión si no es "Total"
    agrupado['Lead a Contacto'] = (agrupado['CONTACTOS'] / agrupado['Leads_Tocados']) * 100
    agrupado['Contacto a VALP'] = (agrupado['VALP'] / agrupado['CONTACTOS']) * 100
    
    agrupado['Lead a Contacto'] = agrupado['Lead a Contacto'].map("{:.2f}%".format)
    agrupado['Contacto a VALP'] = agrupado['Contacto a VALP'].map("{:.2f}%".format)

    agrupado2 = agrupado.transpose( )
    
    

        # Función para resaltar el color de las letras según las condiciones
    def highlight_values_transposed(row):
        styles = []
        for value in row:
            if isinstance(value, str) and '%' in value:  # Si el valor es un porcentaje
                num = float(value.strip('%'))
                if num > 10:
                    styles.append('color: green;')
                elif 5 <= num < 10:
                    styles.append('color: orange;')
                else:
                    styles.append('color: red;')
            else:
                styles.append('')  # Sin estilo
        return styles

    # Aplicar estilo al DataFrame transpuesto
    styled_agrupado_t = agrupado2.style.apply(highlight_values_transposed, axis=1)

    # Mostrar la tabla de métricas agrupadas
    st.write(f"Métricas de Conversión Agrupadas por {agrupacion_seleccionada}")

    # Convertir el DataFrame estilizado a HTML
    styled_html = styled_agrupado_t.to_html()

    # Mostrar el DataFrame estilizado en Streamlit
    st.markdown(
    f"""
    <div style="overflow-x:auto; width: 900px; border: 1px solid #ddd; padding: 2px;">
        {styled_html}
    """,
    unsafe_allow_html=True
    )


else:
    st.error("No se encontraron datos válidos para las condiciones proporcionadas.")



mundo_counts = df['MUNDO_CALCULADO'].value_counts().reset_index()
mundo_counts.columns = ['MUNDO', 'COUNT']


# Crear gráfico de pastel
#fig = px.pie(
 #   mundo_counts, 
  #  values='COUNT', 
   # names='MUNDO', 
    #title='Distribución de Mundos',
    #color_discrete_sequence=px.colors.qualitative.Set3
#)

# Ajustar tamaño del gráfico
#fig.update_layout(width=400, height=400)

# Mostrar gráfico en Streamlit
#st.plotly_chart(fig)



 #(df['fecha_registro_periodo'] >= pd.to_datetime(start_date)) &
 #(df['fecha_registro_periodo'] <= pd.to_datetime(end_date))
# Resumen de métricas
st.write("")
st.write("")
st.markdown(
    '<h3 style="color:#7E57C2;">Resumen de métricas Total</h3>',
    unsafe_allow_html=True
)
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
    leads_pagantes = filtered_df[filtered_df['agrupacion_tipificacion_actual'] == "VALORES_PAGANTE"]['id_prometeo'].nunique()
    st.metric(" Pagantes", format_with_commas(leads_pagantes))


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
st.write("Tabla - STATUS DE BASES")
col1,col2=st.columns(2)
with col1:
    interactive_table(tabla_metricas)
    
with col2:
    st.write("")


# Crear DataFrame
filtered_df3 = filtered_df

# Definir los valores mínimos y máximos de las columnas
min_dsnc = filtered_df3['dias_sin_contacto'].min()
max_dsnc = filtered_df3['dias_sin_contacto'].max()

# Lista de límites superiores para los rangos de cada columna

bins_dsnc = [min_dsnc, 8, 16, 31, 61, max_dsnc]  # Definido manualmente

# Generar etiquetas basadas en los límites de los rangos

labels_dsnc = [f"{bins_dsnc[i]}-{bins_dsnc[i+1]-1}" 
                    for i in range(len(bins_dsnc) - 1)]

# Filtrar los datos donde 'ult_tipf_dif_sin_contacto' es igual a "Perdido"
filtered_df3_perdido = filtered_df3[filtered_df3['ult_tipf_dif_sin_contacto'] == "Perdido"]

# Obtener los valores únicos de 'ult_tipf_dif_sin_contacto_2' solo para los casos "Perdido"
valores_unicos_perdido = filtered_df3_perdido['ult_tipf_dif_sin_contacto_2'].unique()
filtered_df3_perdido = filtered_df3_perdido.copy()
filtered_df3_perdido.loc[:, 'dsnc'] = pd.cut(filtered_df3_perdido.loc[:, 'dias_sin_contacto'], bins=bins_dsnc, labels=labels_dsnc, right=False)

# Crear la tabla dinámica con pivot_table

# Crear la tabla dinámica con pivot_table
tabla = pd.pivot_table(filtered_df3_perdido, index='ult_tipf_dif_sin_contacto_2', columns='dsnc', aggfunc='size', fill_value=0, observed=False)

tabla['Total'] = tabla.sum(axis=1)
# Mostrar la tabla en Streamlit
st.write("Matriz de Perdidos / Días sin contacto")
#st.dataframe(tabla)

col1,col2=st.columns(2)
with col1:
    interactive_table(tabla)
with col2:
    st.write("")




col1,col2=st.columns(2)
with col1:

    # Aplicar prefiltro: Excluir "Sin contacto" en la columna "prim_tipif_no_TI"
    filtered_df_mad = filtered_df[filtered_df["prim_tipif_no_TI"] != "Sin contacto"].copy()

    # Eliminar filas sin fecha de primer toque o fecha de pago
    filtered_df_mad = filtered_df_mad.dropna(subset=["prim_tipif_no_TI2", "fecha_pagante_crm"])

    # Convertir columnas de fecha a tipo datetime
    filtered_df_mad["prim_tipif_no_TI2"] = pd.to_datetime(filtered_df_mad["prim_tipif_no_TI2"])
    filtered_df_mad["fecha_pagante_crm"] = pd.to_datetime(filtered_df_mad["fecha_pagante_crm"])

    # Calcular maduración (días entre primer toque y pago)
    filtered_df_mad["maduracion_dias"] = (filtered_df_mad["fecha_pagante_crm"] - filtered_df_mad["prim_tipif_no_TI2"]).dt.days

    # Eliminar valores atípicos usando el rango intercuartil (IQR)
    Q1 = filtered_df_mad["maduracion_dias"].quantile(0.25)
    Q3 = filtered_df_mad["maduracion_dias"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    # Filtrar datos sin outliers
    filtered_df_mad = filtered_df_mad[(filtered_df_mad["maduracion_dias"] >= limite_inferior) & 
                                    (filtered_df_mad["maduracion_dias"] <= limite_superior)]

    # Crear Boxplot con Plotly
    fig = px.box(filtered_df_mad, y="maduracion_dias", title="Boxplot de Maduración (Días desde 1 Toque a Pago)",
                labels={"maduracion_dias": "Días de Maduración"},
                template="plotly_white", width=400, height=450)

    # Mostrar en Streamlit
    st.plotly_chart(fig)




with col2:

    # Aplicar prefiltro: Excluir "Sin contacto" en la columna "prim_tipif_no_TI"
    filtered_df_mad = filtered_df[filtered_df["prim_tipif_no_TI"] != "Sin contacto"].copy()

    # Convertir a numérico para evitar errores
    filtered_df_mad["cantidad_tipificaciones"] = pd.to_numeric(filtered_df_mad["cantidad_tipificaciones"], errors="coerce")
    # Eliminar valores nulos después de conversión
    filtered_df_mad = filtered_df_mad.dropna(subset=["cantidad_tipificaciones"])
    # Calcular IQR para eliminar valores atípicos
    Q1 = filtered_df_mad["cantidad_tipificaciones"].quantile(0.25)
    Q3 = filtered_df_mad["cantidad_tipificaciones"].quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR

    filtered_df_mad = filtered_df_mad[(filtered_df_mad["cantidad_tipificaciones"] >= limite_inferior) & 
                                    (filtered_df_mad["cantidad_tipificaciones"] <= limite_superior)]
    fig = px.box(filtered_df_mad, y="cantidad_tipificaciones", title="Boxplot de Número de Toques",
                labels={"cantidad_tipificaciones": "Cantidad de Toques"},
                template="plotly_white", width=400, height=450)
    # Mostrar en Streamlit
    st.plotly_chart(fig)


# Crear DataFrame
st.write("Matriz de Toques / Días de Vida")

# Dividir el espacio en columnas
col1, col2 = st.columns([5, 2])  # Ajusta los tamaños relativos de las columnas

filtered_df2 = pd.DataFrame(filtered_df)

with col2:
    # Selector de filtro
    st.write("")
    st.write("")
    st.write("")
    opcion_filtro = st.radio(
        "Filtrar datos por:",
        options=["Con todos los datos", "Sin Blacklist/Perdidos"]
    )

    if opcion_filtro == "Sin Blacklist/Perdidos":
        filtered_df2 = filtered_df2[
            ~filtered_df2['agrupacion_tipificacion_actual'].isin(['VALORES_BLACK_LIST', 'VALORES_PERDIDO'])
        ]

        # Espacio entre elementos
    st.write("")
    st.write("")

    # Control deslizante para seleccionar el límite de cantidad de tipificaciones
    limite_tipificaciones = st.slider(
        "Cantidad de tipificaciones",
        min_value=1,
        max_value=int(filtered_df2['cantidad_tipificaciones'].max()),  # Usar el valor máximo dinámico
        value=40  # Valor inicial por defecto
    )

    # Aplicar el filtro dinámico al DataFrame
    filtered_df2 = filtered_df2[filtered_df2['cantidad_tipificaciones'] <= limite_tipificaciones]

with col1:
    # Definir los valores mínimos y máximos de las columnas
    min_cantidad_tipificaciones = filtered_df2['cantidad_tipificaciones'].min()
    max_cantidad_tipificaciones = filtered_df2['cantidad_tipificaciones'].max()
    min_dias_vida = filtered_df2['DIAS_VIDA'].min()
    max_dias_vida = filtered_df2['DIAS_VIDA'].max()

    # Lista de límites superiores para los rangos de cada columna
    bins_dias_vida = [min_dias_vida, 8, 16, 31, 61, max_dias_vida]  # Definido manualmente

    # Generar etiquetas basadas en los límites de los rangos
    labels_dias_vida = [
        f"{bins_dias_vida[i]}-{bins_dias_vida[i+1]-1}" for i in range(len(bins_dias_vida) - 1)
    ]

    # Crear columna categórica utilizando pd.cut
    filtered_df2.loc[:, 'rango_dias_vida'] = pd.cut(
    filtered_df2['DIAS_VIDA'], bins=bins_dias_vida, labels=labels_dias_vida, right=False
)

    # Crear la tabla dinámica con pivot_table
    tabla = pd.pivot_table(
        filtered_df2,
        index='cantidad_tipificaciones',
        columns='rango_dias_vida',
        aggfunc='size',
        fill_value=0,observed=False
    )

    # Agregar una columna de totales
    tabla['Total'] = tabla.sum(axis=1)

    # Mostrar la tabla en Streamlit
    #st.dataframe(tabla)
    interactive_table(tabla)


# "turno"  == mañana tarde 
#flg_traslados = 0 normla 1 traslados

columnas_seleccionadas = ['id_prometeo', 'ult_programa_interes','MUNDO_CALCULADO', 'modalidad_programa','turno','flg_traslados','canal_atribucion', 'subcanal','fecha_registro_periodo']
filtered_dff = filtered_df[columnas_seleccionadas]
st.write("")
st.dataframe(filtered_dff,hide_index=True)