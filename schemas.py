from pydantic import BaseModel

# Esquemas para MÉDICOS
class MedicoBase(BaseModel):
    nombre: str
    apellidos: str
    especialidad: str
    cedula: str
    telefono: str

class MedicoCreate(MedicoBase):
    pass

class MedicoResponse(MedicoBase):
    id_medico: int
    class Config:
        from_attributes = True

# Esquemas para CITAS
class CitaCreate(BaseModel):
    id_medico: int
    id_paciente_firebase: str
    fecha_hora: str
    motivo: str
    diagnostico_ia: str
    nivel_urgencia: str

class CitaResponse(CitaCreate):
    id_cita: int
    class Config:
        from_attributes = True