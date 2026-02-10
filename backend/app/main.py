from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Enable CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Database (Temporary)
# ---------------------------
users_db = {}


# ---------------------------
# Models
# ---------------------------
class RegisterUser(BaseModel):
    company_name: str
    full_name: str
    email: str
    password: str
    role: str


class LoginUser(BaseModel):
    email: str
    password: str


# ---------------------------
# Routes
# ---------------------------

@app.get("/")
def home():
    return {"status": "VisionPilot Backend Running"}


@app.post("/auth/register")
def register(user: RegisterUser):

    if user.email in users_db:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    users_db[user.email] = {
        "company": user.company_name,
        "name": user.full_name,
        "password": user.password,
        "role": user.role
    }

    return {
        "success": True,
        "message": "Registration successful"
    }


@app.post("/auth/login")
def login(data: LoginUser):

    if data.email not in users_db:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if users_db[data.email]["password"] != data.password:
        raise HTTPException(
            status_code=401,
            detail="Wrong password"
        )

    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "email": data.email,
            "name": users_db[data.email]["name"],
            "role": users_db[data.email]["role"]
        }
    }


# ---------------------------
# Run Local
# ---------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
