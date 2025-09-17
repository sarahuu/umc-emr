from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.schemas.doctors import DoctorResponse, DoctorAvailability
from app.services.odoo_client import OdooClient
import redis, json
from app.core.config import settings

odoo_client = OdooClient()
router = APIRouter(prefix="/doctor", tags=["doctors"])
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
CACHE_TTL = 300  # cache time in seconds (1 minute)

@router.get("/list", response_model=DoctorResponse)
def get_doctor_list(current_user: dict = Depends(deps.get_current_user)):
    uid = current_user["user_id"][0]
    cache_key = f"doctor_list:{uid}"
    cached = redis_client.get(cache_key)
    if cached:
        doctors = json.loads(cached)
    else:
        try:
            doctors = odoo_client.get_doctor_list(uid)
            if not doctors:
                raise HTTPException(status_code=404, detail="No doctors found")
            redis_client.setex(cache_key, CACHE_TTL, json.dumps(doctors))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return DoctorResponse(success=True, doctorData=doctors)


@router.get("/{clinic_type}/{doctor_id}/availability", response_model=DoctorAvailability)
def get_doctor_availability(clinic_type: str, doctor_id: int, current_user: dict = Depends(deps.get_current_user)):
    uid = current_user["user_id"][0]
    cache_key = f"doctor_availability:{clinic_type}:{doctor_id}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    try:
        availability = odoo_client.get_doctor_availability(uid, doctor_id, clinic_type)
        if not availability:
            raise HTTPException(status_code=404, detail="Doctor not found")
        redis_client.setex(cache_key, 30, json.dumps(availability))
        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
