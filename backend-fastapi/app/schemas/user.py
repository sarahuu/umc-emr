from pydantic import BaseModel, EmailStr
from datetime import date

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserData(BaseModel):
    uid: int
    email: str
    name: str
    phone: str
    date_of_birth: date
    gender: str
    # user_id: int

class UserResponse(BaseModel):
    success: bool
    userData: UserData

class BookAppointmentRequest(BaseModel):
    slotId: int
    patientId: int
    note: str

class ErrorResponse(BaseModel):
    code: int
    message: str