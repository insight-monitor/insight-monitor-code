import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()

DEMO_USER = {
    "id": 1,
    "name": "Admin",
    "email": "admin@support.com",
    "role": "admin",
}

DEMO_PASSWORD = "admin123"

TOKEN_EXPIRE_HOURS = 24


def _generate_token() -> str:
    return secrets.token_urlsafe(48)


def _make_response(user: dict) -> dict:
    return {
        "token": _generate_token(),
        "user": user,
    }


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/auth/login")
async def login(body: LoginRequest):
    if body.email == DEMO_USER["email"] and body.password == DEMO_PASSWORD:
        return _make_response(DEMO_USER)

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=401,
        content={"message": "Credenciales inválidas"},
    )


@router.post("/auth/register")
async def register(body: RegisterRequest):
    user = {
        "id": 2,
        "name": body.name,
        "email": body.email,
        "role": "user",
    }
    return _make_response(user)
