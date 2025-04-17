from pydantic import BaseModel, EmailStr,conint
from typing import Optional
from rouge_score import rouge_scorer

# ✅ User Registration Schema
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # No constraints since FastAPI handles hashing

# ✅ User Response Schema (Excludes Password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # Allows ORM conversion

# ✅ Login Request Schema (Fixes ImportError)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ✅ PDF Upload Schema
class PDFUpload(BaseModel):
    filename: str
    user_id: int  # Foreign key reference to Users table

class PDFResponse(BaseModel):
    id: int
    filename: str
    user_id: int

    class Config:
        from_attributes = True

# ✅ PDF Create Schema
class PDFCreate(BaseModel):
    user_id: int
    filename: str

# ✅ Summarization Schema
class SummaryCreate(BaseModel):
    pdf_id: int
    summary_text: str

class SummaryResponse(BaseModel):
    id: int
    pdf_id: int
    summary_text: str
    rouge_scores: dict 
    class Config:
        from_attributes = True

# ✅ Feedback Schema (Linked to User)
class FeedbackCreate(BaseModel):
    user_id: int  # Directly linked to the logged-in user
    rating: conint(ge=1, le=5)  # Ensures rating is between 1-5
    comment: str

class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    rating: int
    comment: str

    class Config:
        orm_mode = True  # Ensures ORM compatibility

class SummaryRequest(BaseModel):
    pdf_id: int
    user_id: int
    model: str  # Model selection (e.g., "bart-large")

