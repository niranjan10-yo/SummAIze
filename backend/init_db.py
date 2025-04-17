from database import engine, Base
from models import User, PDF, Summarization, Feedback  # No need to import Base again
from sqlalchemy import inspect

def create_tables():
    """Creates all tables in the database."""
    try:
        Base.metadata.create_all(bind=engine)
        print("\n✅ Database tables created successfully!\n")
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}\n")

def verify_tables():
    """Verifies if tables exist in the database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            print(f"📋 Tables in the database: {tables}\n")
        else:
            print("\n⚠️ No tables found in the database.\n")
    except Exception as e:
        print(f"\n❌ Error verifying tables: {e}\n")

if __name__ == "__main__":
    create_tables()
    verify_tables()
