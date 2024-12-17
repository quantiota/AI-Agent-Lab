import os
import requests

GRAFANA_URL = "http://localhost:3000/api/search"
GRAFANA_USER = os.getenv("GF_SECURITY_ADMIN_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GF_SECURITY_ADMIN_PASSWORD", "admin")

def validate_grafana_connection():
    try:
        response = requests.get(
            GRAFANA_URL,
            auth=(GRAFANA_USER, GRAFANA_PASSWORD),
            timeout=10,
        )
        if response.status_code == 200:
            print("Grafana connection successful.")
        else:
            print(f"Grafana connection failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error connecting to Grafana: {e}")

validate_grafana_connection()
