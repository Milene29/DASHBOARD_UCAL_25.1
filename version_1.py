
import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import funciones_generales as fg
import warnings

st.set_page_config(page_title="Streamlit Dashboard", layout="wide")


hoy = fg.fecha_peru_hoy()
today_string = hoy.strftime('%y%m%d')

@st.cache_data
def load_data():
    folder_id = '17E4c2ShTX0jbH3_4REOv5oCTY2_ypSxZ'
    file_id='1wLewUXO5ISe2qCDJnTXUf4WdGCA1z8DgP-GO55cUJVI'
    file_id_251='1uML9hmrdOZVQ3Fa1GLDo7XkoWRbZSPgAcKYV1aFd6xs'
    file_id_261='1gVSQQQ1obeIgh6fgsjBD3L2YIG3eU5bizauYnYpzy1Y'
    #archivos_descargados = fg.obtener_archivos_drive(folder_id)
    data_pago_252=pd.read_excel("DATA_VENTA_25.2.xlsx")
    data_pago_251=pd.read_excel("DATA_VENTA_25.1.xlsx")
    data_pago_261=pd.read_excel("DATA_VENTA26.1.xlsx")
    df,df_261, data2,data_espejo = None, None,None,None
  
    df = pd.read_excel("2025-06-12_bbdd_ucal_['2025-2']_conv_(0,1)_pagantes_(0,1)_fecha_250612.xlsx", engine='openpyxl')
    df_261 = pd.read_excel("2025-06-12_bbdd_ucal_['2026-1']_conv_(0,1)_pagantes_(0,1)_fecha_250612.xlsx", engine='openpyxl')
    try:
        data2 = pd.read_csv("250612bbdd_ucal2026-1','2025-2.csv", sep=',', dtype=str)
        data2.columns = data2.columns.str.strip().str.replace(' ', '_')
    except Exception as e:
        st.error(f"Error cargando data2: {e}")
    data_espejo = pd.read_csv("250612bbdd_ucal2025-1', '2024-2.csv", sep=',', dtype=str)
    data_espejo.columns = data_espejo.columns.str.strip().str.replace(' ', '_')

    return df,df_261, data2,data_espejo,data_pago_252,data_pago_251,data_pago_261
# Cargar datos

# Botón para reiniciar la aplicación y limpiar el caché
if st.button('Reiniciar'):
    st.cache_data.clear()  # Limpiar caché de datos
    st.rerun()  
df252, df_261,data2 ,data_espejo,data_pago_252,data_pago_251,data_pago_261= load_data()

print("................................p´´´++++++++++++++++++++++")

# Verificar si los datos se cargaron correctamente
if (df_261 is None):
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
            Dashboard UCAL
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
    col1, col2,col3 = st.columns(3)
    with col3:
        st.write("")
    with col1:
        campana_seleccionada = st.selectbox("Campaña: ", ["24.2","25.1","25.2", "26.1"])
            # Selección del dataframe base
        data2 = data2 if campana_seleccionada in ["25.2", "26.1"] else data_espejo
        print(data2.columns)
        # Filtro adicional por "sc_campana" si aplica
        if campana_seleccionada == "25.2": 
            data2 = data2[data2["sc_campana"] == "2025-2"]
            data_pago=data_pago_252
            df=df252
            
        elif campana_seleccionada == "26.1":
            data2 = data2[data2["sc_campana"] == "2026-1"]
            data_pago=data_pago_261
            df = df_261
        elif campana_seleccionada == "25.1":
            data_espejo = data_espejo[data_espejo["sc_campana"] == "2025-1"]
            data_pago=data_pago_251
            df=df252
            

        elif campana_seleccionada == "24.2":
            data_espejo = data_espejo[data_espejo["sc_campana"] == "2024-2"]
            data_pago=data_pago_251 
            df=df252  

        data_pago['Asesor Homologado']=data_pago['ASESOR HOMOLOGADO'] if campana_seleccionada in ["25.2", "26.1"] else data_pago['Asesor Homologado']
        data_pago['Fecha de Pago']=data_pago['FECHA DE PAGO COMPLETO'] if campana_seleccionada in ["25.2", "26.1"] else data_pago['Fecha de Pago']
        data_pago['CARRERA']=data_pago['CARRERA'] if campana_seleccionada in ["25.2", "26.1"] else data_pago['Carrera']
        data_pago['HORARIO DE ESTUDIO']=data_pago['HORARIO DE ESTUDIO'] if campana_seleccionada in ["25.2", "26.1"] else data_pago['Horario de Estudio']


# Helper function to format numbers with commas
def format_with_commas(number):
    return f"{number:,}"

# Define logic to classify careers into worlds
def clasificar_mundo(PROGRAMA):
    if PROGRAMA in [
        "COMUNICACIÓN", "COMUNICACIÓN AUDIOVISUAL Y CINE", "COMUNICACIÓN Y PUBLICIDAD TRANSMEDIA"
    ]:
        return "MUNDO COMUNICACIONES"
    elif PROGRAMA in ["ARQUITECTURA", "ARQUITECTURA DE INTERIORES"]:
        return "MUNDO ARQUITECTURA"
    elif PROGRAMA == "DISEÑO GRÁFICO PUBLICITARIO":
        return "MUNDO DISEÑO"
    elif PROGRAMA in [
        "ADMINISTRACIÓN", "ADMINISTRACIÓN Y MARKETING", "MARKETING E INNOVACIÓN",
        "ADMINISTRACIÓN Y NEGOCIOS INTERNACIONALES"
    ]:
        return "MUNDO NEGOCIOS"
    elif PROGRAMA == "PSICOLOGÍA":
        return "MUNDO PSICOLOGIA"
    elif PROGRAMA in ["DISEÑO ESTRATÉGICO", "INGENIERIA INDUSTRIAL"]:
        return "PORTAFOLIO ANTIGUO"
    elif PROGRAMA == "SIN CARRERA":
        return "SIN CARRERA"
    

carr_mapping = {
    "Comunicación Audiovisual y Cine": "COMUNICACIÓN AUDIOVISUAL Y CINE",
    "Arquitectura": "ARQUITECTURA",
    "Arquitectura de Interiores": "ARQUITECTURA DE INTERIORES",
    "Administración y Negocios Internacionales": "ADMINISTRACIÓN Y NEGOCIOS INTERNACIONALES",
    "Psicología": "PSICOLOGÍA",
    "Diseño Gráfico Publicitario": "DISEÑO GRÁFICO PUBLICITARIO",
    "Comunicación y Publicidad Transmedia": "COMUNICACIÓN Y PUBLICIDAD TRANSMEDIA",
    "Administración y Marketing": "ADMINISTRACIÓN Y MARKETING",
    "Administración": "ADMINISTRACIÓN",
    "Comunicación": "COMUNICACIÓN",
    "Marketing e Innovación": "MARKETING E INNOVACIÓN"
}



data_pago['Carrera'] = data_pago['CARRERA'].replace(carr_mapping)
df['PROGRAMA'] = df['PROGRAMA'].fillna('SIN CARRERA')
df['flg_convocatoria'] = df['FLAG CONVO']
df['agrupacion_tipificacion_actual'] = df['STATUS DE GESTION']
df['ult_tipf_dif_sin_contacto'] = df['RESPUESTA ULT TIP']
df['ult_tipf_dif_sin_contacto_2']=df['RESPUESTA 2 ULT TIP']
df['cantidad_tipificaciones']=df['# DE TOQUES']
df['DIAS_VIDA']=df['DIAS DE VIDA']
df['turno']=df['TURNO']
df['fecha_registro_periodo']=df['FECHA HORA DE REGISTRO']

data2['ult_programa_interes'] = data2['ult_programa_interes'].fillna('SIN CARRERA')

data_pago['Carrera'] = data_pago['Carrera'].fillna('SIN CARRERA')
df['id_prometeo'] = df['ID PROMETEO']
df['MUNDO_CALCULADO'] = df['PROGRAMA'].apply(clasificar_mundo)
data2['MUNDO_CALCULADO'] = data2['ult_programa_interes'].apply(clasificar_mundo)
data_pago['MUNDO_CALCULADO'] = data_pago['Carrera'].apply(clasificar_mundo)
df_traslados = df[['id_prometeo', 'ES TRASLADO']]
df['ES TRASLADO'] = df['ES TRASLADO'].replace({0: 'NUEVO', 1: 'TRASLADO'})
df['flg_convocatoria'] = df['flg_convocatoria'].replace({0: 'No Convo', 1: 'Convo'})

data2['flg_convocatoria'] = data2['flg_convocatoria'].replace({"0": 'No Convo', "1": 'Convo'})

data_pago['Horario de Estudio'] = data_pago['HORARIO DE ESTUDIO'].replace({'Nocturno - A distancia': 'RE', 'Diurno': 'PR','Nocturno - Psicologia':'RE'})


print("creando flg_traslado")

