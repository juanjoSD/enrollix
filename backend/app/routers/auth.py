import secrets
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.dependencies import get_db
from app.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.db.security import verify_password, create_access_token, hash_password
from app.schemas.user import UserCreate
from app.services.email_service import send_verification_email



router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()
    
    if not user or verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified. Please check your inbox."
        )
    
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
    
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(400, "Email already registered")
    
    # création de l'utilisateur
    user = User(
        email=user_in.email,
        password=hash_password(user_in.password),
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    # création de l'email de vérification
    token = secrets.token_urlsafe(32)
    
    verification = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    
    db.add(verification)
    db.commit()
    
    # Envoie d'email à l'utilisateur
    
    background_tasks.add_task(
        send_verification_email,
        user.email,
        token
    )
    
    return {"message": "Registration successful. Check your email."}

@router.get("/confirm-email")
def confirm_email(token: str, db: Session = Depends(get_db)):
    record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()

    if not record:
        raise HTTPException(400, "Invalid token")

    if record.expires_at < datetime.utcnow():
        raise HTTPException(400, "Token expired")
    
    user = db.query(User).filter(User.id == record.user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    user.is_verified = True

    db.delete(record)
    db.commit()
    
    
    return {"message": "Email verified successfully"}