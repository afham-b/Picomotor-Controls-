import requests

try:
    response = requests.get("http://localhost:4400")
    response.raise_for_status()
    print("PHD2 server is running and accessible")
except requests.exceptions.RequestException as e:
    print(f"Failed to connect to PHD2 server: {e}")