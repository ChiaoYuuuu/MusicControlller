from locust import HttpUser, task, between
import uuid
import json


def register_unique_user(client, prefix="user_", password="testpassword", retries=5):
    for _ in range(retries):
        username = f"{prefix}{uuid.uuid4().hex[:8]}"
        with client.post("/api/register", json={"username": username, "password": password}, catch_response=True) as res:
            if res.status_code == 201:
                res.success()
                token = res.json().get("access")
                return token, username
            elif res.status_code == 400 and res.json().get("error") == "Username already exists":
                res.success()  
            elif res.status_code == 400 and res.json().get("error") == "Username and password are required":
                res.success()  
            else:
                res.failure(f"Unexpected error: {res.status_code} - {res.text}")
    raise Exception("❌ Failed to register unique user after retries")



class User(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        self.token, self.username = register_unique_user(self.client, prefix="host_")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        self.room_code = None

    @task
    def create_room(self):
        if self.room_code:
            return
        res = self.client.post("/api/create-room", json={
            "guest_can_pause": True,
            "votes_to_skip": 2
        }, headers=self.headers)
        if res.status_code == 201:
            self.room_code = res.json().get("code")

    @task
    def leave_room(self):
        if self.room_code:
            self.client.post("/api/leave-room", headers=self.headers)
            self.room_code = None



