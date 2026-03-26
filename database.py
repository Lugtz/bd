from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Credenciales de Somee
SERVER = 'universidad_prueba.mssql.somee.com'
USERNAME = 'Lugtz_SQLLogin_1'
PASSWORD = 'njob52wdme' 
DATABASE = 'universidad_prueba' 

SQLALCHEMY_DATABASE_URL = f"mssql+pymssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"

# pool_pre_ping asegura que la conexión no se muera por inactividad
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()