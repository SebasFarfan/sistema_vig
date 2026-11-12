from sqlalchemy import create_engine, text
from sqlalchemy.types import VARCHAR


# Relaciones entre las diferentes tablas 
RELACIONES_DB = [
    ("vigilante", "id_empresa", "empresa", "id_empresa"),
    ("objetivo", "id_empresa", "empresa", "id_empresa"),
    ("objetivo_vigilante", "id_objetivo", "objetivo", "id_objetivo"),
    ("objetivo_vigilante", "dni_vigilante", "vigilante", "dni"), 
    ("salida", "id_empresa", "empresa", "id_empresa")
]

# remover las claves foraneas en caso de volver a crear las relaciones
def eliminar_claves_foraneas_viejas(config):
    usuario = config['db']['usuario']
    password = config['db']['password']
    host = config['db']['host']
    puerto = config['db']['puerto']
    nombre_db = config['db']['nombre']
    
    engine = create_engine(f'mysql+pymysql://{usuario}:{password}@{host}:{puerto}/{nombre_db}')
    
    print("🧹 Removiendo claves foráneas antiguas para preparar la carga...")
    with engine.connect() as connection:
        with connection.begin():
            for tabla_origen, col_origen, tabla_destino, col_destino in RELACIONES_DB:
                constraint_name = f"fk_{tabla_origen}_{col_origen}_{tabla_destino}"
                try:
                    # Intentamos borrar la restricción si existe en MySQL
                    connection.execute(text(f"ALTER TABLE {tabla_origen} DROP FOREIGN KEY {constraint_name};"))
                except Exception:
                    pass # Si es la primera corrida o la tabla no existe, ignora el error limpiamente

# Cargar a base de datos 
def cargar_a_db(df, nombre_tabla, pk, config):
    
    # sentencia sql para agregar la clave primaria
    sentencia_sql_pk = f'ALTER TABLE {nombre_tabla} ADD PRIMARY KEY ({pk});'
    
    # leer configuracion de conexion
    usuario = config['db']['usuario']
    password = config['db']['password']
    host = config['db']['host']
    puerto = config['db']['puerto']
    nombre_db = config['db']['nombre']
    
    # Crear motor de conexion
    engine = create_engine(f'mysql+pymysql://{usuario}:{password}@{host}:{puerto}/{nombre_db}')
    
     #  Forzar que la clave primaria sea VARCHAR si es un texto
    data_types = {}
    if df.index.dtype == 'object' or df.index.dtype == 'string':
        data_types[pk] = VARCHAR(50)  # Esto fuerza a MySQL a estructurarlo como VARCHAR desde el inicio
    
    # Verificar si hay columnas de texto en el DataFrame (ej: 'dni_vigilante' en la tabla intermedia)
    for columna in df.columns:
        if df[columna].dtype == 'object' or df[columna].dtype == 'string':
            # Si la columna contiene la palabra 'dni' o 'id', la forzamos a VARCHAR(50)
            if 'dni' in columna.lower() or 'id' in columna.lower():
                data_types[columna] = VARCHAR(50)
 
    # Cargar datos (if_exitst='replace' para carga completa)
    df.to_sql(nombre_tabla, engine, if_exists='replace', index=True, index_label=pk,dtype=data_types)
    print(f"✅ Tabla '{nombre_tabla}' cargada exitosamente: {len(df)} registros.")
    
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(sentencia_sql_pk))
        print(f'Clave primaria {pk} configurada exitosamente')
    except Exception as e:
        print(f'Error al establecer clave primaria')
        raise
    

# define las claves foraneas a las tablas
def aplicar_claves_foraneas(config):
    usuario = config['db']['usuario']
    password = config['db']['password']
    host = config['db']['host']
    puerto = config['db']['puerto']
    nombre_db = config['db']['nombre']
    
    engine = create_engine(f'mysql+pymysql://{usuario}:{password}@{host}:{puerto}/{nombre_db}')
        
    print("\n🔗 Configurando claves foráneas en la base de datos...")
    
    with engine.connect() as connection:
        with connection.begin():
            for tabla_origen, col_origen, tabla_destino, col_destino in RELACIONES_DB:
                constraint_name = f"fk_{tabla_origen}_{col_origen}_{tabla_destino}"
                
                sql = f"""
                ALTER TABLE {tabla_origen} 
                ADD CONSTRAINT {constraint_name} 
                FOREIGN KEY ({col_origen}) REFERENCES {tabla_destino}({col_destino});
                """
                connection.execute(text(sql))
                print(f"✅ Relación establecida: {tabla_origen}({col_origen}) ➡️ {tabla_destino}({col_destino})")
                
    print("🎉 ¡Todas las claves foráneas fueron configuradas con éxito!")
