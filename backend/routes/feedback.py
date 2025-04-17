from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, conint
from sqlalchemy.orm import Session
from database import get_db
from models import Feedback
from typing import Optional

#router = APIRouter()
router = APIRouter(prefix="/feedback")

class FeedbackRequest(BaseModel):
    user_id: int
    rating: conint(ge=1, le=5)
    comment: str
@router.post("/submit")
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        print("Received feedback request:", feedback.dict())  # Debugging
        new_feedback = Feedback(
            user_id=feedback.user_id,
            rating=feedback.rating,
            comment=feedback.comment
        )
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        print("Feedback saved successfully:", new_feedback)  # Debugging
        return {"message": "Feedback submitted successfully", "feedback_id": new_feedback.id}
    except Exception as e:
        db.rollback()
        print(f"🚨 Error inserting feedback: {e}")  # Debugging output
        raise HTTPException(status_code=500, detail=str(e))
