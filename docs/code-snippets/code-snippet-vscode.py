import os
import requests

# Load environment variables
CODE_SERVER_URL = os.getenv("DOMAIN", "http://localhost:8080")
CODE_SERVER_PASSWORD = os.getenv("PASSWORD")

# Function to validate connection
def validate_code_server_connection():
    try:
        response = requests.get(
            CODE_SERVER_URL,
            auth=('admin', CODE_SERVER_PASSWORD),
            timeout=10,
        )
        if response.status_code == 200:
            print("VSCode Code-Server connection successful.")
        else:
            print(f"VSCode Code-Server connection failed: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to VSCode Code-Server: {e}")

validate_code_server_connection()
