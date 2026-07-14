from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, User

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Request model
class UserRegister(BaseModel):
    email: EmailStr
    password: str


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register API
@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = User(
        email=user.email,
        password=user.password   # Hash passwords in production
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "email": new_user.email
    }