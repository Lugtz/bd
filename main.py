from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
import schemas
from pydantic import BaseModel

# 1. Crea las tablas en Somee si no existen
models.Base.metadata.create_all(bind=engine)

# 2. Inicializa la aplicación (¡Esto es lo que faltaba en la línea 3!)
app = FastAPI(
    title="API Clínica - Parcial III (Con IA)",
    description="Backend conectado a SQL Server en Somee con módulo predictivo"
)

# 3. Permisos para que Angular se pueda conectar (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Conexión a la Base de Datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- MODELO RÁPIDO PARA CITAS ---
class CitaRecepcion(BaseModel):
    id_medico: int
    id_paciente_firebase: str
    fecha_hora: str
    motivo: str
    diagnostico: str
    estado: str

# ==========================================
#              ENDPOINTS (RUTAS)
# ==========================================

@app.get("/")
def prueba_conexion():
    return {"mensaje": "¡Hola! Tu API REST está viva y conectada 🚀", "estado": 200}

# --- MÉDICOS ---
@app.post("/medicos/", response_model=schemas.MedicoResponse)
def crear_medico(medico: schemas.MedicoCreate, db: Session = Depends(get_db)):
    nuevo_medico = models.Medico(**medico.model_dump())
    db.add(nuevo_medico)
    db.commit()
    db.refresh(nuevo_medico)
    return nuevo_medico

@app.get("/medicos/", response_model=list[schemas.MedicoResponse])
def obtener_medicos(db: Session = Depends(get_db)):
    medicos = db.query(models.Medico).all()
    return medicos

# --- CITAS (Requisito de la tarea) ---
@app.post("/citas/")
def crear_cita(cita: CitaRecepcion, db: Session = Depends(get_db)):
    # Guardamos la cita en Somee
    nueva_cita = models.Cita(**cita.model_dump())
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita

@app.get("/citas/")
def obtener_citas(db: Session = Depends(get_db)):
    # Esto va a Somee, lee la tabla Citas y devuelve toda la lista
    citas = db.query(models.Cita).all()
    return citas
# --- INTELIGENCIA ARTIFICIAL 
@app.get("/ia/prediccion-personal/")
def predecir_personal(
    virus: str = Query(..., description="Texto del diagnóstico"),
    pacientes_actuales: int = Query(..., description="Cantidad de pacientes"),
    db: Session = Depends(get_db)
):
    texto = virus.lower()
    
    # NLP Básico Mejorado: Diccionario de palabras clave por gravedad
    urgencia_roja = ["covid", "infarto", "dengue", "hemorragia", "pecho", "inconsciente", "grave"]
    urgencia_amarilla = ["fiebre", "fractura", "dolor agudo", "corte", "infección", "influenza"]
    
    # Valores por defecto (Caso Verde)
    riesgo = "BAJO (Verde)"
    medicos_necesarios = 1
    mensaje = "Paciente de rutina. Personal actual en clínica es suficiente."

    # Lógica de clasificación (Triage)
    if any(palabra in texto for palabra in urgencia_roja):
        riesgo = "ALTO (Rojo)"
        medicos_necesarios = 3
        mensaje = "⚠️ EMERGENCIA: Requiere atención inmediata y posible aislamiento."
    elif any(palabra in texto for palabra in urgencia_amarilla):
        riesgo = "MEDIO (Amarillo)"
        medicos_necesarios = 2
        mensaje = "⚡ URGENCIA: Pasar a valoración en los próximos 30 minutos."

    # Contamos cuántos médicos hay realmente en Somee
    medicos_actuales = db.query(models.Medico).count()
    deficit = max(0, medicos_necesarios - medicos_actuales)
    
    # Si la IA detecta que faltan doctores para la emergencia, lo advierte
    if deficit > 0:
        mensaje += f" ALERTA ADMINISTRATIVA: Faltan {deficit} médicos en turno para cubrir la demanda."

    return {
        "analisis_ia": {
            "riesgo_epidemia": riesgo,
            "diagnostico_analizado": virus
        },
        "recomendacion": {
            "medicos_sugeridos": medicos_necesarios,
            "medicos_en_nomina": medicos_actuales,
            "mensaje": mensaje
        }
    }