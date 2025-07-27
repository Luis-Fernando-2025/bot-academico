import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Usuario, Examen
from add_user import registrar_usuario_db

@pytest.fixture
def db_session():
    # Crea una base de datos temporal en memoria con SQLAlchemy
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    yield session
    session.close()

def test_registrar_usuario(db_session):
    usuario = registrar_usuario_db(
        db_session,
        telefono="+51987654321",
        timezone="America/Lima",
        examenes=[{"curso": "Macroeconomía", "fecha": "2025-08-10"}]
    )
    # Verificamos que el usuario se haya creado correctamente
    assert usuario.id is not None
    assert usuario.telefono == "whatsapp:+51987654321"
    assert len(usuario.examenes) == 1
    assert usuario.examenes[0].curso == "Macroeconomía"
