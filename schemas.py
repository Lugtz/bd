from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Esquemas para Médico ---
class MedicoBase(BaseModel):
    nombre: str
    apellidos: str
    especialidad: str
    cedula: str
    telefono: Optional[str] = None

class MedicoCreate(MedicoBase):
    pass # Se usa cuando Angular nos manda datos para CREAR un médico

class MedicoResponse(MedicoBase):
    id_medico: int

    class Config:
        from_attributes = True # Permite que Pydantic lea los modelos de SQLAlchemy

# --- Esquemas para Cita ---
class CitaBase(BaseModel):
    id_medico: int
    id_paciente_firebase: str
    fecha_hora: datetime
    motivo: str
    estado: Optional[str] = 'Pendiente'
    diagnostico: Optional[str] = None

class CitaCreate(CitaBase):
    pass

class CitaResponse(CitaBase):
    id_cita: int

    class Config:
        from_attributes = True
        