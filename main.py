
import time
import requests
import json
import random
from datetime import datetime, timezone

# Configuration
DEVICE_ID = "1804030000F00000"
IMEI = "860384067029857"
ICCID = "89981129000715130234"
API_URL = f"http://connectedcars.ir/platform/api/device/aes+YT@NlxJtq_@)/telemetry"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def generate_position_data():
    return {
        "Header": {
            "DeviceID": DEVICE_ID,
            "IMEI": IMEI,
            "ICCID": ICCID,
            "MsgType": "POS"
        },
        "Data": {
            "NumberOfPoint": "1",
            "POS": {
                "@sequence": "0",
                "MessageContent": "MjFENzdERTMwRTdDRjU2MEY3QkIwMkQ2",
                "DateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                "Lat": str(35.8094368 + random.uniform(-0.1, 0.1)),
                "Long": str(51.4685669 + random.uniform(-0.1, 0.1)),
                "ALT": str(1678 + random.randint(-50, 50)),
                "SPD": str(random.randint(0, 80)),
                "COG": str(random.randint(0, 359)),
                "NoSat": str(random.randint(6, 12)),
                "LatHemisphere": "Northern",
                "LongHemisphere": "Eastern"
            }
        }
    }

def generate_event_data():
    return {
        "Header": {
            "DeviceID": DEVICE_ID,
            "IMEI": IMEI,
            "ICCID": ICCID,
            "MsgType": "Event"
        },
        "Data": {
            "POS": {
                "@sequence": "0",
                "MessageContent": "NULL",
                "DateTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                "Lat": str(35.7140541 + random.uniform(-0.1, 0.1)),
                "Long": str(51.43813 + random.uniform(-0.1, 0.1)),
                "ALT": str(1320 + random.randint(-50, 50)),
                "SPD": str(random.randint(0, 5)),
                "COG": str(random.randint(0, 359)),
                "NoSat": str(random.randint(6, 12)),
                "LatHemisphere": "Northern",
                "LongHemisphere": "Eastern"
            },
            "EventId": str(random.randint(1, 5)),
            "GPInput": {
                "IO": {
                    "CAN": {
                        "@Source": "1",
                        "@Range": "Over",
                        "CurrentValue": str(random.randint(2000, 3000)),
                        "SampleDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    }
                }
            },
            "Geofenc": {"@xsi:nil": "true"},
            "OverSpeed": {"@xsi:nil": "true"},
            "CallMe": {"@xsi:nil": "true"}
        }
    }

def generate_ios_data():
    return {
        "Header": {
            "DeviceID": DEVICE_ID,
            "IMEI": IMEI,
            "ICCID": ICCID,
            "MsgType": "IOs"
        },
        "Data": {
            "NumberOfIO": "3",
            "IOTransaction": [
                {
                    "@IOSequence": "Engine_Speed",
                    "Type": "CAN",
                    "CurrentValue": {
                        "AnalogValue": str(random.randint(600, 800))
                    },
                    "SampleDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                {
                    "@IOSequence": "Engine_Coolant_Temperatur",
                    "Type": "CAN",
                    "CurrentValue": {
                        "AnalogValue": str(random.randint(-15, 95))
                    },
                    "SampleDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                {
                    "@IOSequence": "Engine_Oil_Temperatur",
                    "Type": "CAN",
                    "CurrentValue": {
                        "AnalogValue": str(random.randint(70, 110))
                    },
                    "SampleDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            ],
            "MsgContent": "IzAwMTAwMDAwMkUwIzAwMkZGRkZGRkY0IzAwMzAwMDAwMDU2"
        }
    }

def send_data():
    data_generators = [
        generate_position_data,
        generate_event_data,
        generate_ios_data
    ]
    
    while True:
        for generator in data_generators:
            data = generator()
            print(f"\nSending {data['Header']['MsgType']} data...")
            print(json.dumps(data, indent=2))
            
            try:
                response = requests.post(API_URL, json=data, headers=HEADERS, timeout=10)
                print(f"Response status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Error response: {response.text}")
            except Exception as e:
                print(f"Error sending data: {str(e)}")
            
            time.sleep(5)  # Wait 5 seconds between different message types

if __name__ == "__main__":
    try:
        print("Starting smart lock data simulation...")
        send_data()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
