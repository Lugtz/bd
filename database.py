from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Credenciales (Verificadas)
SERVER = 'universidad_prueba.mssql.somee.com'
USERNAME = 'Lugtz_SQLLogin_1'
PASSWORD = 'njob52wdme' 
DATABASE = 'universidad_prueba' 

# URL con pymssql (Obligatorio para Render/Linux)
SQLALCHEMY_DATABASE_URL = f"mssql+pymssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True, 
    connect_args={'timeout': 30} 
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()