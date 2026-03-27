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

@app.post("/citas/")
def crear_cita(cita: CitaRecepcion, db: Session = Depends(get_db)):
    # SQL Server recibirá exactamente lo que pide
    nueva_cita = models.Cita(**cita.model_dump())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita

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