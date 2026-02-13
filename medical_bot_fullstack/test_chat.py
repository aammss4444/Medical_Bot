import requests
import json

def test_chat():
    url = "http://127.0.0.1:8001/chat"
    
    # Message 1
    payload1 = {"message": "Hi, I'm finding it hard to sleep at night."}
    print(f"User: {payload1['message']}")
    try:
        response1 = requests.post(url, json=payload1)
        response1.raise_for_status()
        print(f"Bot: {response1.json()['reply']}\n")
    except Exception as e:
        print(f"Error calling API: {e}")
        return

    # Message 2 (Context dependent)
    payload2 = {"message": "What could be the reason for this?"}
    print(f"User: {payload2['message']}")
    try:
        response2 = requests.post(url, json=payload2)
        response2.raise_for_status()
        print(f"Bot: {response2.json()['reply']}\n")
    except Exception as e:
        print(f"Error calling API: {e}")

if __name__ == "__main__":
    test_chat()
