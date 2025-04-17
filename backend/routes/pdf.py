from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import PDF
import shutil
import os
import uuid
import io
from PyPDF2 import PdfReader  # ✅ Import for text extraction

router = APIRouter(prefix="/pdf", tags=["PDF Handling"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Handles PDF file uploads and extracts text."""
    print("📥 Received Upload Request")

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    print(f"📄 File Name: {file.filename}")
    print(f"📄 Content Type: {file.content_type}")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_location = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        # Save the file to disk
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ Saved PDF as: {unique_filename}")

        # ✅ Extract text from PDF
        file.file.seek(0)  # Reset file pointer for reading
        pdf_reader = PdfReader(io.BytesIO(file.file.read()))
        extracted_text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])

        if not extracted_text.strip():
            extracted_text = "No text extracted (possibly a scanned PDF)"

        print("🔹 Extracted Text Preview:", extracted_text[:500])  # Print first 500 chars

    except Exception as e:
        print(f"🚨 Error Processing File: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

    # ✅ Save PDF info and extracted text in the database
    db_pdf = PDF(filename=unique_filename, user_id=1, text=extracted_text)  # ✅ Store text
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)

    print(f"✅ PDF Stored in DB with ID: {db_pdf.id}")

    return {
        "filename": unique_filename,
        "message": "PDF uploaded successfully",
        "pdf_id": db_pdf.id,
        "text_preview": extracted_text[:300]  # Show first 300 characters
    }
