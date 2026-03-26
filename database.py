from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Tus credenciales de Somee.com (Se quedan intactas)
SERVER = 'universidad_prueba.mssql.somee.com'
USERNAME = 'Lugtz_SQLLogin_1'
PASSWORD = 'njob52wdme' 
DATABASE = 'universidad_prueba'   

# 2. La nueva cadena de conexión (Usando pymssql para que no truene en Linux)
SQLALCHEMY_DATABASE_URL = f"mssql+pymssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"

# 3. Encendemos el motor
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print(":P Conexión preparada para SQL Server en Somee (Compatible con Render/Linux)")
except Exception as e:
    print(f" Error al configurar la conexión: {e}")