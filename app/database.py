from pathlib import Path

import yaml
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Leer la configuración desde config.yaml
CONFIG_PATH = Path(__file__).resolve().parent.parent / 'config.yaml'

with open(CONFIG_PATH, encoding='utf-8') as f:
    _cfg = yaml.safe_load(f)['db']

DATABASE_URL = URL.create(
    drivername= 'mysql+pymysql',
    username= _cfg['usuario'],
    password= _cfg['password'],
    host=_cfg['host'],
    port=int(_cfg['puerto']),
    database=_cfg['nombre'],
)

# 2. Creación del motor y sesión de SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Modelo de la tabla de Usuarios
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

# 4. Crear las tablas si no existen
def inicializar_base_datos():
    Base.metadata.create_all(bind=engine)