if 'traslados_set' not in globals():
    traslados_set = set(map(str, df.loc[df['ES TRASLADO'] == "TRASLADO", 'id_prometeo']))  
    print("traslados_set creado")

    data2['ES TRASLADO'] = data2['id_prometeo'].apply(lambda x: "TRASLADO" if x in traslados_set else "NUEVO")

print("termino flg_traslado") 

data2['PROGRAMA']=data2['ult_programa_interes']
with st.sidebar:
    st.header("Filtros")
    
    # Filtro de mundos
    mundos_disponibles = ["TODAS LAS CARRERAS"] + df['MUNDO_CALCULADO'].dropna().unique().tolist()
    mundo_seleccionado = st.selectbox("Selecciona un mundo", options=mundos_disponibles)

    # Filtro de carreras dinámico según el mundo seleccionado
    if mundo_seleccionado == "TODAS LAS CARRERAS":
        carreras_disponibles = df['PROGRAMA'].dropna().unique()
        carreras_disponibles = [carrera for carrera in carreras_disponibles if carrera != "SIN CARRERA"]

        carreras_disponibles2 = data2['PROGRAMA'].dropna().unique()
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["Todas"] + list(carreras_disponibles))

    elif mundo_seleccionado != "SIN CARRERA":
        carreras_disponibles = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]['PROGRAMA'].dropna().unique()
        carreras_disponibles2 = data2[data2['MUNDO_CALCULADO'] == mundo_seleccionado]['PROGRAMA'].dropna().unique()
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["Todas"] + list(carreras_disponibles))
    else:
        
        carrera_seleccionada = st.selectbox("Selecciona una carrera",options=["SIN CARRERA"] )

filtered_df = df.copy()
filtered_df_2 = data2.copy()
print(filtered_df_2.head())
# Filtrar por mundo
if mundo_seleccionado != "TODAS LAS CARRERAS":
    filtered_df = df[df['MUNDO_CALCULADO'] == mundo_seleccionado]
    filtered_df_2=data2[data2['MUNDO_CALCULADO'] == mundo_seleccionado]
    data_pago=data_pago[data_pago['MUNDO_CALCULADO']==mundo_seleccionado]
# Filtrar por mundo
if carrera_seleccionada != "Todas":
    filtered_df = df[(df['MUNDO_CALCULADO'] == mundo_seleccionado) & (df['PROGRAMA'] == carrera_seleccionada) ]
    filtered_df_2 = data2[(data2['MUNDO_CALCULADO'] == mundo_seleccionado) & (data2['PROGRAMA'] == carrera_seleccionada) ]
    data_pago = data_pago[(data_pago['MUNDO_CALCULADO'] == mundo_seleccionado) & (data_pago['Carrera'] == carrera_seleccionada) ]

if mundo_seleccionado == "SIN CARRERA":
    filtered_df = df[(df['MUNDO_CALCULADO'] == mundo_seleccionado)& (df['PROGRAMA'] == "SIN CARRERA")]
    filtered_df2 = data2[(data2['MUNDO_CALCULADO'] == mundo_seleccionado)& (data2['PROGRAMA'] == "SIN CARRERA")]

# Mostrar resultados filtrados
with st.sidebar:
    try:
            # Asegurarse de que la columna sea numérica
            filtered_df['dias_sin_contacto'] = pd.to_numeric(filtered_df['DIAS SIN CONTACTO'], errors='coerce')

            # Calcular el mínimo y el máximo
            min_dias = int(filtered_df['dias_sin_contacto'].min())
            max_dias = int(filtered_df['dias_sin_contacto'].max())

            rango_dias = st.slider("Selecciona el rango de días sin contacto", min_dias, max_dias, (min_dias, max_dias))
            # Filtrar los datos según el rango seleccionado
            filtered_df = filtered_df.query("@rango_dias[0] <= dias_sin_contacto <= @rango_dias[1]")
    except ValueError as e:
                st.error(f"Error al procesar la columna 'dias_sin_contacto': {e}")  
    filtered_df['flg_traslados']=filtered_df['ES TRASLADO']
    tipo_ingreso =["Todos"] + filtered_df['flg_traslados'].unique().tolist()
    tipo_select= st.selectbox("Tipo Ingreso", options=tipo_ingreso)
    if tipo_select != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['flg_traslados'] == tipo_select]
     filtered_df_2 = filtered_df_2[filtered_df_2['flg_traslados'] == tipo_select]
     # Filtrar los IDs con flg_traslados = 1

     data_pago=data_pago[data_pago['Tipo de Ingreso']== tipo_select]

 
    filtered_df['modalidad_programa']=filtered_df['MODALIDAD']
    modalidad =["Todos"] + filtered_df['modalidad_programa'].unique().tolist()
    moda_selec= st.selectbox("Modalidad", options=modalidad)
    if moda_selec != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['modalidad_programa'] == moda_selec]
     filtered_df_2 = filtered_df_2[filtered_df_2['modalidad_programa'] == moda_selec]
     data_pago=data_pago[data_pago['Horario de Estudio']== moda_selec]
     
    filtered_df['canal_atribucion']=filtered_df['CANAL']
    filtered_df['subcanal']=filtered_df['SUBCANAL']
    canales_disponibles =filtered_df['canal_atribucion'].unique().tolist()
    canales_seleccionados = st.multiselect("Canal", options=canales_disponibles,placeholder="Selecciona uno o varios canales...")
    # Filtrar los datos según la selección
    if canales_seleccionados:
        filtered_df = filtered_df[filtered_df['canal_atribucion'].isin(canales_seleccionados)]
        filtered_df_2 = filtered_df_2[filtered_df_2['canal_atribucion'].isin(canales_seleccionados)]
        data_pago=data_pago[data_pago['CANAL'].isin(canales_seleccionados)]
     
     
    subcanales_disponibles =["Todos"] + filtered_df['subcanal'].unique().tolist()
    subcanal_seleccionado= st.selectbox("Subcanal", options=subcanales_disponibles)
    if subcanal_seleccionado != "Todos":
        # Filtrar por el canal seleccionado
     filtered_df = filtered_df[filtered_df['subcanal'] == subcanal_seleccionado]     
     

    Convo =["Todos"] + filtered_df['FLAG CONVO'].unique().tolist()
    Convo_seleccionado= st.selectbox("Convo", options=Convo)
    if Convo_seleccionado != "Todos":
     filtered_df = filtered_df[filtered_df['FLAG CONVO'] == Convo_seleccionado]
     filtered_df_2 = filtered_df_2[filtered_df_2['FLAG CONVO'] == Convo_seleccionado]

nombre_mapping_1 = {
    "ROSA NATALIA UGARTE CHAVEZ": "Rosa Ugarte",
    "FIORELLA LANEGRA": "Fiorella Lanegra",
    "SERGIO VALDERRAMA RODRIGUEZ": "Sergio Valderrama",
    "ANGELICA IPARRAGUIRRE": "Angelica Iparraguirre",
    "JUAN MANUEL RODRIGUEZ CHIPANA": "Juan Chipana",
    "CINTHIA OROSCO": "Cinthia Orosco",
    "ERWIN TERIE VITAL AVILA": "Erwin Vital",
    "DANIEL ENRIQUE ZAPATA ALVARADO": "Daniel Zapata",
    "JUAN MANUEL RODRIGUEZ CHIPANA": "Juan Manuel",
    "ANDREA ARAUJO ANTARA": "Andrea Araujo",
    "INGRID GUILLERMO RIVERA": "Ingrid Guillermo",
    "ANDREA ALEJANDRA CRISANTO NAVARRO": "Andrea Crisanto",
    "STEFANO NAPURI": "Stefano Napuri",
    "JANIRA DELGADO SALAZAR": "Janira Delgado",
    "ROSMERY ENRIQUEZ": "Rosmery Enriquez",
    "JOSE RAUL MENDEZ NONAJULCA": "Jose Mendez",
    "JUAN GOMEZ": "Juan Gomez",
    "CÉSAR ALBERTO LOAYZA GUTIÉRREZ": "César Loayza",
    "LOHANA RIVERA": "Lohana Rivera",
    "MERI LUZ RICALDE GONZALES":"Meri Ricalde",
    "FABIOLA ORTEGA" : "Fabiola Galindo",
    "ALEJANDRA NAVARRO":"Andrea Crisanto",
    "JHONATAN ADIEL LOPEZ RODRIGUEZ":"Jhonatan Lopez"
}
nombre_mapping_2 = {
    "Andrea Araujo Antara": "Andrea Araujo",
    "Andrea Crisanto" :"Andrea Crisanto",
    "Ingrid Guillermo Rivera": "Ingrid Guillermo",
    "Juan Pablo Gómez": "Juan Gomez",
    "Cinthia Mariella Orosco": "Cinthia Orosco",
    "Sergio Valderrama Rodriguez": "Sergio Valderrama",
    "Juan Manuel Rodríguez": "Juan Manuel",
    
}
data_pago['Asesor Homologado'] = data_pago['Asesor Homologado'].replace(nombre_mapping_2)
filtered_df_2['nombre_asesor'] = filtered_df_2['nombre_asesor'].replace(nombre_mapping_1)

