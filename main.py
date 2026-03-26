from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas, joblib

# Crear tablas en Somee
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Clínica Inteligente")

# Configuración de CORS
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
except Exception as e:
    print(f"❌ Error al cargar modelo: {e}")
    modelo_ia = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---

@app.get("/ia/analizar-sintomas/")
def analizar_sintomas(motivo: str = Query(...)):
    if not modelo_ia: raise HTTPException(status_code=500, detail="IA Offline")
    resultado = modelo_ia.predict([motivo.lower().strip()])[0]
    esp, ries = resultado.split("|")
    return {"prediccion": {"especialidad_sugerida": esp, "urgencia": ries}}

@app.get("/medicos/", response_model=list[schemas.MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(models.Medico).all()

@app.post("/citas/", response_model=schemas.CitaResponse)
def registrar_cita(cita: schemas.CitaCreate, db: Session = Depends(get_db)):
    nueva_cita = models.Cita(**cita.model_dump())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita