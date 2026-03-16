import requests

BASE_URL = "http://localhost:5000"
headers = {"Authorization": "Bearer validtoken"}

def print_resp(label, resp):
    print(f"{label}: {resp.status_code}", resp.json())

# Get users
print_resp("GET /users/", requests.get(f"{BASE_URL}/users/", headers=headers))

# Create user
user_data = {
    "username": "testuser",
    "password": "testpass",
    "firstname": "Test",
    "lastname": "User",
    "balance": 500.0
}
print_resp("POST /users/", requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers))

# Get user details
print_resp("GET /users/testuser", requests.get(f"{BASE_URL}/users/testuser", headers=headers))

# Update user balance
update_data = {"username": "testuser", "new_balance": 1000.0}
print_resp("PUT /users/update-balance", requests.put(f"{BASE_URL}/users/update-balance", json=update_data, headers=headers))

# Delete user
print_resp("DELETE /users/testuser", requests.delete(f"{BASE_URL}/users/testuser", headers=headers))
