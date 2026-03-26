from pydantic import BaseModel

class MedicoResponse(BaseModel):
    id_medico: int
    nombre: str
    apellidos: str
    especialidad: str
    class Config:
        from_attributes = True

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