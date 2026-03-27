from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# Modelo para la tabla Medicos
class Medico(Base):
    __tablename__ = "Medicos"

    id_medico = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    especialidad = Column(String(80), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    telefono = Column(String(15))

    # Relación bidireccional (opcional pero muy útil)
    citas = relationship("Cita", back_populates="medico")

# Modelo para la tabla Citas
class Cita(Base):
    __tablename__ = "Citas"

    id_cita = Column(Integer, primary_key=True, index=True)
    id_medico = Column(Integer, ForeignKey("Medicos.id_medico", ondelete="CASCADE"), nullable=False)
    id_paciente_firebase = Column(String(100), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=False)
    estado = Column(String(20), default='Pendiente')
    estado = Column(String(50))  
    diagnostico = Column(String(500))

    medico = relationship("Medico", back_populates="citas")
    diagnostico = Column(String(500), nullable=True)