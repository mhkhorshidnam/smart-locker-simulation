
import time
import requests

# Constants
API_URL = "http://connectedcars.ir/platform/api/device/aes+YT@NlxJtq_@)/telemetry"
HEADERS = {"Content-Type": "application/json"}
PROVINCES = {
    "Province1": "data1",
    "Province2": "data2",
    "Province3": "data3"
}

def generate_data(province, step):
    # Add your data generation logic here
    return {
        "province": province,
        "step": step,
        "timestamp": time.time()
    }

# Initialize variables
current_province = list(PROVINCES.keys())[0]
step = 0

while True:
    data = generate_data(current_province, step)
    print(f"Sending data from: {current_province}...")

    try:
        response = requests.post(API_URL, json=data, headers=HEADERS)
        print(f"Status: {response.status_code} | Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    step += 1
    if step % 12 == 0:
        provinces_list = list(PROVINCES.keys())
        current_index = provinces_list.index(current_province)
        current_province = provinces_list[(current_index + 1) % len(provinces_list)]
        print(f"\nMoving to: {current_province}\n")

    time.sleep(10)
