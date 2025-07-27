import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Usuario, Examen
from add_user import registrar_usuario_db

@pytest.fixture
def db_session():
    # Crear una base de datos temporal en memoria
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    yield session
    session.close()

def test_registrar_varios_examenes(db_session):
    usuario = registrar_usuario_db(
        db_session,
        telefono="+51987654321",
        timezone="America/Lima",
        examenes=[
            {"curso": "Macroeconomía", "fecha": "2025-08-10"},
            {"curso": "Microeconomía", "fecha": "2025-08-15"}
        ]
    )
    assert len(usuario.examenes) == 2
    cursos = [ex.curso for ex in usuario.examenes]
    assert "Macroeconomía" in cursos
    assert "Microeconomía" in cursos

def test_evitar_duplicados_telefono(db_session):
    # Registrar usuario por primera vez
    usuario1 = registrar_usuario_db(
        db_session,
        telefono="+51987654321",
        timezone="America/Lima",
        examenes=[{"curso": "Contabilidad", "fecha": "2025-09-01"}]
    )

    # Registrar el mismo número otra vez (debería añadir exámenes al mismo usuario)
    usuario2 = registrar_usuario_db(
        db_session,
        telefono="+51987654321",
        timezone="America/Lima",
        examenes=[{"curso": "Finanzas", "fecha": "2025-09-10"}]
    )

    # Verificamos que solo haya un usuario en la base de datos
    usuarios_total = db_session.query(Usuario).all()
    assert len(usuarios_total) == 1
    assert len(usuarios_total[0].examenes) == 2
