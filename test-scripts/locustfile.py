from locust import HttpUser, task, between

class AuthUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        resp = self.client.post("/api/auth/login", json={"email":"mofe.abe@umcemr.com","password":"october7"})
        self.token = resp.json().get("access_token")
        self.auth_headers = {"Authorization": f"Bearer {self.token}"}

    @task(10)
    def profile(self):
        with self.client.get("/api/user/get-profile", headers=self.auth_headers, name="GET /api/user/get-profile", catch_response=True) as response:
            if response.status_code >= 500:
                response.failure(f"500 Error: {response.text[:200]}")

    @task(10)
    def get_doctors_list(self):
        with self.client.get("/api/doctor/list", headers=self.auth_headers, name="GET /api/doctor/list", catch_response=True) as response:
            if response.status_code >= 500:
                response.failure(f"500 Error: {response.text[:200]}")

    @task(6)
    def get_doctors_availability(self):
        self.client.get("/api/doctor/general-outpatient-clinic/2/availability", headers=self.auth_headers, name="GET /api/doctor/{clinic_type}/{doctor_id}/availability")

