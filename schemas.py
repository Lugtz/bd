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
    pass 

class MedicoResponse(MedicoBase):
    id_medico: int

    class Config:
        from_attributes = True 

# --- Esquemas para Cita ---
class CitaBase(BaseModel):
    id_medico: int
    id_paciente_firebase: str
    fecha_hora: datetime
    motivo: str
    estado: Optional[str] = 'Pendiente'

class CitaCreate(CitaBase):
    # Añadimos estos campos como opcionales para que 
    # la API pueda llenarlos con los resultados de la IA
    diagnostico_ia: Optional[str] = None
    nivel_urgencia: Optional[str] = None

class CitaResponse(CitaBase):
    id_cita: int
    diagnostico_ia: Optional[str] = None
    nivel_urgencia: Optional[str] = None

    class Config:
        from_attributes = True