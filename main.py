
import time
import requests
import json
import random
from datetime import datetime, timezone

# Configuration
DEVICE_ID = "1804030000F00000"
IMEI = "860384067029857"
ICCID = "89981129000715130234"
API_URL = "http://connectedcars.ir/platform/api/device/aes+YT@NlxJtq_@)/telemetry"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Connection": "keep-alive"
}

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def interpolate_position(start_pos, end_pos, progress):
    lat = start_pos["lat"] + (end_pos["lat"] - start_pos["lat"]) * progress
    lon = start_pos["lon"] + (end_pos["lon"] - start_pos["lon"]) * progress
    alt = start_pos["alt"] + (end_pos["alt"] - start_pos["alt"]) * progress
    return {"lat": lat, "lon": lon, "alt": alt}

# Define route waypoints (lat, lon, altitude)
ROUTES = {
    "tehran_bandar": {
        "name": "Tehran-Bandar Abbas",
        "duration_days": 10,
        "waypoints": [
            {"lat": 35.6892, "lon": 51.3890, "alt": 1200},  # Tehran
            {"lat": 27.1832, "lon": 56.2667, "alt": 9}      # Bandar Abbas
        ]
    },
    "tehran_mazandaran": {
        "name": "Tehran-Mazandaran",
        "duration_days": 7,
        "waypoints": [
            {"lat": 35.6892, "lon": 51.3890, "alt": 1200},  # Tehran
            {"lat": 36.5659, "lon": 53.0586, "alt": -21}    # Sari (Mazandaran)
        ]
    },
    "tehran_isfahan": {
        "name": "Tehran-Isfahan",
        "duration_days": 5,
        "waypoints": [
            {"lat": 35.6892, "lon": 51.3890, "alt": 1200},  # Tehran
            {"lat": 32.6539, "lon": 51.6660, "alt": 1574}   # Isfahan
        ]
    }
}

def get_current_position():
    current_time = time.time()
    
    # Calculate total cycle duration in seconds
    total_duration = sum(route["duration_days"] * 86400 for route in ROUTES.values())
    
    # Get current cycle progress
    cycle_progress = (current_time % total_duration) / total_duration
    
    # Determine current route
    current_time_in_cycle = (current_time % total_duration)
    elapsed_time = 0
    
    for route_id, route in ROUTES.items():
        route_duration = route["duration_days"] * 86400
        if current_time_in_cycle < elapsed_time + route_duration:
            # We're on this route
            route_progress = (current_time_in_cycle - elapsed_time) / route_duration
            
            # Handle return journey
            going_forward = route_progress < 0.5
            progress = route_progress * 2 if going_forward else (1 - (route_progress - 0.5) * 2)
            
            pos = interpolate_position(
                route["waypoints"][0],
                route["waypoints"][1],
                progress
            )
            
            # Add some randomness to make movement more realistic
            pos["lat"] += random.uniform(-0.01, 0.01)
            pos["lon"] += random.uniform(-0.01, 0.01)
            pos["alt"] += random.randint(-20, 20)
            
            return pos
            
        elapsed_time += route_duration
    
    return ROUTES["tehran_bandar"]["waypoints"][0]  # Fallback to Tehran

def generate_position_data():
    pos = get_current_position()
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
                "Lat": str(pos["lat"]),
                "Long": str(pos["lon"]),
                "ALT": str(int(pos["alt"])),
                "SPD": str(random.randint(60, 100)),  # Highway speeds
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
            
            for attempt in range(MAX_RETRIES):
                try:
                    response = requests.post(API_URL, json=data, headers=HEADERS, timeout=10)
                    print(f"Response status: {response.status_code}")
                    if response.status_code == 200:
                        break
                    print(f"Error response: {response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {str(e)}")
                    if attempt < MAX_RETRIES - 1:
                        print(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        print("Max retries reached. Moving to next data point.")
            
            time.sleep(5)  # Wait 5 seconds between different message types

if __name__ == "__main__":
    try:
        print("Starting smart lock data simulation...")
        send_data()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
