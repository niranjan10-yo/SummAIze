from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from database import get_db

router = APIRouter(prefix="/tables", tags=["Database"])  # ✅ Add prefix here

@router.get("",summary="GET TABLES")
def get_tables(db: Session = Depends(get_db)):
    """Fetches all table names from the database."""
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        if not tables:
            raise HTTPException(status_code=404, detail="No tables found in the database.")
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tables: {str(e)}")
