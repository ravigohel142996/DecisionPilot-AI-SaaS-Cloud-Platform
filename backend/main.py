import os
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token

ADMIN_EMAIL = "admin@visionpilot.ai"
ADMIN_PASSWORD = "admin123"

app = FastAPI(title="VisionPilot AI API", version="2.0.0")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = ["*"] if allowed_origins_env.strip() == "*" else [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


security = HTTPBearer(auto_error=False)


def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    subject = decode_access_token(credentials.credentials)
    if subject != ADMIN_EMAIL:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return subject


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "visionpilot-backend"}


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    email = payload.email.lower().strip()
    password = payload.password

    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(subject=ADMIN_EMAIL, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return AuthResponse(access_token=access_token)


@app.get("/auth/me")
def me(current_user_email: str = Depends(get_current_user_email)):
    return {
        "id": 1,
        "email": current_user_email,
        "full_name": "VisionPilot Admin",
        "is_active": True,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
