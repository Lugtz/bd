from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, SessionLocal
import models
import schemas
import joblib

# 1. Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 2. CORS para Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Carga del Modelo IA Real (.pkl)
try:
    modelo_ia = joblib.load("modelo_triage.pkl")
    print("✅ IA Cargada Exitosamente")
except Exception as e:
    print(f"❌ Error IA: {e}")
    modelo_ia = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. EL PUENTE ORIGINAL PARA GUARDAR CITAS (¡Esto lo arregla todo!)
class CitaRecepcion(BaseModel):
    id_medico: int
    id_paciente_firebase: str
    fecha_hora: str
    motivo: str
    diagnostico: str
    estado: str

# ==========================================
# ENDPOINTS
# ==========================================

from fastapi import HTTPException # Asegúrate de tener esto arriba en tus imports

@app.post("/citas/")
def crear_cita(cita: CitaRecepcion, db: Session = Depends(get_db)):
    try:
        # 1. Le quitamos la 'T' y la 'Z' a la fecha para que SQL Server no llore
        fecha_limpia = cita.fecha_hora.replace("T", " ")[:19] 

        # 2. Armamos el objeto manualmente para evitar errores de Pydantic
        nueva_cita = models.Cita(
            id_medico=cita.id_medico,
            id_paciente_firebase=cita.id_paciente_firebase,
            fecha_hora=fecha_limpia,
            motivo=cita.motivo,
            diagnostico=cita.diagnostico,
            estado=cita.estado
        )
        
        # 3. Guardamos
        db.add(nueva_cita)
        db.commit()
        db.refresh(nueva_cita)
        return nueva_cita
        
    except Exception as e:
        # 4. SI SQL SERVER RECHAZA ALGO, ESTO EVITA QUE PYTHON MUERA Y CAUSE CORS
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error Real de SQL: {str(e)}")
@app.get("/citas/")
def obtener_citas(db: Session = Depends(get_db)):
    return db.query(models.Cita).all()

@app.get("/medicos/")
def obtener_medicos(db: Session = Depends(get_db)):
    return db.query(models.Medico).all()

@app.get("/ia/analizar-sintomas/")
def analizar_sintomas(motivo: str = Query(...)):
    if not modelo_ia: raise HTTPException(status_code=500, detail="IA Offline")
    res = modelo_ia.predict([motivo.lower()])[0]
    esp, ries = res.split("|")
    return {"prediccion": {"especialidad_sugerida": esp, "urgencia": ries}}