try:
    min_fecha =  filtered_df_2['sc_fecha'].min()
    max_fecha = filtered_df_2['sc_fecha'].max()
    print(max_fecha)
    print(min_fecha)
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
except Exception as e:
    st.error(f"Ocurrió u    n error al procesar las fechas: {e}")
# Agrupar por 'sc_fecha' y contar los 'ID PROMETEO' únicos

asesores_unicos = filtered_df_2[~filtered_df_2['nombre_asesor'].isin(['TI INTEGRADOR','ANGIE AVALOS','ANA JURADO','Rosmery Enriquez','ANGIE JANETH ARIAS FERNANDEZ','Stefano Napuri','Jose Mendez','César Loayza','OMAR GONZALES','Lohana Rivera','YADIRA ALANIA','Juan Gomez','DENISE YANAY'])]['nombre_asesor'].unique()
asesores_unicos = asesores_unicos[~pd.isna(asesores_unicos)]  # Asegúrate de filtrar NaN aquí

col1,col2=st.columns([1,3])
with col1:
    agrupaciones = ["Día", "Semana", "Mes"]
    agrupacion_seleccionada = st.selectbox("Agrupar por", options=agrupaciones)
with col2:
    st.write("")

            
st.markdown(f'<h4 style="color:#01579b;font-weight:bold;">Métricas de Gestión - {agrupacion_seleccionada}</h4>', unsafe_allow_html=True)


col1,col2=st.columns([1,3])
with col1:
    asesores_seleccionados = st.multiselect("Selecciona uno o más Asesores", options=asesores_unicos)
with col2:
    st.write("")


id_prometeo_fechas = filtered_df_2.groupby('sc_fecha')['id_prometeo'].nunique()
# Convertir a DataFrame para mejor visualización
Leads_gestion_diaria = id_prometeo_fechas.reset_index()
Leads_gestion_diaria.columns = ['sc_fecha', 'unique_id_count']

# Filtrar los datos para excluir al "TI" Integrador
filtered_data = filtered_df_2[filtered_df_2['nombre_asesor'] != 'TI INTEGRADOR']
if asesores_seleccionados:
    filtered_data = filtered_df_2[filtered_df_2['nombre_asesor'].isin(asesores_seleccionados)]
    data_pago= data_pago[data_pago['Asesor Homologado'].isin(asesores_seleccionados)]

# Agrupar por 'nombre_asesor' y contar los 'id_prometeo' únicos por fecha
Leads_gestionados = (
    filtered_data.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo'].count()
).reset_index()
# Renombrar columnas para claridad
Leads_gestionados.columns = ['sc_fecha','nombre_asesor','unique_id_count']

Leads_gestionados_unicos = (
    filtered_data.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo'].nunique()
).reset_index()

# Renombrar columnas para claridad
Leads_gestionados_unicos.columns = ['sc_fecha', 'nombre_asesor', 'unique_id_count']


filtered_data_perdidos = filtered_df_2[filtered_df_2['desc_resultado_1'] == 'Perdido']

Leads_perdidos_unicos = (
    filtered_data_perdidos.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo'].nunique()
).reset_index()
# Renombrar columnas para claridad
Leads_perdidos_unicos.columns = ['sc_fecha', 'nombre_asesor', 'unique_id_count']


filtered_data2= filtered_data[(filtered_data['desc_resultado_1'] != 'Sin contacto')  & (filtered_data['nombre_asesor'] != 'TI INTEGRADOR')  ]

Leads_contactos = (
    filtered_data2.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo']
    .count()
)
Leads_contactos = Leads_contactos.reset_index()
# Renombrar columnas para claridad
Leads_contactos.columns = ['sc_fecha', 'nombre_asesor', 'unique_id_count']

Leads_contactos_unicos = (
    filtered_data2.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo']
    .nunique()
    .reset_index()
)
Leads_contactos_unicos.columns = ['sc_fecha', 'nombre_asesor', 'unique_id_count']

filtered_data20= filtered_data[(filtered_data['desc_resultado_1'].isin(["Se inscribio","Registrado a evento","Volver a llamar","Evaluando" ,'Interesado','Se inscribio','Promesa de pago',"Pagante"])) & 
    (filtered_data['desc_resultado_1'] != 'Sin contacto')  & (filtered_data['nombre_asesor'] != 'TI INTEGRADOR')  ]

Leads_contactos_efectivos = (
    filtered_data20.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo']
    .count()
)
Leads_contactos_efectivos = Leads_contactos_efectivos.reset_index()
# Renombrar columnas para claridad
Leads_contactos_efectivos.columns = ['sc_fecha', 'nombre_asesor', 'unique_id_count']





filtered_data3 = filtered_data[
    (filtered_data['desc_resultado_1'].isin(["Evaluando" ,'Interesado','Se inscribio','Promesa de pago',"Registrado a evento","Pagante"])) & 
    (filtered_data['desc_resultado_1'] != 'Sin contacto') 
]
filtered_data_vll = filtered_data[
    (filtered_data['desc_resultado_1'].isin(["Evaluando" ,'Interesado','Se inscribio','Promesa de pago','Volver a llamar',"Registrado a evento","Pagante"])) & 
    (filtered_data['desc_resultado_1'] != 'Sin contacto') 
]
# Agrupar por 'sc_fecha' y contar los valores únicos de 'id_prometeo'
Leads_valp = (
    filtered_data3.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo']
    .nunique()
    .reset_index(name='unique_id_count')  # Convertir a DataFrame y nombrar la columna
)
print(Leads_valp)
Leads_valp_vll = (
    filtered_data_vll.groupby(['sc_fecha', 'nombre_asesor'])['id_prometeo']
    .nunique()
    .reset_index(name='unique_id_count')  # Convertir a DataFrame y nombrar la columna
)

data_pago['Fecha de Pago de Boleta'] = pd.to_datetime(data_pago['Fecha de Pago'], format="%d/%m/%Y", errors='coerce')

data_pago['sc_fecha'] = data_pago['Fecha de Pago de Boleta'].dt.date

Leads_pagos = (
    data_pago.groupby(['sc_fecha', 'Asesor Homologado'])['ID PROMETEO']
    .nunique()
    .reset_index(name='unique_id_count')  # Convertir a DataFrame y nombrar la columna
)

