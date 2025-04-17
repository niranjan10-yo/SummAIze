from sqlalchemy.orm import Session
from models import User, PDF, Summarization, Feedback
from schemas import UserCreate, PDFCreate, SummarizationCreate, FeedbackCreate  # You'll need schemas
from security import get_password_hash  # Hashing for passwords

# ✅ Create a new user
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ✅ Get user by username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# ✅ Get user by ID
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# ✅ Create PDF entry
def create_pdf(db: Session, pdf: PDFCreate, user_id: int):
    db_pdf = PDF(user_id=user_id,

# ✅ Create feedback entry
def create_feedback(db: Session, feedback: FeedbackCreate):
    db_feedback = Feedback(
        user_id=feedback.user_id,
        rating=feedback.rating,
        comment=feedback.comment  # 🚨 Ensure this field exists in models.py & schemas.py
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
