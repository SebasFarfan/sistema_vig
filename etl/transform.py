import pandas as pd
import unicodedata


# =========================== Funciones para las diferentes tablas ==================

# obtener info de dataframe
def informe_vig(df):
    info = df.info()
    return info

# convertir a minúsculas los nombres de columnas
def normalizar_columnas(df):
    df.columns = df.columns.str.lower()
    return df

# Convertir los datos a tipo fecha
def convertir_fecha(df, columna):
    
    fechas_limpias = df[columna].str.lower()
    fechas_limpias = fechas_limpias.str.replace('ene', 'jan', regex=False)
    fechas_limpias = fechas_limpias.str.replace('abr', 'apr', regex=False)
    fechas_limpias = fechas_limpias.str.replace('ago', 'aug', regex=False)
    fechas_limpias = fechas_limpias.str.replace('dic', 'dec', regex=False)
    
    # definimos formatos identificados
    formatos = ['%d-%m-%y', '%m-%d-%y', '%d-%b-%y', '%d/%m/%Y',  '%d-%b.-%y']

    df[columna+'_norm'] = pd.NaT
    
    
    for fmt in formatos:
        fechas_convertidas = pd.to_datetime(fechas_limpias, format=fmt, errors='coerce')
        df[columna+'_norm'] = df[columna+'_norm'].fillna(fechas_convertidas)
    
    return df
        

# convertir_mayuscula
def convertir_mayuscula_primera_letra(df):
    
    # buscamos la columna de texto
    col_texto = df.select_dtypes(include= ['str']).columns
    
    
    # aplica el formato
    for col in col_texto:
        df[col] = df[col].str.title()
    
    return df

# quitar espacios 
def quitar_espacios(df):
    # buscamos columnas de texto
    col_texto = df.select_dtypes(include=['str']).columns
    
    # aplica formato
    for col in col_texto:
        df[col] = df[col].str.strip()
    return df
    
# pasar a minusculas y quitar tildes
def limpiar_texto(celda):
    if isinstance(celda, str):
        texto = celda.lower()
        # descomponemos los acentos
        texto = unicodedata.normalize('NFD', texto)
        # filtramos y eliminamos los simbolos de tildes
        texto = ''.join([c for c in texto if unicodedata.category(c) != 'Mn'])
        return texto
    return celda

# Arreglar la columna de Empresa
def convertir_columna_empresa(df):
    df['empresa'] = df['empresa'].str.title()
    return df

# arreglar columna objetivos
def convertir_columnas(df):
    columnas = ['objetivo', 'empresa']
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title()
    return df

# Convertir las fechas de la tabla salida
def convertir_fechas_incio_final(df, f_inicio, f_final):
    df = convertir_fecha(df, f_inicio)
    df = convertir_fecha(df, f_final)
    return df

def convertir_columna_str(df, col):
    # Convertir la columna a string (eliminando decimales si se cargó como float)
    df[col] = df[col].astype(str).str.split('.').str[0]
    # Rellenar con ceros a la izquierda (ajusta el número '8' según el largo de tu país)
    df[col] = df[col].str.zfill(8)
    
    return df


# ===================================================================================

# --------Limpiar la tabla vigilantes-----------------

def limpiar_vig(df):
    # normalizar columnas
    df = normalizar_columnas(df)
    
    #  quitar espacios inicio y final
    df = quitar_espacios(df)
        
    # normalizar registros
    df = convertir_mayuscula_primera_letra(df)
    
    # eliminar filas con valores vacios
    df = df.dropna()
    
    # convertir tipos
    df = convertir_fecha(df, 'ftramite')
    
    # convertir la columna dni a str
    df = convertir_columna_str(df, 'dni')
    
    return df
    

# ----------- transformar tabla Empresas seguridad -------------

def limpiar_emp_seg(df):
    # normalizar columnas
    df = normalizar_columnas(df)
    
    #  quitar espacios inicio y final
    df = quitar_espacios(df)
    
    df = convertir_columna_empresa(df)
    
    df = convertir_fecha(df, 'fecha de notificacion')
    
    
    return df


# ----------- transformar tabla objetivos----------------------------

def limpiar_objetivos(df):
    
    # normalizar columnas
    df = normalizar_columnas(df)
    
    # quitar espacios inicio y final
    df = quitar_espacios(df)
    
    # normalizar datos columnas
    df = convertir_columnas(df)
    
    # filtrar los que tienen campo objetivo vacio
    df = df.dropna(subset=['objetivo'])
    
    # eliminar duplicados por la columna 'objetivo'
    df = df.drop_duplicates(subset=['objetivo'])
        
    return df

# ------------------transformar df obetivos-vigilantes----------------

def limpiar_obj_vig(df):
    
    # normalizar columnas
    df = normalizar_columnas(df)
    
    # quitar espacios inicio y final
    df = quitar_espacios(df)
    
    # poner la primera letra en mayuscula de cada columna
    columnas = ['vigilante', 'objetivo']
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title()
    
    # convertir los dni a str
    df = convertir_columna_str(df, 'vigilante')
    
    # eliminar los registros vacios
    df = df.dropna()
    
    return df
    
    
# --------------------transformar df salida---------------------------

def limpiar_salida(df):
    
    # normalizar columnas
    df = normalizar_columnas(df)
    
    # quitar espacios inicio y final
    df = quitar_espacios(df)
    
    # poner la primera letra en mayuscula de cada columna
    df['empresa'] = df['empresa'].astype(str).str.title()
    
    # convertir los campos fechas
    df = convertir_fechas_incio_final(df,'habinicial', 'habfinal')
    
    # Quitar filas duplicadas en todas las columnas
    df = df.drop_duplicates()

    # limpiar los vacios 
    df = df.dropna()
    
    # convertir a string
    df['contacto'] = df['contacto'].astype("string")

    return df

# ===================================================================================

#     Se Crean la estructura para exportar a una base de datos

# ---------------------Tabla EMPRESA-------------------------------------------------
def crear_tabla_empresa_bd(df):
    columnas_empresas = ['empresa', 'domempresa', 'cuit', 'fecha de notificacion_norm']
    df_empresas = df[columnas_empresas].drop_duplicates(subset=['empresa']).copy()
    df_empresas.insert(0, 'id_empresa', range(1, len(df_empresas) + 1))
    return df_empresas

# --------------------Tabla OBJETIVOS-----------------------------------------------
def crear_tabla_obj_bd(df_obj, df_empresa):
    columnas_obj = ['id', 'objetivo', 'dirobjetivo', 'horario', 'unidad regional', 'empresa']
    df_obj = df_obj[columnas_obj].copy()
    df_obj = df_obj.merge(df_empresa[['id_empresa', 'empresa']], on='empresa', how='left')
    df_obj = df_obj.drop(columns=['empresa'])
    return df_obj


# -------------------Tabla VIGILANTES------------------------------------------------
def crear_tabla_vig_db(df_vig, df_empresa):
    columnas_vig = ['dni', 'apellido', 'nombres', 'empresas', 'estado', 'ftramite_norm']
    
    df_vig = df_vig[columnas_vig].copy()
    df_vig = df_vig.merge(
    df_empresa[['id_empresa', 'empresa']], left_on='empresas', right_on='empresa', how='left')
    
    df_vig = df_vig.drop(columns=['empresa', 'empresas'])
    
    return df_vig

# -----------------Tabla OBJETIVO VIGILANTE --------------------------—--------------
def crear_tabla_obj_vig_db(df_obj_vig, df_obj, df_vig):
    # columnas_obj_vig = ['id', 'vigilante', 'objetivo']
    df_intermedio = df_obj_vig.copy()
    df_intermedio = df_intermedio.merge(
        df_obj[['id', 'objetivo']],
        on='objetivo',
        how='inner'
    )
    df_intermedio = df_intermedio.drop(columns=['objetivo'])
    # renombrar columnas
    columnas_renombradas = ['id', 'dni_vigilante', 'id_objetivo']
    df_intermedio.columns = columnas_renombradas
    
    
    
    # obtener la lista de todos los DNI reales y válidos de la tabla vigilante
    dnis_validos = df_vig['dni'].unique()
    # filtrar la tabla intermedia: conservar solamente los que existen
    df_intermedio = df_intermedio[df_intermedio['dni_vigilante'].isin(dnis_validos)].copy()
    
    return df_intermedio

# ----------------Tabla SALIDA-------------------------------------------------------
def crear_tabla_salida(df_salida, df_empresa):
    df_salida_tabla = df_salida.copy()
    df_salida_tabla = df_salida_tabla.merge(
        df_empresa[['id_empresa', 'empresa']],
        on='empresa',
        how='inner'            
    )
    df_salida_tabla = df_salida_tabla.drop(columns=['empresa'])
    columnas = ['id', 'expministerial', 'expdgsp', 'contacto', 'habinicial_norm', 'habfinal_norm', 'id_empresa']
    df_salida_tabla = df_salida_tabla[columnas].copy()
    return df_salida_tabla
    

# ------------------------renombrar columnas de todas las tablas--------------------
def renombrar_columnas(df_emp, df_vig, df_obj, df_sal):
    df_emp.rename(columns={'empresa':'nombre_empresa', 'domempresa':'domicilio_empresa', 'cuit':'cuit_empresa', 'fecha de notificacion_norm':'fecha_notificacion'}, inplace=True)
    df_vig.rename(columns={'ftramite_norm':'fecha_tramite'}, inplace=True)
    df_obj.rename(columns={'id':'id_objetivo', 'objetivo':'nombre_objetivo'}, inplace=True)
    df_sal.rename(columns={'id':'id_salida', 'expministerial':'exp_ministerial', 'expdgsp':'exp_dgsp', 'habinicial_norm':'hab_inicial', 'habfinal_norm': 'hab_final'}, inplace=True)

# -----------------------convertir a string la columnas dni--------------------------
def convertir_dni(df_vig, df_vig_obj):
    
    # 1. Convertir la columna a string (eliminando decimales si se cargó como float)
    df_vig['dni'] = df_vig['dni'].astype(str).str.split('.').str[0]

    # 2. Rellenar con ceros a la izquierda (ajusta el número '8' según el largo de tu país)
    df_vig['dni'] = df_vig['dni'].str.zfill(8)
    
    # para obj_vig

    # 1. Convertir la columna a string (eliminando decimales si se cargó como float)
    df_vig_obj['dni_vigilante'] = df_vig_obj['dni_vigilante'].astype(str).str.split('.').str[0]

    # 2. Rellenar con ceros a la izquierda (ajusta el número '8' según el largo de tu país)
    df_vig_obj['dni_vigilante'] = df_vig_obj['dni_vigilante'].str.zfill(8)


    # # 3. Establecer la columna DNI como el índice ("clave primaria")
    # df.set_index('dni', inplace=True)

# ----------------------------convertir en clave primarias---------------------------
def convertir_pk(df_emp, df_vig, df_obj, df_obj_vig, df_sal):
    df_emp.set_index('id_empresa', inplace=True)
    df_vig.set_index('dni', inplace=True)
    df_obj.set_index('id_objetivo', inplace=True)
    df_obj_vig.set_index('id', inplace=True)
    df_sal.set_index('id_salida', inplace=True)
    

# ==================================================================================