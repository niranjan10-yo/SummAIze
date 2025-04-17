from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from schemas import UserCreate, UserResponse, LoginRequest
import models
from passlib.context import CryptContext
import jwt  # For JWT token generation
from fastapi.security import OAuth2PasswordBearer

# Create a router with prefix "/auth"
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Secret Key & Algorithm (Change 'your_secret_key' to something secure)
SECRET_KEY = "your_secret_key"  # In production, use environment variables for this
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expires in 1 hour

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generates JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

# Register a new user
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user with a hashed password."""
    
    # Check if username OR email already exists
    existing_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")

    # Hash password before saving
    hashed_pwd = hash_password(user.password)

    # Create a new user object
    new_user = models.User(username=user.username, email=user.email, password=hashed_pwd)

    # Save user to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token for the new user
    token = create_access_token({"sub": new_user.email})

    # Return user data with token
    return {
        "id": new_user.id,
        "user_id": new_user.id,  # Added for frontend compatibility
        "username": new_user.username,
        "email": new_user.email,
        "token": token
    }

# Login Route
@router.post("/login")
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates a user with email and password and returns a JWT token."""
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    token = create_access_token({"sub": user.email})

    return {
        "id": user.id,
        "user_id": user.id,  # Added for frontend compatibility
        "username": user.username,
        "email": user.email,
        "token": token
    }

# Test route for debugging
@router.get("/test")
def test_auth():
    """Test if the authentication module is working."""
    return {"message": "Authentication module is working!"}
