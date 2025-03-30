
import time
import requests

# Constants
from urllib.parse import quote

device_id = "aes+YT@NlxJtq_@)"
encoded_device_id = quote(device_id)
API_URL = f"http://connectedcars.ir/platform/api/device/{encoded_device_id}/telemetry"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

PROVINCES = {
    "Province1": {"latitude": 35.6892, "longitude": 51.3890},  # Tehran
    "Province2": {"latitude": 32.6539, "longitude": 51.6660},  # Isfahan
    "Province3": {"latitude": 29.5926, "longitude": 52.5836}   # Shiraz
}

def generate_data(province, step):
    province_data = PROVINCES[province]
    return {
        "deviceId": device_id,
        "location": {
            "lat": province_data["latitude"],
            "lng": province_data["longitude"]
        },
        "speed": 60 + (step % 20),  # Simulated speed between 60-80 km/h
        "timestamp": int(time.time() * 1000)  # Millisecond timestamp
    }

# Initialize variables
current_province = list(PROVINCES.keys())[0]
step = 0

while True:
    data = generate_data(current_province, step)
    print(f"Sending data from: {current_province}...")

    try:
        response = requests.post(API_URL, json=data, headers=HEADERS, timeout=5)
        print(f"Status: {response.status_code} | Response: {response.text}")
    except requests.Timeout:
        print("Request timed out - API server took too long to respond")
    except requests.ConnectionError:
        print("Connection error - Could not connect to the API server")
    except Exception as e:
        print(f"Error: {e}")

    step += 1
    if step % 12 == 0:
        provinces_list = list(PROVINCES.keys())
        current_index = provinces_list.index(current_province)
        current_province = provinces_list[(current_index + 1) % len(provinces_list)]
        print(f"\nMoving to: {current_province}\n")

    time.sleep(10)
