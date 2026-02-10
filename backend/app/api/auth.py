from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.entities import Company, User
from app.schemas.auth import (
    CreateUserRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    company = db.scalar(select(Company).where(Company.name == payload.company_name))
    if not company:
        company = Company(name=payload.company_name)
        db.add(company)
        db.flush()

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        company_id=company.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserProfile)
def me(current_user: User = Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        company_id=current_user.company_id,
        company_name=current_user.company.name,
        subscription_tier=current_user.company.subscription_tier,
        subscription_status=current_user.company.subscription_status,
    )


@router.post("/users", response_model=UserProfile)
def create_user(
    payload: CreateUserRequest,
    current_user: User = Depends(require_roles("ceo", "cto")),
    db: Session = Depends(get_db),
):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        company_id=current_user.company_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=user.company_id,
        company_name=current_user.company.name,
        subscription_tier=current_user.company.subscription_tier,
        subscription_status=current_user.company.subscription_status,
    )
