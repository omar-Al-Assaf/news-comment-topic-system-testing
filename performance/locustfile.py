from locust import HttpUser, task, between


class StreamlitUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def load_home_page(self):
        with self.client.get("/", name="GET /", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
