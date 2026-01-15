# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import get_db_url

# URL de la base de datos
SQLALCHEMY_DATABASE_URL = get_db_url()

# Crear el motor de SQLAlchemy
# pool_pre_ping=True ayuda a manejar conexiones perdidas
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_pre_ping=True
)

# Crear una clase SessionLocal para cada solicitud
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos declarativos
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("Intentando conectar a la base de datos...")
    try:
        # Intento de conexión para verificar la URL
        with engine.connect() as connection:
            print("Conexión exitosa (simulada por la creación del motor).")
    except Exception as e:
        print(f"Error al conectar: {e}")
