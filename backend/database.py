from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./SummAIze.db"  # Ensure the correct database path

# ✅ Create Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ✅ Create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base Class for Models
Base = declarative_base()

# ✅ Dependency for database session
def get_db():
    """Yields a new database session and ensures it is closed properly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
