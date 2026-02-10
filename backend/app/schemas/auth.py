from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""
    role: str = Field(default="ceo", pattern="^(ceo|cto|manager|analyst)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    company_id: int
    company_name: str
    subscription_tier: str
    subscription_status: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = ""
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(ceo|cto|manager|analyst)$")
