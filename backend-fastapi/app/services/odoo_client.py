import xmlrpc.client
from fastapi import HTTPException, status
from app.core.config import settings
from app.services.session import SecureSessionStore

class OdooClient:
    def __init__(self):
        self.url = settings.ODOO_URL
        self.db = settings.ODOO_DB
        self.token = settings.ODOO_API_KEY
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
        self.session_store = SecureSessionStore()

    def authenticate(self, username: str, password: str):
        uid = self.common.authenticate(self.db, username, password, {})
        if not uid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        self.session_store.save_user_credentials(uid, password)
        return uid
    
    def get_or_create_api_key(self, uid: int, password: str, scope="emr") -> str:
        return self.models.execute_kw(
            self.db, uid, password,
            "res.users", "get_or_create_api_key",
            [uid], {"scope": scope}
        )

    def get_user_info(self, uid: int, password: str):
        user = self.models.execute_kw(
            self.db, uid, password,
        "patient.record", "search_read",
        [[("user_id", "=", uid)]],
        {"fields": ["id","name","email","user_id", "date_of_birth","phone","gender"]}
        )
        return user[0] if user else None
    
    def get_doctor_list(self, uid:int):
        password = self.session_store.get_user_password(uid)
        doctors = self.models.execute_kw(
            self.db, uid, password,
            'emr.provider', 'get_doctor_data', [[]]
        )
        return doctors
    
    def get_doctor_availability(self, uid: int, doctor_id:int, clinic_type):
        password = self.session_store.get_user_password(uid)
        return self.models.execute_kw(
            self.db, uid, password,
            "emr.provider", "get_doctor_availability",
            [doctor_id, clinic_type]
        )
    
    def book_appointment(self, uid: int, slot_id: int, patient_id: int, note: str):
        password = self.session_store.get_user_password(uid)
        return self.models.execute_kw(
            self.db, uid, password,
            "appointment.appointment", "book_appointment",
            [slot_id, patient_id, note]
        )

    def get_user_appointments(self, uid: int, patient_id:int):
        password = self.session_store.get_user_password(uid)
        return self.models.execute_kw(
            self.db, uid, password,
            "appointment.appointment", "get_user_appointments",
            [patient_id]
        )


