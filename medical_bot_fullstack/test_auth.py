import requests
import time

BASE_URL = "http://127.0.0.1:8001"
EMAIL = f"testuser_{int(time.time())}@example.com"
PASSWORD = "securepassword123"

def test_signup():
    print(f"Testing Signup with {EMAIL}...")
    response = requests.post(f"{BASE_URL}/signup", json={"email": EMAIL, "password": PASSWORD})
    if response.status_code == 201:
        print("Signup Successful")
    else:
        print(f"Signup Failed: {response.text}")
        exit(1)

def test_login():
    print("Testing Login...")
    response = requests.post(f"{BASE_URL}/login", data={"username": EMAIL, "password": PASSWORD})
    if response.status_code == 200:
        print("Login Successful")
        return response.json()["access_token"]
    else:
        print(f"Login Failed: {response.text}")
        exit(1)

def test_protected_chat(token):
    print("Testing Protected Chat Route...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": "Hello, doctor!"}
    
    response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
    if response.status_code == 200:
        print("Protected Chat Access Successful")
        print(f"Bot Reply: {response.json().get('reply', 'No reply field')[:50]}...")
    else:
        print(f"Protected Chat Access Failed: {response.status_code} - {response.text}")

def test_unauthorized_access():
    print("Testing Unauthorized Access...")
    payload = {"message": "Hello, doctor!"}
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    if response.status_code == 401:
        print("Unauthorized Access Blocked (As Expected)")
    else:
        print(f"Security Failure! Unauthorized access allowed: {response.status_code}")

if __name__ == "__main__":
    test_signup()
    token = test_login()
    test_protected_chat(token)
    test_unauthorized_access()
