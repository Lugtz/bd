from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas, joblib

# Intentar sincronizar tablas con Somee
try:
    models.Base.metadata.create_all(bind=engine)
except:
    pass

app = FastAPI()

# CONFIGURACIÓN DE CORS (Esto quita las letras rojas de Chrome)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carga de IA
try:
    modelo_ia = joblib.load("modelo_triage.pkl")
    print("✅ IA Lista")
except:
    modelo_ia = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- RUTAS CORREGIDAS (Con slash final para evitar el 405) ---

@app.get("/medicos/", response_model=list[schemas.MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(models.Medico).all()

@app.get("/citas/", response_model=list[schemas.CitaResponse])
def listar_citas(db: Session = Depends(get_db)):
    return db.query(models.Cita).all()

@app.post("/citas/", response_model=schemas.CitaResponse)
def registrar_cita(cita: schemas.CitaCreate, db: Session = Depends(get_db)):
    nueva_cita = models.Cita(**cita.model_dump())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita

@app.get("/ia/analizar-sintomas/")
def analizar(motivo: str = Query(...)):
    if not modelo_ia: raise HTTPException(status_code=500, detail="IA Offline")
    res = modelo_ia.predict([motivo.lower()])[0]
    esp, ries = res.split("|")
    return {"prediccion": {"especialidad_sugerida": esp, "urgencia": ries}}