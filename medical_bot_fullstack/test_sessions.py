import requests
import time

BASE_URL = "http://127.0.0.1:8001"
EMAIL = f"session_test_{int(time.time())}@example.com"
PASSWORD = "password123"

def run_test():
    # 1. Signup & Login
    print(f"Creating user {EMAIL}...")
    requests.post(f"{BASE_URL}/signup", json={"email": EMAIL, "password": PASSWORD})
    resp = requests.post(f"{BASE_URL}/login", data={"username": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        print("Login failed")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Create Session
    print("Creating Session 1...")
    resp = requests.post(f"{BASE_URL}/sessions", headers=headers)
    if resp.status_code != 201:
        print(f"Create session failed: {resp.text}")
        return
    session1 = resp.json()
    print(f"Session 1 created: {session1['id']}")

    # 3. Chat in Session 1
    print("Sending message to Session 1...")
    resp = requests.post(f"{BASE_URL}/chat", json={"message": "Hello session 1", "session_id": session1['id']}, headers=headers)
    print(f"Reply: {resp.json().get('reply', 'Error')[:20]}...")

    # 4. Create Session 2
    print("Creating Session 2...")
    resp = requests.post(f"{BASE_URL}/sessions", headers=headers)
    session2 = resp.json()
    print(f"Session 2 created: {session2['id']}")

    # 5. List Sessions
    print("Listing sessions...")
    resp = requests.get(f"{BASE_URL}/sessions", headers=headers)
    sessions = resp.json()
    print(f"Found {len(sessions)} sessions.")
    if len(sessions) != 2:
        print("Error: Expected 2 sessions.")
    
    # 6. Get Messages for Session 1
    print("Fetching messages for Session 1...")
    resp = requests.get(f"{BASE_URL}/sessions/{session1['id']}/messages", headers=headers)
    msgs = resp.json()
    print(f"Session 1 has {len(msgs)} messages.")
    
    print("Test Complete.")

if __name__ == "__main__":
    run_test()
