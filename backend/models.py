from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

# ✅ Users Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)  # ✅ Added Email
    password = Column(String, nullable=False)

    # ✅ Relationships
    pdfs = relationship("PDF", back_populates="user", passive_deletes=True)
    summaries = relationship("Summarization", back_populates="user", passive_deletes=True)
    feedbacks = relationship("Feedback", back_populates="user", passive_deletes=True)  # ✅ Links feedback to user

# ✅ PDFs Table
class PDF(Base):
    __tablename__ = "pdfs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)  # ✅ Nullable for guest uploads
    filename = Column(String, nullable=False)
    text = Column(String, nullable=False)  # ✅ Ensure this column exists
    
    # ✅ Relationship
    user = relationship("User", back_populates="pdfs", passive_deletes=True)
    summaries = relationship("Summarization", back_populates="pdf", passive_deletes=True)

# ✅ Summarization Table
class Summarization(Base):
    __tablename__ = "summarization"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    pdf_id = Column(Integer, ForeignKey("pdfs.id", ondelete="CASCADE"), index=True, nullable=False)
    summary_text = Column(Text, nullable=False)

    # ✅ Relationships
    user = relationship("User", back_populates="summaries", passive_deletes=True)
    pdf = relationship("PDF", back_populates="summaries", passive_deletes=True)

# ✅ Feedback Table (Updated to Match Schema)
class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)  # ✅ Linked to user
    rating = Column(Integer, nullable=False)  # ✅ Stores rating (1-5)
    comment = Column(Text, nullable=False)  # ✅  comment

    # ✅ Relationships
    user = relationship("User", back_populates="feedbacks", passive_deletes=True)
