from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User, AshaWorker
from app.schemas.schemas import UserLogin, UserRegister, TokenResponse
from app.core.security import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/demo-login", response_model=TokenResponse)
def demo_login(db: Session = Depends(get_db)):
    """Convenient 1-click hackathon demo login using synthetic ASHA worker profile."""
    user = db.query(User).filter(User.email == "asha.shweta@karnataka.gov.in").first()
    if not user:
        # Fallback to any user
        user = db.query(User).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Demo account not initialized")

    token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role
    )
    db.add(new_user)
    db.flush()

    asha = AshaWorker(
        user_id=new_user.id,
        worker_id=data.worker_id or f"ASHA-BLR-{new_user.id:03d}",
        assigned_area=data.assigned_area or "Bengaluru Urban",
        village=data.village or "Kadugodi",
        total_visits=0
    )
    db.add(asha)
    db.commit()

    token = create_access_token(data={"sub": new_user.email, "role": new_user.role, "user_id": new_user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    }
