from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.schemas.doctors import DoctorResponse, DoctorAvailability
from app.services.odoo_client import OdooClient

odoo_client = OdooClient()
router = APIRouter(prefix="/doctor", tags=["doctors"])

@router.get("/list", response_model=DoctorResponse)
def get_doctor_list(current_user: dict = Depends(deps.get_current_user)):
    uid = current_user["user_id"][0]
    doctors = odoo_client.get_doctor_list(uid)
    return DoctorResponse(success=True, doctorData=doctors)

@router.get("/{clinic_type}/{doctor_id}/availability", response_model=DoctorAvailability)
def get_doctor_availability(clinic_type:str, doctor_id: int, current_user: dict = Depends(deps.get_current_user)):
    try:
        uid = current_user["user_id"][0]
        availability = odoo_client.get_doctor_availability(uid, doctor_id, clinic_type)
        if not availability:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))