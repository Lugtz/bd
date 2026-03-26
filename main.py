from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import schemas
import joblib
import re
import unicodedata

# 1. Creación de tablas en Somee
models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="API Clínica Inteligente - Triage ML",
    description="Sistema experto con Machine Learning y SQL Server Relacional"
)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Carga del Modelo de IA
try:
    modelo_ia = joblib.load("modelo_triage.pkl")
    print("✅ Inteligencia Artificial cargada y lista.")
except Exception as e:
    print(f"❌ Error al cargar el modelo .pkl: {e}")
    modelo_ia = None

# 4. Normalización de Texto (NLP)
def limpiar_texto(texto):
    if not isinstance(texto, str): return ""
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^a-z\s]', '', texto)
    return re.sub(r'\s+', ' ', texto).strip()

# 5. Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ORIGINALES ---

@app.get("/")
def estado_api():
    return {
        "mensaje": "API Clínica Viva 🚀",
        "ia_status": "Online" if modelo_ia else "Offline"
    }

@app.get("/ia/analizar-sintomas/")
def analizar_sintomas(motivo: str = Query(..., description="Síntomas del paciente"), db: Session = Depends(get_db)):
    if not modelo_ia:
        raise HTTPException(status_code=500, detail="Modelo de IA no cargado.")

    texto_procesado = limpiar_texto(motivo)
    resultado = modelo_ia.predict([texto_procesado])[0]
    especialidad, riesgo = resultado.split("|")

    especialistas = db.query(models.Medico).filter(
        models.Medico.especialidad == especialidad
    ).all()

    return {
        "prediccion": {
            "especialidad_sugerida": especialidad,
            "urgencia": riesgo
        },
        "disponibilidad": {
            "total_medicos": len(especialistas),
            "medicos": [f"{m.nombre} {m.apellidos}" for m in especialistas]
        },
        "fuente": "Criterios Oficiales OMS / Manchester Triage"
    }

@app.post("/medicos/", response_model=schemas.MedicoResponse)
def crear_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    nuevo_medico = models.Medico(**medico.model_dump())
    db.add(nuevo_medico)
    db.commit()
    db.refresh(nuevo_medico)
    return nuevo_medico

@app.get("/medicos/", response_model=list[schemas.MedicoResponse])
def listar_medicos(db: Session = Depends(get_db)):
    return db.query(models.Medico).all()

@app.get("/medicos/{id_medico}", response_model=schemas.MedicoResponse)
def obtener_medico_por_id(id_medico: int, db: Session = Depends(get_db)):
    medico = db.query(models.Medico).filter(models.Medico.id_medico == id_medico).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado")
    return medico

@app.post("/citas/", response_model=schemas.CitaResponse)
def registrar_cita(cita: schemas.CitaCreate, db: Session = Depends(get_db)):
    nueva_cita = models.Cita(**cita.model_dump())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita

@app.get("/citas/", response_model=list[schemas.CitaResponse])
def listar_citas(db: Session = Depends(get_db)):
    return db.query(models.Cita).all()

@app.get("/citas/paciente/{id_firebase}", response_model=list[schemas.CitaResponse])
def obtener_citas_paciente(id_firebase: str, db: Session = Depends(get_db)):
    return db.query(models.Cita).filter(models.Cita.id_paciente_firebase == id_firebase).all()

@app.get("/citas/especialidad/{especialidad}")
def obtener_citas_por_especialidad(especialidad: str, db: Session = Depends(get_db)):
    return db.query(models.Cita).join(models.Medico).filter(
        models.Medico.especialidad == especialidad
    ).all()