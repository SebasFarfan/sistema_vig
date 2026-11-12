import sys
from pathlib import Path


# Importacion de la lógica de ETL
from etl.extract import *
from etl.transform import *
from etl.load import *
import yaml
import logging

# Configuración de Rutas

# Definir la raíz del proyecto de forma dinámica
BASE_DIR = Path(__file__).resolve().parent

# Definir la carpeta contenedora de los datos
DATA_RAW_DIR = BASE_DIR / 'data' / 'raw'

# Ruta absoluta al archivo YAML
RUTA_CONFIG_YAML = BASE_DIR / 'config.yaml'

# Rutas absolutas a los Archivos csv
RUTA_VIGILANTES = DATA_RAW_DIR / 'Vigilantes.csv'
RUTA_EMP_SEG = DATA_RAW_DIR / 'Empresas.csv'
RUTA_OBJ = DATA_RAW_DIR / 'OBJETIVOS.csv'
RUTA_OBJ_VIG = DATA_RAW_DIR / 'ObjetivoVigilante.csv'
RUTA_SALIDA = DATA_RAW_DIR / 'Salida.csv'

# ruta absoluta de logs
RUTA_LOG = BASE_DIR / 'logs' / 'etl.log'

# ===================================================================================

# configurar logging
logging.basicConfig(filename=RUTA_LOG, level=logging.INFO)

# --------------------------Ejecutar el pipeline------------------------------
def ejecutar_pipeline():
    logging.info('Iniciando ETL...')
    
    # cargar configuración
    with open(RUTA_CONFIG_YAML) as f:
        config = yaml.safe_load(f)
    
    try:
        # ==================== Extract ====================
        logging.info('Extrayendo datos...')
        # ---------------vigilantes---------------
        df_vigilantes = extraer_vigilantes(RUTA_VIGILANTES)
        # ---------------Empresas seguridad---------------
        df_emp_seg = extraer_emp_seg(RUTA_EMP_SEG)
        # ---------------Objetivos---------------
        df_objetivos = extraer_objetivos(RUTA_OBJ)
        # ---------------Objetivos-Vigilantes---------------
        df_obj_vig = extraer_obj_vig(RUTA_OBJ_VIG)
        # ---------------Salida---------------
        df_salida = extraer_salida(RUTA_SALIDA)
        
        # ==================== Transform ====================
        logging.info('Transformando los datos...')
        # ---------------vigilantes---------------
        df_vig_limpio = limpiar_vig(df_vigilantes)
        # ---------------Empresas seguridad---------------
        df_emp_seg_limpio = limpiar_emp_seg(df_emp_seg)
        # ---------------Objetivos---------------
        df_obj_limpio = limpiar_objetivos(df_objetivos)
        # ---------------Objetivos-Vigilantes---------------
        df_obj_vig_limpio = limpiar_obj_vig(df_obj_vig)
        # ---------------Salida---------------
        df_salida_limpio = limpiar_salida(df_salida)
        
        # ==================== Load ====================
        logging.info('Definiendo las tablas de la base de datos...')
        # Crear las tablas de base de datos
        df_emp_bd = crear_tabla_empresa_bd(df_emp_seg_limpio)
        df_obj_bd = crear_tabla_obj_bd(df_obj_limpio, df_emp_bd)
        df_vig_bd = crear_tabla_vig_db(df_vig_limpio, df_emp_bd)
        df_obj_vig_db = crear_tabla_obj_vig_db(df_obj_vig_limpio,df_obj_bd,df_vig_bd)
        df_salida_db = crear_tabla_salida(df_salida_limpio, df_emp_bd)
        
        # renombrar las columnas de las diferentes tablas
        renombrar_columnas(df_emp_bd, df_vig_bd, df_obj_bd, df_salida_db)
        
        # Definir las claves primarias
        convertir_pk(df_emp_bd, df_vig_bd, df_obj_bd, df_obj_vig_db, df_salida_db)
        
        logging.info('Cargando a la base de datos...')
        
        # borrar relaciones antiguas 
        eliminar_claves_foraneas_viejas(config)
            
        # cargar datos
        cargar_a_db(df_emp_bd, 'empresa', 'id_empresa', config)
        cargar_a_db(df_obj_bd, 'objetivo', 'id_objetivo', config)
        cargar_a_db(df_vig_bd, 'vigilante', 'dni', config)
        cargar_a_db(df_obj_vig_db, 'objetivo_vigilante', 'id', config)
        cargar_a_db(df_salida_db, 'salida', 'id_salida', config)
        aplicar_claves_foraneas(config)
        
        logging.info("✅ ETL completado exitosamente")
        
    
    except Exception as e:
        logging.error(f'❌ Error en el ETL: {str(e)}')
        raise


