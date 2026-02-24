from fastapi import APIRouter,  HTTPException
from pydantic import BaseModel, Field, EmailStr

router = APIRouter()

class UserIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Имя пользователя")
    age: int = Field(..., ge=0, le=120, description="Возраст от 0 до 120")
    email: EmailStr = Field(..., description="Электронная почта")
    is_active: bool = Field(True, description="Флаг активности, по умолчанию True")

@router.post("/user")
def validate_user(payload: UserIn):
    return {"ok": True, "user": payload}

@router.post("/user/register")
def register_user(payload: UserIn):
    if payload.age < 18:
        raise HTTPException(
            status_code=400,
            detail="Регистрация доступна только с 18 лет",
        )
    return {"ok": True, "message": "Пользователь зарегистрирован", "user": payload}