# Convertir a DataFrame con formato datetime.date
try:
    fecha_completa = pd.date_range(start=rango_fechas[0], end=rango_fechas[1])
    fecha_completa_df = pd.DataFrame({'sc_fecha': fecha_completa.date})

    # Unir el DataFrame de pagos con el de todas las fechas
    Leads_pagos = fecha_completa_df.merge(Leads_pagos, on='sc_fecha', how='left')
    # Rellenar valores NaN con 0 (fechas sin pagos)
    Leads_pagos['unique_id_count'] = Leads_pagos['unique_id_count'].fillna(0).astype(int)
    Leads_pagos.columns = ['sc_fecha','nombre_asesor','unique_id_count']
    # Verificar si el DataFrame tiene datos válidos
    if Leads_gestion_diaria.empty:
        st.error("No se encontraron datos válidos para las condiciones proporcionadas.")
    else:
        chart_data_dict = {
        'Métrica': [ 'Gestiones','%Contacto Corriente', 'Contacto', 'Gestion Unicos','%Contacto','Contacto Unicos','%Valp','Valp Unicos (+VLL)','Valp Unicos','Perdidos Unicos','%Perdidos','Pagos','%Pago (Paso)','%Pago (Acum)']
    }
        chart_data_dict2 = {
        'Métrica': ['%Contacto Corriente','%Contacto','%Valp','%Perdidos','%Pago (Paso)','%Pago (Acum)']
    }
        # Rellenar con datos desde los DataFrames originales

        Leads_gestion_diaria['sc_fecha'] = pd.to_datetime(Leads_gestion_diaria['sc_fecha'])
        Leads_pagos['sc_fecha'] = pd.to_datetime(Leads_pagos['sc_fecha'])
        Leads_gestionados['sc_fecha'] = pd.to_datetime(Leads_gestionados['sc_fecha'])
        Leads_gestionados_unicos['sc_fecha'] = pd.to_datetime(Leads_gestionados_unicos['sc_fecha'])
        Leads_contactos['sc_fecha'] = pd.to_datetime(Leads_contactos['sc_fecha'])
        Leads_contactos_unicos['sc_fecha'] = pd.to_datetime(Leads_contactos_unicos['sc_fecha'])
        Leads_valp['sc_fecha'] = pd.to_datetime(Leads_valp['sc_fecha'])
        Leads_valp_vll['sc_fecha'] = pd.to_datetime(Leads_valp_vll['sc_fecha'])
        Leads_perdidos_unicos['sc_fecha'] = pd.to_datetime(Leads_perdidos_unicos['sc_fecha'])
        Leads_contactos_efectivos['sc_fecha'] = pd.to_datetime(Leads_contactos['sc_fecha'])
        for fecha in Leads_gestion_diaria['sc_fecha']:
            # Obtener los valores correspondientes a cada métrica por fecha
            pagos = Leads_pagos.loc[Leads_pagos['sc_fecha'] == fecha, 'unique_id_count'].sum()
            leads_tocados = Leads_gestion_diaria.loc[Leads_gestion_diaria['sc_fecha'] == fecha, 'unique_id_count'].sum() 
            leads_asesor = Leads_gestionados.loc[Leads_gestionados['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos
            leads_asesor_unicos = Leads_gestionados_unicos.loc[Leads_gestionados_unicos['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos
            contactos = Leads_contactos.loc[Leads_contactos['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos
            contactos_unicos = Leads_contactos_unicos.loc[Leads_contactos_unicos['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos
            valp = Leads_valp.loc[Leads_valp['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos
            valp_vll = Leads_valp_vll.loc[Leads_valp_vll['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos
            perdidos = Leads_perdidos_unicos.loc[Leads_perdidos_unicos['sc_fecha'] == fecha, 'unique_id_count'].sum() +pagos

            # Calcular tasas de conversión
            # Calcular tasas de conversión con validaciones
            lead_a_contacto = (contactos / leads_tocados) * 100 if leads_tocados > 0 else 0
            contacto_a_valp = ( valp/ contactos) * 100 if contactos > 0 and valp > 0 else 0
            lead_a_valp=(valp / leads_tocados) * 100 if leads_tocados > 0 and valp > 0 else 0
            
            contac_corr=(contactos / leads_asesor) * 100 if contactos > 0 and leads_asesor > 0 else 0
            contac=(contactos_unicos / leads_asesor_unicos) * 100 if contactos_unicos > 0 and leads_asesor_unicos > 0 else 0
            valp_con = (valp / contactos_unicos) * 100 if valp > 0 and contactos_unicos > 0 else 0
            pago_valp_paso=(pagos/valp)* 100 if valp > 0 and pagos > 0 else 0
            pago_valp_acumu=(pagos/contactos_unicos)* 100 if contactos_unicos > 0 and pagos > 0 else 0
            perd_cont=(perdidos/contactos_unicos)* 100 if perdidos > 0 and contactos_unicos > 0 else 0
            
            # Agregar datos al diccionario
            if fecha not in chart_data_dict:
                chart_data_dict[fecha] = []
                chart_data_dict2[fecha] = []
            chart_data_dict[fecha].extend([ leads_asesor, contac_corr,contactos,leads_asesor_unicos, contac,contactos_unicos,valp_con,valp_vll,valp, perdidos,perd_cont,pagos,pago_valp_paso,pago_valp_acumu])
            chart_data_dict2[fecha].extend([contac_corr,contac,valp_con,perd_cont,pago_valp_paso,pago_valp_acumu])
    
                
        # Convertir el diccionario en un DataFrame
        chart_data2 = pd.DataFrame(chart_data_dict).set_index('Métrica')
        chart_data3 = pd.DataFrame(chart_data_dict2).set_index('Métrica')

    chart_data1 = chart_data3.loc[['%Contacto Corriente','%Contacto','%Valp','%Perdidos','%Pago (Paso)','%Pago (Acum)']].T
    # Convertir índice a tipo datetime si no lo está
    chart_data1.index = pd.to_datetime(chart_data1.index)
    chart_data1 = chart_data1[~chart_data1.index.dayofweek.isin([5, 6])]

    chart_data3 = chart_data3.loc[['%Pago (Acum)']].T
    chart_data3.index = pd.to_datetime(chart_data3.index)
    chart_data3 = chart_data3[~chart_data3.index.dayofweek.isin([5, 6])]


    chart_data2.columns = pd.to_datetime(chart_data2.columns)
    warnings.simplefilter("ignore")
    pd.options.mode.chained_assignment = None  # Ignorar warnings de pandas


    def agrupar_por(fecha_df, agrupacion_seleccionada):
        metricas_porcentaje = ['%Contacto Corriente','%Contacto','%Valp','%Perdidos','%Pago (Paso)','%Pago (Acum)']

        if agrupacion_seleccionada == "Semana":
            agrupador = fecha_df.columns.to_series().dt.to_period('W').apply(lambda r: r.start_time)
        elif agrupacion_seleccionada == "Mes":
            agrupador = fecha_df.columns.to_series().dt.to_period('M').apply(lambda r: r.start_time)
        else:
            fecha_df.columns = fecha_df.columns.strftime('%Y-%m-%d')
            return fecha_df

        # Separa métricas porcentuales y absolutas
        df_abs = fecha_df[~fecha_df.index.isin(metricas_porcentaje)]
        df_pct = fecha_df[fecha_df.index.isin(metricas_porcentaje)]

        # Agrupar absolutas con sum
        df_abs_grouped = df_abs.groupby(agrupador, axis=1).sum()

        # Agrupar porcentajes con promedio
        df_pct_grouped = df_pct.groupby(agrupador, axis=1).mean()

        # Juntar de nuevo
        df_grouped = pd.concat([df_abs_grouped, df_pct_grouped])

        # Formatear columnas
        df_grouped.columns = df_grouped.columns.strftime('%Y-%m-%d')
        
        return df_grouped
    # Aplicar la agrupación seleccionada

    chart_data_grouped = agrupar_por(chart_data2, agrupacion_seleccionada)
            
    for col in chart_data_grouped.index:
        if col in [ '%Contacto Corriente','%Contacto','%Valp','%Perdidos','%Pago (Paso)','%Pago (Acum)']:  # Asumiendo que estas son las filas donde están los porcentajes
            for fecha in chart_data_grouped.columns:
                if chart_data_grouped.loc[col, fecha] > 0:  # Asegurar que el valor no sea 0 antes de formatearlo
                        chart_data_grouped.loc[col, fecha] = "{:.1f}%".format(chart_data_grouped.loc[col, fecha])
                else:
                        chart_data_grouped.loc[col, fecha] = "0%"
        else:
            for fecha in chart_data_grouped.columns:
                if chart_data_grouped.loc[col, fecha] >= 0:  # Asegurar que el valor no sea 0 antes de formatearlo
                    chart_data_grouped.loc[col, fecha] = "{:.0f}".format(chart_data_grouped.loc[col, fecha])

    st.write("Tipificaciones únicas de todos los asesores")
    st.dataframe(chart_data_grouped, use_container_width=False,height=530,)       
        
        # Filtrar por asesores seleccionados (si hay selección)
    if asesores_seleccionados:  # si estás usando st.multiselect
        asesores_a_mostrar = asesores_seleccionados
    else:
        asesores_a_mostrar = asesores_unicos


    consolidado_dict = {
    'Métrica': ['Gestiones','%Contacto Corriente', 'Contacto', 'Gestion Unicos','%Contacto', 'Contacto Unicos','%Valp',
                'Valp Unicos (+VLL)', 'Valp Unicos', 'Perdidos Unicos', '%Perdidos','Pagos',
                   
                '%Pago (Paso)', '%Pago (Acum)']
    }
    for asesor in asesores_a_mostrar:
        # Filtrar todos los DataFrames por asesor y fecha
        gestion = Leads_gestionados[
            (Leads_gestionados['nombre_asesor'] == asesor) &
            (Leads_gestionados['sc_fecha'] >= min_fecha) &
            (Leads_gestionados['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        contacto = Leads_contactos[
            (Leads_contactos['nombre_asesor'] == asesor) &
            (Leads_contactos['sc_fecha'] >= min_fecha) &
            (Leads_contactos['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        gestion_unicos = Leads_gestionados_unicos[
            (Leads_gestionados_unicos['nombre_asesor'] == asesor) &
            (Leads_gestionados_unicos['sc_fecha'] >= min_fecha) &
            (Leads_gestionados_unicos['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        contacto_unicos = Leads_contactos_unicos[
            (Leads_contactos_unicos['nombre_asesor'] == asesor) &
            (Leads_contactos_unicos['sc_fecha'] >= min_fecha) &
            (Leads_contactos_unicos['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        valp_vll = Leads_valp_vll[
            (Leads_valp_vll['nombre_asesor'] == asesor) &
            (Leads_valp_vll['sc_fecha'] >= min_fecha) &
            (Leads_valp_vll['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        valp = Leads_valp[
            (Leads_valp['nombre_asesor'] == asesor) &
            (Leads_valp['sc_fecha'] >= min_fecha) &
            (Leads_valp['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        perdidos = Leads_perdidos_unicos[
            (Leads_perdidos_unicos['nombre_asesor'] == asesor) &
            (Leads_perdidos_unicos['sc_fecha'] >= min_fecha) &
            (Leads_perdidos_unicos['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()

        pagos = Leads_pagos[
            (Leads_pagos['nombre_asesor'] == asesor) &
            (Leads_pagos['sc_fecha'] >= min_fecha) &
            (Leads_pagos['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()
        

        # Cálculos de porcentaje
        contac_corr = (contacto / gestion) * 100 if gestion > 0 else 0
        contac_pct = (contacto_unicos / gestion_unicos) * 100 if gestion_unicos > 0 else 0
        valp_pct = (valp / contacto_unicos) * 100 if contacto_unicos > 0 else 0
        perd_pct = (perdidos / contacto_unicos) * 100 if contacto_unicos > 0 else 0
        pago_paso = (pagos / valp) * 100 if valp > 0 else 0
        pago_acum = (pagos / contacto_unicos) * 100 if contacto_unicos > 0 else 0

        consolidado_dict[asesor] = [
            gestion, contac_corr,contacto, gestion_unicos,  contac_pct, contacto_unicos,valp_pct, valp_vll, valp,
            perdidos,perd_pct, pagos,  
            pago_paso, pago_acum
        ]
    df_consolidado = pd.DataFrame(consolidado_dict).set_index('Métrica')





    # Formatear porcentajes
    for metrica in ['%Contacto Corriente','%Contacto','%Valp','%Perdidos','%Pago (Paso)','%Pago (Acum)']:
        df_consolidado.loc[metrica] = df_consolidado.loc[metrica].apply(lambda x: f"{x:.1f}%" if x > 0 else "0%")
    for metrica in ['Gestiones', 'Contacto', 'Gestion Unicos','Contacto Unicos','Valp Unicos (+VLL)','Valp Unicos','Perdidos Unicos','Pagos']:
        df_consolidado.loc[metrica] = df_consolidado.loc[metrica].apply(lambda x: f"{int(x)}")

    st.markdown(f'<h4 style="color:#01579b;font-weight:bold;">Consolidado por Asesor</h4>', unsafe_allow_html=True)
    st.write("Total de tipificaciones únicas en el rango de fecha filtrado. Vista por asesor")
    st.dataframe(df_consolidado, use_container_width=True,height=530)


    # Título del dashboard

    st.markdown(f'<h4 style="color:#01579b;font-weight:bold;">Gestión último Status por Asesor</h4>', unsafe_allow_html=True)
    columa1, columa2 = st.columns([1, 1])   
    with columa1:
        opcion_filtro = st.radio(
            "Mostrar asesores por:",
            options=["Asesores Activos","Todos"]
        )
    with columa2:
        vll_filtro = st.radio(
            "Filtro Vps:",
            options=["Sin Volver a Llamar","Con Volver a Llamar"]
        )
    
    #if asesores_seleccionados:  # si estás usando st.multiselect
     #   asesores_a_mostrar = asesores_seleccionados
    #else:
     #   asesores_a_mostrar = asesores_unicos

    if (opcion_filtro=="Asesores Activos"):
        if campana_seleccionada == "25.2":
            asesores=["Andrea Araujo","Sergio Valderrama","Angelica Iparraguirre","Rosa Ugarte","Juan Manuel","Fiorella Lanegra"]
        else:
            asesores=["Cinthia Orosco","Erwin Vital","Daniel Zapata","Meri Ricalde"]
    else:
        if asesores_seleccionados:
            asesores=asesores_seleccionados
        else:
            asesores=asesores_unicos
    
    if (vll_filtro=="Con Volver a Llamar"):
        no_efectivos = {"Sin contacto", 1, 2, 3, 4, None}
    else:
        no_efectivos = {"Sin contacto", 1, 2, 3, 4, None,"Volver a llamar"}
            
    filtered_data_2= filtered_data[filtered_data['nombre_asesor'].isin(asesores)]
    Leads_pagos= Leads_pagos[Leads_pagos['nombre_asesor'].isin(asesores)]
 
    print(filtered_data_2.columns)

        # Definición de categorías
    
    positivos = ["Evaluando", "Interesado", "Registrado a evento", "Se inscribio", "Pagante", "Promesa de pago"]
    negativos = ["Perdido", "Black List"]
    
    volver_llamar=["Volver a llamar"]
    filtered_data_2['sc_fecha'] = pd.to_datetime(filtered_data_2['sc_fecha'])
    data_contacto = filtered_data_2[~filtered_data_2["desc_resultado_1"].isin(no_efectivos)]
    ultimos_diarios = data_contacto.sort_values("sc_fecha").groupby(["sc_fecha", "nombre_asesor", "id_prometeo"]).last().reset_index()

    pagos = Leads_pagos[
            (Leads_pagos['nombre_asesor'] == asesor) &
            (Leads_pagos['sc_fecha'] >= min_fecha) &
            (Leads_pagos['sc_fecha'] <= max_fecha)
        ]['unique_id_count'].sum()
    
    def generar_resumen(df_campaña, data_pago):
        id_unicos = df_campaña.groupby("nombre_asesor")["id_prometeo"].nunique().rename("LEADS GESTIONADOS")

        ids_contacto = df_campaña[~df_campaña["desc_resultado_1"].isin(no_efectivos)]
        contacto_efectivo = ids_contacto.groupby("nombre_asesor")["id_prometeo"].nunique().rename("CONTACTO EFECTIVO")

        df_valid = df_campaña[~df_campaña["desc_resultado_1"].isin(no_efectivos)].copy()
        df_valid = df_valid.sort_values("sc_fecha")
        ultimos = df_valid.groupby(["nombre_asesor", "id_prometeo"]).last().reset_index()

        valoracion_positiva = ultimos[ultimos["desc_resultado_1"].isin(positivos)] \
            .groupby("nombre_asesor")["id_prometeo"].nunique().rename("VALORACIÓN POSITIVA")

        perdido_blacklist = ultimos[ultimos["desc_resultado_1"].isin(negativos)] \
            .groupby("nombre_asesor")["id_prometeo"].nunique().rename("PERDIDO")

        volver_a_llamar = ultimos[ultimos["desc_resultado_1"].isin(volver_llamar)] \
            .groupby("nombre_asesor")["id_prometeo"].nunique().rename("VOLVER A LLAMAR")

        # Procesar base de pagos externa
        data_pago['Fecha de Pago de Boleta'] = pd.to_datetime(data_pago['Fecha de Pago'], format="%d/%m/%Y", errors='coerce')
        data_pago['sc_fecha'] = data_pago['Fecha de Pago de Boleta'].dt.date
        pagos = Leads_pagos.groupby("nombre_asesor")["unique_id_count"].nunique().rename("VENTA")
        pagos.index.name = "nombre_asesor"

        # Unir todas las métricas
        resumen = pd.concat([
            id_unicos,
            contacto_efectivo,
            valoracion_positiva,
            perdido_blacklist,
            pagos
        ], axis=1).fillna(0)

        # Calcular KPIs porcentuales
        resumen["% LEAD A CONTACTO EFECTIVO"] = (resumen["CONTACTO EFECTIVO"] / resumen["LEADS GESTIONADOS"]) * 100
        resumen["% CONTACTO EFECTIVO A VP"] = (resumen["VALORACIÓN POSITIVA"] / resumen["CONTACTO EFECTIVO"]) * 100
        resumen["% CONTACTO EFECTIVO A PERDIDO"] = (resumen["PERDIDO"] / resumen["CONTACTO EFECTIVO"]) * 100
        resumen["% VP A VENTA"] = (resumen["VENTA"] / resumen["VALORACIÓN POSITIVA"]) * 100

        resumen = resumen.reset_index()
        return resumen

    # Generar resumen
    def calcular_metricas_diarias(df, data_pago):
        resumenes = []

        for fecha in sorted(df['sc_fecha'].dt.date.unique()):
            df_dia = df[df['sc_fecha'].dt.date == fecha]
            pago_dia = data_pago[data_pago['sc_fecha'] == fecha]

            resumen = generar_resumen(df_dia, pago_dia)
            resumen["fecha"] = fecha
            resumenes.append(resumen)

        df_resumenes = pd.concat(resumenes)
        return df_resumenes
    resumen_df = generar_resumen(filtered_data_2, data_pago)

    # Transponer para mostrar métricas como filas
    resumen_transpuesto = resumen_df.set_index("nombre_asesor").T.copy()

    # Formatear porcentajes
    metricas_porcentaje = [
        "% LEAD A CONTACTO EFECTIVO",
        "% CONTACTO EFECTIVO A VP",
        "% CONTACTO EFECTIVO A PERDIDO",
        "% VP A VENTA"
    ]

    for metrica in metricas_porcentaje:
        resumen_transpuesto.loc[metrica] = resumen_transpuesto.loc[metrica].apply(lambda x: f"{x:.0f}%" if x > 0 else "0%")
      
    # Formato entero para métricas absolutas
    metricas_enteras = [
        "LEADS GESTIONADOS",
        "CONTACTO EFECTIVO",
        "VALORACIÓN POSITIVA",
        "PERDIDO",
        "VENTA"
    ]

    for metrica in metricas_enteras:
        resumen_transpuesto.loc[metrica] = resumen_transpuesto.loc[metrica].apply(lambda x: f"{int(x)}")

    # Orden final de las métricas
    orden_metrico = [
        "LEADS GESTIONADOS",
        "% LEAD A CONTACTO EFECTIVO",
        "CONTACTO EFECTIVO",
        "% CONTACTO EFECTIVO A VP",
        "VALORACIÓN POSITIVA",
        "% CONTACTO EFECTIVO A PERDIDO",
        "PERDIDO",
        "% VP A VENTA",
        "VENTA"
    ]
    resumen_transpuesto = resumen_transpuesto.loc[orden_metrico]

    st.dataframe(resumen_transpuesto, use_container_width=True)
    
    def calcular_metricas_por_periodo(df, data_pago, agrupacion_seleccionada):
        # Asegurar formato datetime y eliminar fechas inválidas
        df['sc_fecha'] = pd.to_datetime(df['sc_fecha'], errors='coerce')
        data_pago['Fecha de Pago'] = pd.to_datetime(data_pago['Fecha de Pago'], format="%d/%m/%Y", errors='coerce')
        data_pago['sc_fecha'] = data_pago['Fecha de Pago'].dt.date
        df = df.dropna(subset=['sc_fecha'])
        data_pago = data_pago.dropna(subset=['sc_fecha'])

        # Determinar frecuencia
        if agrupacion_seleccionada == 'Semana':
            df['periodo'] = df['sc_fecha'].dt.to_period('W').dt.start_time.dt.date
            data_pago['periodo'] = pd.to_datetime(data_pago['sc_fecha']).dt.to_period('W').dt.start_time.dt.date
        elif agrupacion_seleccionada == 'Mes':
            df['periodo'] = df['sc_fecha'].dt.to_period('M').dt.to_timestamp().dt.date
            data_pago['periodo'] = pd.to_datetime(data_pago['sc_fecha']).dt.to_period('M').dt.to_timestamp().dt.date
        else:
            df['periodo'] = df['sc_fecha']
            data_pago['periodo'] = pd.to_datetime(data_pago['sc_fecha'])

        resumenes = []

        for periodo in sorted(df['periodo'].unique()):
            df_periodo = df[df['periodo'] == periodo]
            pago_periodo = data_pago[data_pago['periodo'] == periodo]

            resumen = generar_resumen(df_periodo, pago_periodo)
            resumen["fecha"] = periodo
            #resumen.loc[metrica] = resumen.loc[metrica].apply(lambda x: f"{x:.0f}%" if x > 0 else "0%")

            resumenes.append(resumen)

        df_resumenes = pd.concat(resumenes, ignore_index=True)
        return df_resumenes

    #resumen_diario = calcular_metricas_diarias(filtered_data_2, data_pago)
    resumen_diario = calcular_metricas_por_periodo(filtered_data_2, data_pago, agrupacion_seleccionada)
    

    # Convertir columnas de fecha y asesor en índices para pivotar
    def preparar_chart(df, metrica):
        df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        pivot = df.pivot(index="fecha", columns="nombre_asesor", values=metrica).fillna(0)
        pivot_tabla_porcentaje = pivot.applymap(lambda x: f"{x:.0f}%" if x > 0 else "0%")
        return pivot,pivot_tabla_porcentaje
    def preparar_chart_z(df, metrica):
        df['sc_fecha'] = pd.to_datetime(df['fecha']).dt.date
        pivot = df.pivot(index="sc_fecha", columns="nombre_asesor", values=metrica).fillna(0)
        return pivot

        # Crear los 4 charts
    chart1_data = preparar_chart_z(resumen_diario, "LEADS GESTIONADOS")
    chart21_data_line,chart21_data_tabla = preparar_chart(resumen_diario, "% LEAD A CONTACTO EFECTIVO")
    chart2_data_line,chart2_data_tabla = preparar_chart(resumen_diario, "% CONTACTO EFECTIVO A VP")
    chart3_data_line,chart3_data_tabla = preparar_chart(resumen_diario, "% CONTACTO EFECTIVO A PERDIDO")
    chart4_data_line,chart4_data_tabla = preparar_chart(resumen_diario, "% VP A VENTA")
    print("JAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    print(df_consolidado)
    print(resumen_diario)
    

    Leads_pagos = Leads_pagos.rename(columns={'Asesor Homologado': 'nombre_asesor'})
    def preparar_df(df, nombre_df):
        df_filtrado = df[
            (df['sc_fecha'] >= min_fecha) &
            (df['sc_fecha'] <= max_fecha) &
            (df['nombre_asesor'].isin(asesores_a_mostrar))
        ]
        df_grouped = df_filtrado.groupby(['sc_fecha', 'nombre_asesor'])['unique_id_count'].sum().reset_index()
        df_pivot = df_grouped.pivot(index='sc_fecha', columns='nombre_asesor', values='unique_id_count').fillna(0)
        df_pivot = df_pivot.sort_index()
        return df_pivot
    df_gestion=preparar_df(Leads_gestionados_unicos, "gestiones")
    df_contactos_ef = preparar_df(Leads_contactos_efectivos, "contactos_ef")
    df_valp = preparar_df(Leads_valp, "valp")
    df_perdidos = preparar_df(Leads_perdidos_unicos, "perdidos")
    df_pagos = preparar_df(Leads_pagos, "pagos")
    pct_lead_a_contacto = (df_contactos_ef / df_gestion.where(df_gestion != 0)).fillna(0) * 100
    pct_contacto_a_vp = (df_valp / df_contactos_ef.where(df_gestion != 0)).fillna(0) * 100
    pct_contacto_a_perdido = (df_perdidos / df_contactos_ef.where(df_gestion != 0)).fillna(0) * 100
    pct_vp_a_venta = (df_pagos / df_contactos_ef.where(df_gestion != 0)).fillna(0) * 100
    print(pct_lead_a_contacto)

            
        
    
    
    #chart1_data_2 = preparar_chart_z(consolidado_dict, "Gestion Unicos")
    #chart21_data_2_line,chart21_data_2_tabla = preparar_chart(df_consolidado, "%Contacto")
    #chart2_data_2_line,chart2_data_2_tabla = preparar_chart(df_consolidado, "%Valp")
    #chart3_data_2_line,chart3_data_2_tabla = preparar_chart(df_consolidado, "%Perdidos")
    #chart4_data_2_line,chart4_data_2_tabla = preparar_chart(df_consolidado, "%Pago (Paso)")
    
        # Mostrar charts en dos filas
    st.markdown(f'<h4 style="color:#01579b;font-weight:bold;">Evolutivo de Asesores por fecha</h4>', unsafe_allow_html=True)
        # Primera fila
        # Selector de vista: Gráfico o Tabla
    vista = st.radio(
        "Selecciona la vista:",
        options=["Gráficos", "Tablas"],
        horizontal=True
    )
    # Primera fila
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<h5 style="color:#230443;font-weight:bold;">Leads Gestionados</h5>', unsafe_allow_html=True)
        if vista == "Gráficos":
            #st.line_chart(chart1_data)
            st.line_chart(df_gestion)
        else:
            st.dataframe(df_gestion.T, use_container_width=True)

    with col2:
        st.markdown(f'<h5 style="color:#230443;font-weight:bold;">Gestión a C. efectivo</h5>', unsafe_allow_html=True)
        if vista == "Gráficos":
            st.line_chart(pct_lead_a_contacto)
        else:
            st.dataframe(pct_lead_a_contacto.T, use_container_width=True)

    # Segunda fila
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f'<h5 style="color:#230443;font-weight:bold;">%C. efectivo a VP</h5>', unsafe_allow_html=True)
        if vista == "Gráficos":
            st.line_chart(pct_contacto_a_vp)
        else:
            st.dataframe(pct_contacto_a_vp.T, use_container_width=True)

    with col4:
        st.markdown(f'<h5 style="color:#230443;font-weight:bold;">%C. efectivo a Perdido</h5>', unsafe_allow_html=True)
        if vista == "Gráficos":
            st.line_chart(chart3_data_line)
        else:
            st.dataframe(chart3_data_tabla.T, use_container_width=True)
    col5, col6 = st.columns(2)
    
    
    with col5:
        st.markdown(f'<h5 style="color:#230443;font-weight:bold;">%VP a Venta</h5>', unsafe_allow_html=True)
        if vista == "Gráficos":
            st.line_chart(chart4_data_line)
        else:
            st.dataframe(chart4_data_tabla.T, use_container_width=True)
        
    with col6:
        st.write(" ")



  
    #st.markdown('<p style="font-weight:bold;">Crecimiento de GESTIÓN por Fechas</p>', unsafe_allow_html=True)

    #col1, col2 = st.columns([1, 1])
    #with col1:
     #   st.line_chart(chart_data1)
    #with col2:

     #   st.line_chart(chart_data3)

except NameError:
    st.error("Error: 'rango_fechas' no está definido. Verifica que la variable esté correctamente asignada.")


st.markdown(f'<h5 style="color:#01579b;font-weight:bold;">Métricas de COHORT - {agrupacion_seleccionada}</h5>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])
with col1:
    dias_madura = [0,1, 2, 3, 4, 5, 7, 10,100]  # Opciones en enteros
    dias_select_madura = st.selectbox("Días de maduración", options=dias_madura)
with col2:
    st.write("")
    
filtered_df['prim_tipif_dif_sin_contacto'] =filtered_df['RESPUESTA PRIM TIP DF SN CONTC']
filtered_df['prim_tipif_dif_sin_contacto_fecha'] =df['FECHA HORA DE PRIM TIP'] 
filtered_df['fecha_primera_tipif'] =filtered_df['FECHA HORA DE REGISTRO'] 
filtered_df['fecha_pagante_crm'] =filtered_df['FECHA PAGO'] 

df_cohort = filtered_df.copy()
fecha_inicio = pd.to_datetime(rango_fechas[0]).date()
fecha_fin = pd.to_datetime(rango_fechas[1]).date()


df_cohort['fecha_primera_tipif'] = pd.to_datetime(df_cohort['fecha_primera_tipif'], errors='coerce').dt.date
df_cohort['prim_tipif_dif_sin_contacto_fecha'] = pd.to_datetime(df_cohort['prim_tipif_dif_sin_contacto_fecha'], errors='coerce').dt.date

df_cohort['fecha_primera_valp'] = df_cohort[
    (df_cohort['RESPUESTA PRIM TIP DF SN CONTC'].isin(["Evaluando", "Interesado"]))
]['fecha_primera_tipif']


df_cohort['fecha_primera_valp'] = pd.to_datetime(df_cohort['fecha_primera_valp'], errors='coerce').dt.date
df_cohort = df_cohort[
    (df_cohort['fecha_primera_tipif'] >= fecha_inicio) &
    (df_cohort['fecha_primera_tipif'] <= fecha_fin)
]
df_cohort['contactado_cohort_maduracion'] = (
    (df_cohort['fecha_primera_tipif'] <= df_cohort['prim_tipif_dif_sin_contacto_fecha']) & 
    (df_cohort['prim_tipif_dif_sin_contacto_fecha'] <= df_cohort['fecha_primera_tipif'] + pd.to_timedelta(dias_select_madura, unit="D"))
).astype(int)

print(df_cohort['contactado_cohort_maduracion'])

df_cohort['perdido_cohort_maduracion'] = (
    (df_cohort['fecha_primera_tipif'] <= df_cohort['prim_tipif_dif_sin_contacto_fecha']) & 
    (df_cohort['prim_tipif_dif_sin_contacto_fecha'] <= df_cohort['fecha_primera_tipif'] + pd.to_timedelta(dias_select_madura, unit="D")) & (df_cohort['prim_tipif_dif_sin_contacto'].isin(["Perdido", "Black List"]))
).astype(int)

df_cohort['val_plus_cohort_maduracion'] = (
    (df_cohort['fecha_primera_tipif'] <= df_cohort['fecha_primera_valp']) & 
    (df_cohort['fecha_primera_valp'] <= df_cohort['fecha_primera_tipif'] + pd.to_timedelta(dias_select_madura, unit="D"))
).astype(int)

df_cohort['val_plus_cohort'] = (df_cohort['fecha_primera_tipif'] == df_cohort['fecha_primera_valp']).astype(int)
contactados_ids = df_cohort.loc[df_cohort['contactado_cohort_maduracion'] == 1, 'id_prometeo']

# Verificar si estos IDs están en la base de pagos
df_cohort['pagante_cohort'] = df_cohort['id_prometeo'].isin(contactados_ids) & df_cohort['id_prometeo'].isin(data_pago['ID PROMETEO'])

# Convertir a 1 o 0
df_cohort['pagante_cohort'] = df_cohort['pagante_cohort'].astype(int)
# Calcular métricas
leads_cohort = df_cohort.groupby('fecha_primera_tipif')['id_prometeo'].count()
contactados_cohort = df_cohort.groupby('fecha_primera_tipif')['contactado_cohort_maduracion'].sum()
val_plus_cohort = df_cohort.groupby('fecha_primera_tipif')['val_plus_cohort_maduracion'].sum()
pagante_cohort = df_cohort.groupby('fecha_primera_tipif')['pagante_cohort'].sum()
perdido_cohort = df_cohort.groupby('fecha_primera_tipif')['perdido_cohort_maduracion'].sum()

# Calcular las métricas porcentuales
pct_contactados = (contactados_cohort / leads_cohort * 100).fillna(0).astype(int)
print(pct_contactados)
pct_contacto_valp = (val_plus_cohort / contactados_cohort * 100).replace([float('inf'), -float('inf')], 0).fillna(0).round().astype(int)

print(pct_contacto_valp)
pct_lead_valp = (val_plus_cohort / leads_cohort * 100).fillna(0).astype(int)
pct_pagantes = ((pagante_cohort / contactados_cohort) * 100).replace([float('inf'), -float('inf')], 0).fillna(0).astype(int)
# Crear DataFrame final
cohort_metrics = pd.DataFrame({
    'Leads Cohort': leads_cohort,
    'Contactados Cohort': contactados_cohort,
    'Val + Cohort': val_plus_cohort,
    'Perdidos' :perdido_cohort,
    'Pagante Cohort': pagante_cohort,
    '% Contactados Cohort': pct_contactados,
    '% Contacto a Valp': pct_contacto_valp,
    '% lead a Valp': pct_lead_valp,
    '% Pagantes Cohort': pct_pagantes
})

# Transponer para que las fechas sean columnas
cohort_metrics = cohort_metrics.T
chart_data = cohort_metrics.loc[['% Contactados Cohort', '% Contacto a Valp', '% lead a Valp']].T
chart_data.index = pd.to_datetime(chart_data.index)

chart_data = chart_data[~chart_data.index.dayofweek.isin([5, 6])]

cohort_metrics.columns = pd.to_datetime(cohort_metrics.columns, errors='coerce') 
# Función para agrupar por semana o mes en el DataFrame de cohortes
def agrupar_por_cohort(fecha_df, agrupacion_seleccionada):
    metricas_porcentaje = ['% Contactados Cohort', '% Contacto a Valp', '% lead a Valp', '% Pagantes Cohort']

    fecha_df.columns = pd.to_datetime(fecha_df.columns, errors='coerce')
    df_abs = fecha_df[~fecha_df.index.isin(metricas_porcentaje)]
    df_pct = fecha_df[fecha_df.index.isin(metricas_porcentaje)]

    if agrupacion_seleccionada == "Semana":
        agrupador = fecha_df.columns.to_series().dt.to_period('W').apply(lambda r: r.start_time)
    elif agrupacion_seleccionada == "Mes":
        agrupador = fecha_df.columns.to_series().dt.to_period('M').apply(lambda r: r.start_time)
    else:
        fecha_df.columns = fecha_df.columns.strftime('%Y-%m-%d')
        return fecha_df

    # Sumar métricas absolutas
    df_abs_grouped = df_abs.groupby(agrupador, axis=1).sum()

    # Promediar métricas de porcentaje
    df_pct_grouped = df_pct.groupby(agrupador, axis=1).mean()

    # Unir ambas
    df_grouped = pd.concat([df_abs_grouped, df_pct_grouped])

    # Formatear columnas como fechas
    df_grouped.columns = df_grouped.columns.strftime('%Y-%m-%d')
    
    return df_grouped

# Aplicar la agrupación seleccionada a cohort_metrics
cohort_metrics_grouped = agrupar_por_cohort(cohort_metrics, agrupacion_seleccionada)
# Formatear los valores porcentuales y numéricos de la tabla resultante
for col in cohort_metrics_grouped.index:
    if col in ['% Contactados Cohort', '% Contacto a Valp', '% lead a Valp', '% Pagantes Cohort']:  # Asumiendo que estas son las filas donde están los porcentajes
        for fecha in cohort_metrics_grouped.columns:
            if cohort_metrics_grouped.loc[col, fecha] > 0:  # Asegurar que el valor no sea 0 antes de formatearlo
                cohort_metrics_grouped.loc[col, fecha] = "{:.1f}%".format(cohort_metrics_grouped.loc[col, fecha])
            else:
                cohort_metrics_grouped.loc[col, fecha] = "0%"  # Si es 0, poner 0.00%

    else:  # Para las filas de números que no son porcentajes
        for fecha in cohort_metrics_grouped.columns:
            if cohort_metrics_grouped.loc[col, fecha] >= 0:  # Asegurar que el valor no sea 0 antes de formatearlo
                cohort_metrics_grouped.loc[col, fecha] = int(cohort_metrics_grouped.loc[col, fecha])
st.dataframe(cohort_metrics_grouped)

st.markdown('<p style="font-weight:bold;">Crecimiento de GESTIÓN COHORT por Fechas</p>', unsafe_allow_html=True)
st.line_chart(chart_data)

 #(df['fecha_registro_periodo'] >= pd.to_datetime(start_date)) &
 #(df['fecha_registro_periodo'] <= pd.to_datetime(end_date))
# Resumen de métricas
st.write("")
st.write("")
st.markdown(
    '<h3 style="color:#7E57C2;font-weight:bold;">Resumen de métricas Total</h3>',
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
    vll = (
        (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VOLVER_A_LLAMAR")
    )
    # Contar la cantidad de leads valp
    leads_vll = filtered_df[vll]['id_prometeo'].nunique()
    st.metric("Volver a llamar", format_with_commas(leads_vll))
with col5:
    # Contar la cantidad de leads valp
    valp_condition = (
        (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") 
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
    (filtered_df['ult_tipf_dif_sin_contacto'].isin(["Interesado", "Evaluando", "Volver a llamar"]))& 
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

with col3:
    st.markdown('<h5 style="color:#003399;"> CALC- Valp</h5>', unsafe_allow_html=True)

    seguimiento_vivo = filtered_df[
        (filtered_df['dias_sin_contacto'] <= 3) & 
        (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") 
    ]
    val_vivo = filtered_df[
    (filtered_df['dias_sin_contacto'] <= 3) & 
    (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_VALORACIONES_POSITIVAS") &
    (filtered_df['ult_tipf_dif_sin_contacto'].isin(['Evaluando', 'Interesado']))  
    ]
    pps = filtered_df[
        (filtered_df['agrupacion_tipificacion_actual'] == "VALORES_PROMESA_DE_PAGO") & 
        (filtered_df['flg_convocatoria'] == "Convo")
    ]

    # Calcular Q para cada filtro (número de registros únicos)
    q_seguimiento_vivo = seguimiento_vivo['id_prometeo'].nunique()
    q_val_vivo = val_vivo['id_prometeo'].nunique()
    q_pps = pps['id_prometeo'].nunique()

    # Tasas de conversión
    tasa_seguimiento_vivo = 0.05  # 5%
    tasa_val_vivo = 0.30  # 30%
    tasa_pps = 0.80  # 80%

    # Calcular los pagos potenciales
    pagos_seguimiento_vivo = q_seguimiento_vivo * tasa_seguimiento_vivo
    pagos_val_vivo = q_val_vivo * tasa_val_vivo
    pagos_pps = q_pps * tasa_pps

    # Construir la tabla
    data = {
        'Q': [q_seguimiento_vivo, q_val_vivo, q_pps],
        '% de conversión': [f"{tasa_seguimiento_vivo*100}%", f"{tasa_val_vivo*100}%", f"{tasa_pps*100}%"],
        'Pagos potenciales': [round(pagos_seguimiento_vivo), round(pagos_val_vivo), round(pagos_pps)]
    }
    tabla_resultado = pd.DataFrame(data, index=['Seguimiento vivo', 'Val+ vivo', 'PPs'])

    # Agregar total
    total_q = sum(data['Q'])
    total_pagos = sum(data['Pagos potenciales'])

    tabla_resultado.loc['Total'] = [total_q, '', total_pagos]

    tabla_resultado = tabla_resultado.style.highlight_max(subset='Pagos potenciales', axis=0, 
                                   props='color: #990000;')

    st.dataframe(tabla_resultado)

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
# Restablecer el índice para que sea visible en AgGrid
tabla = tabla.reset_index()
# Mostrar la tabla en Streamlit
st.markdown('<h5 style="color:#003399;">Perdidos / Días sin contacto</h5>', unsafe_allow_html=True)

gb = GridOptionsBuilder.from_dataframe(tabla)
gb.configure_side_bar()
gb.configure_column("ult_tipf_dif_sin_contacto_2", header_name="TIPIFICACION 2🔹", cellStyle={'fontWeight': 'bold'})  
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True) 
grid_options = gb.build()

col1,col2=st.columns([3, 2])
with col1:
    AgGrid(tabla, gridOptions=grid_options, fit_columns_on_grid_load=False, height=400, theme="blue", width='100%')

with col2:  
    st.write("")
    filtered_df4 = filtered_df
    min_dsnc = filtered_df4['dias_sin_contacto'].min()
    max_dsnc = filtered_df4['dias_sin_contacto'].max()
    bins_dsnc = [min_dsnc, 7, 14, 21, 30, max_dsnc]  # Definido manualmente
    labels_dsnc = [f"{bins_dsnc[i]}-{bins_dsnc[i+1]-1}" 
                        for i in range(len(bins_dsnc) - 1)]

    # Filtrar los datos donde 'ult_tipf_dif_sin_contacto' es igual a "Perdido"
    filtered_df4_pp = filtered_df4[filtered_df4['agrupacion_tipificacion_actual'] == "VALORES_PROMESA_DE_PAGO"]
    filtered_df4_pp.loc[:, 'agrupacion_tipificacion_actual'] = filtered_df4_pp['agrupacion_tipificacion_actual'].replace("VALORES_PROMESA_DE_PAGO", "PP")
 # Obtener los valores únicos de 'ult_tipf_dif_sin_contacto_2' solo para los casos "Perdido"
    filtered_df4_pp = filtered_df4_pp.copy()
    filtered_df4_pp.loc[:, 'dsnc'] = pd.cut(filtered_df4_pp.loc[:, 'dias_sin_contacto'], bins=bins_dsnc, labels=labels_dsnc, right=False)
    # Crear la tabla dinámica con pivot_table
    tabla = pd.pivot_table(filtered_df4_pp, index='agrupacion_tipificacion_actual', columns='dsnc', aggfunc='size', fill_value=0, observed=False)
    tabla['Total'] = tabla.sum(axis=1)
    # Restablecer el índice para que sea visible en AgGrid
    tabla = tabla.rename_axis("📌 Tipificación").reset_index()
    # Mostrar la tabla en Streamlit
    st.markdown('<h5 style="color:#003399;">PP / Días sin contacto</h5>', unsafe_allow_html=True)
    # Configuración de la tabla
    
    st.dataframe(tabla,hide_index=True)
col1,col2=st.columns(2)
with col1:

    # Aplicar prefiltro: Excluir "Sin contacto" en la columna "prim_tipif_no_TI"
    filtered_df_mad = filtered_df[filtered_df["prim_tipif_dif_sin_contacto"] != "Sin contacto"].copy()

    # Eliminar filas sin fecha de primer toque o fecha de pago
    filtered_df_mad = filtered_df_mad.dropna(subset=["prim_tipif_dif_sin_contacto_fecha", "fecha_pagante_crm"])

    # Convertir columnas de fecha a tipo datetime
    filtered_df_mad["prim_tipif_dif_sin_contacto_fecha"] = pd.to_datetime(filtered_df_mad["prim_tipif_dif_sin_contacto_fecha"])
    filtered_df_mad["fecha_pagante_crm"] = pd.to_datetime(filtered_df_mad["fecha_pagante_crm"])

    # Calcular maduración (días entre primer toque y pago)
    filtered_df_mad["maduracion_dias"] = (filtered_df_mad["fecha_pagante_crm"] - filtered_df_mad["prim_tipif_dif_sin_contacto_fecha"]).dt.days

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
    filtered_df_mad = filtered_df[filtered_df["prim_tipif_dif_sin_contacto"] != "Sin contacto"].copy()

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
st.markdown('<h5 style="color:#003399;">Toques / Días de Vida</h5>', unsafe_allow_html=True)

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
    tabla = tabla.reset_index()
    # Configurar opciones de la tabla
    gb = GridOptionsBuilder.from_dataframe(tabla)
    gb.configure_side_bar()
    # Aplicar estilo al índice (columna "ID")
    gb.configure_column("cantidad_tipificaciones", header_name="Toques 🔹", cellStyle={'fontWeight': 'bold'})  
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, editable=True)
    grid_options = gb.build()
    
    AgGrid(tabla, gridOptions=grid_options, fit_columns_on_grid_load=False, height=400, theme="blue")


# "turno"  == mañana tarde 
#flg_traslados = 0 normla 1 traslados

columnas_seleccionadas = ['id_prometeo', 'PROGRAMA','MUNDO_CALCULADO', 'modalidad_programa','turno','flg_traslados','canal_atribucion', 'subcanal','fecha_registro_periodo']
filtered_dff = filtered_df[columnas_seleccionadas]
st.write("")
st.dataframe(filtered_dff,hide_index=True)



