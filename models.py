from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Medico(Base):
    __tablename__ = "medicos"
    id_medico = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    especialidad = Column(String(50), nullable=False, index=True) # IMPORTANTE para la IA
    cedula = Column(String(50))
    telefono = Column(String(20))
    
    # Relación: Un médico tiene muchas citas
    citas = relationship("Cita", back_populates="medico")

class Cita(Base):
    __tablename__ = "citas"
    id_cita = Column(Integer, primary_key=True, index=True)
    id_medico = Column(Integer, ForeignKey("medicos.id_medico"))
    id_paciente_firebase = Column(String(100), nullable=False)
    fecha_hora = Column(String(50))
    motivo = Column(String(500))
    diagnostico_ia = Column(String(100)) # Aquí guardamos lo que predice el .pkl
    nivel_urgencia = Column(String(50))  # Ej: "ALTO (Rojo)"
    estado = Column(String(20), default="Pendiente")

    # Relación: La cita pertenece a un médico
    medico = relationship("Medico", back_populates="citas")