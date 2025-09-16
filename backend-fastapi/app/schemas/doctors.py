from pydantic import BaseModel, EmailStr
from datetime import date
from typing import List, Optional

class DoctorData(BaseModel):
    id: int
    name: str
    speciality: str
    about: str
    clinic_type: str
    clinic_type_slug: str
    is_available: bool

class DoctorResponse(BaseModel):
    success: bool
    doctorData: List[DoctorData]

class DoctorSlotTime(BaseModel):
    id: int
    time: str

class DoctorSlot(BaseModel):
    date: str
    slots: List[DoctorSlotTime]

class DoctorAvailability(BaseModel):
    name: str
    about: str
    doctor_id: int
    clinic_type: str
    clinic_type_slug: str
    availability: List[DoctorSlot]

class ErrorResponse(BaseModel):
    code: int
    message: str