if __name__ == '__main__':
    ejecutar_pipeline()
    
    
# -----------------------------------------
# vigilantes
# df_vigilantes = extraer_vigilantes(ruta)

# print(df_vigilantes.head())

# informacion = informe_vig(df_vigilantes)

# print(informacion)


# df_vig_limpio = limpiar_vig(df_vigilantes)
# print(df_vig_limpio.head(200))

# print(informe_vig(df_vig_limpio))

# print(df_vig_limpio['fecha_tramite'].count())
# print(df_vig_limpio['ftramite'].unique())

# --------------------------—------------------
# Empresas seguridad
# df_emp_seg = extraer_emp_seg(ruta_emp_seg)
# print(df_emp_seg)

# info_emp = df_emp_seg.info()

# df_emp_seg_limpio = limpiar_emp_seg(df_emp_seg)

# print(df_emp_seg_limpio)

# print(df_emp_seg_limpio.info())



# --------------------------—------------------
# Objetivos
# df_objetivos = extraer_objetivos(ruta_obj)
# print(df_objetivos)

# print(df_objetivos.info())

# df_obj_limpio = limpiar_objetivos(df_objetivos)
# print(df_obj_limpio)
# print(df_obj_limpio.info())

# --------------------------—------------------
# Objetivos-Vigilantes
# df_obj_vig = extraer_obj_vig(ruta_obj_vig)
# df_obj_vig_limpio = limpiar_obj_vig(df_obj_vig)
# print(df_obj_vig_limpio)
# print(df_obj_vig_limpio.info())

# --------------------------—------------------
# Salida
# df_salida = extraer_salida(ruta_salida)
# df_salida_limpio = limpiar_salida(df_salida)
# print(df_salida_limpio.info())


# ---------------------------------------------
# Crear las tablas de base de datos
# df_emp_bd = crear_tabla_empresa_bd(df_emp_seg_limpio)
# # print(df_emp_bd)
# # print(df_emp_bd.info())

# df_obj_bd = crear_tabla_obj_bd(df_obj_limpio, df_emp_bd)
# # print(df_obj_bd)
# # print(df_obj_bd.info())

# df_vig_bd = crear_tabla_vig_db(df_vig_limpio, df_emp_bd)
# # print(df_vig_bd)
# # print(df_vig_bd.info())

# df_obj_vig_db = crear_tabla_obj_vig_db(df_obj_vig_limpio,df_obj_bd,df_vig_bd)
# # print(df_obj_vig_db)
# # print(df_obj_vig_db.info())

# df_salida_db = crear_tabla_salida(df_salida_limpio, df_emp_bd)
# # print(df_salida_db)
# # print(df_salida_db.info())

# --------------------------—------------------
# renombrar_columnas(df_emp_bd, df_vig_bd, df_obj_bd, df_salida_db)
# # print(df_emp_bd)
# convertir_dni(df_vig_bd, df_obj_vig_db)
# # print(df_emp_bd.info())
# # print(df_vig_bd.info())
# # print(df_obj_bd.info())
# # print(df_obj_vig_db.info())
# # print(df_salida_db.info())

# # --------------------------—------------------
# convertir_pk(df_emp_bd, df_vig_bd, df_obj_bd, df_obj_vig_db, df_salida_db)
# # print(df_emp_bd)
# # print(df_vig_bd)
# # print(df_obj_bd)
# # print(df_obj_vig_db)
# # print(df_salida_db)


# with open('config.yaml') as f:
#     config = yaml.safe_load(f)
    
# try:
#     # borrar relaciones antiguas 
#     eliminar_claves_foraneas_viejas(config)
    
#     # cargar datos
#     cargar_a_db(df_emp_bd, 'empresa', 'id_empresa', config)
#     cargar_a_db(df_obj_bd, 'objetivo', 'id_objetivo', config)
#     cargar_a_db(df_vig_bd, 'vigilante', 'dni', config)
#     cargar_a_db(df_obj_vig_db, 'objetivo_vigilante', 'id', config)
#     cargar_a_db(df_salida_db, 'salida', 'id_salida', config)
#     print('exito!!')
    
#     aplicar_claves_foraneas(config)
    
# except Exception as e:
#     raise

