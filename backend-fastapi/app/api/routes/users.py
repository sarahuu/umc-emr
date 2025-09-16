from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.schemas.user import UserResponse, UserData, BookAppointmentRequest
from app.services.odoo_client import OdooClient

router = APIRouter(prefix="/user", tags=["users"])
odoo_client = OdooClient()


@router.get("/get-profile", response_model=UserResponse)
def get_me(current_user: dict = Depends(deps.get_current_user)):

    return UserResponse(
        success=True,
        userData=UserData(
            uid=current_user["uid"],
            email=current_user["email"], 
            name=current_user["name"],
            date_of_birth=current_user["date_of_birth"],
            gender=current_user["gender"],
            phone=current_user["phone"]
        )
    )

@router.post("/book-appointment")
def book_appointment(payload: BookAppointmentRequest, current_user=Depends(deps.get_current_user)):
    try:
        result = odoo_client.book_appointment(
            uid=current_user['user_id'][0],
            slot_id=payload.slotId,
            patient_id=current_user['uid'],
            note=payload.note
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments")
def list_appointments(current_user: dict = Depends(deps.get_current_user)):
    try:
        appointments = odoo_client.get_user_appointments(current_user["user_id"][0], current_user['uid'])
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        