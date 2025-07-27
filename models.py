from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

# Tabla de Usuarios (cada estudiante es un usuario)
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    telefono = Column(String(20), unique=True, nullable=False)
    avisos_globales = Column(String(50), default="30,20,10,5")  # Valores por defecto
    usar_globales = Column(Boolean, default=True)
    timezone = Column(String(50), default="America/Lima")  # <- Nueva columna para zona horaria

    examenes = relationship("Examen", back_populates="usuario", cascade="all, delete-orphan")

# Tabla de Exámenes (cada examen pertenece a un usuario)
class Examen(Base):
    __tablename__ = "examenes"

    id = Column(Integer, primary_key=True)
    curso = Column(String(100), nullable=False)
    fecha = Column(String(10), nullable=False)  # formato YYYY-MM-DD
    avisos = Column(String(50), default="")  # valores personalizados

    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="examenes")

# Configuración de la base de datos
DATABASE_URL = "sqlite:///data.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    print("Creando tablas en data.db...")
    init_db()
    print("¡Listo! Base de datos inicializada.")
