
import time
import requests
import json
import random
from datetime import datetime, timezone

# Configuration
DEVICE_ID = "1804030000F00000"
IMEI = "860384067029857"
ICCID = "89981129000715130234"
API_URL = "http://connectedcars.ir/platform/api/device/87654321/telemetry"

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
# Bandar Abbas Railway Station coordinates
BANDAR_RAILWAY = {"lat": 27.1443, "lon": 56.2504}
GEOFENCE_RADIUS = 4  # km

# Main route waypoints following asphalt roads
ROUTE = {
    "name": "Tehran-Bandar Abbas",
    "duration_hours": 50,
    "waypoints": [
        {"lat": 35.6892, "lon": 51.3890, "alt": 1200},  # Tehran
        {"lat": 35.3061, "lon": 51.4045, "alt": 1000},  # Qom
        {"lat": 33.9956, "lon": 51.4482, "alt": 900},   # Kashan
        {"lat": 32.6539, "lon": 51.6660, "alt": 1574},  # Isfahan
        {"lat": 30.2839, "lon": 52.5918, "alt": 1500},  # Shiraz
        {"lat": 28.9784, "lon": 53.9919, "alt": 800},   # Sirjan
        {"lat": 27.1832, "lon": 56.2667, "alt": 9}      # Bandar Abbas
    ]
}

def calculate_distance(pos1, pos2):
    from math import sin, cos, sqrt, atan2, radians
    R = 6371  # Earth's radius in km
    lat1, lon1 = radians(float(pos1["lat"])), radians(float(pos1["lon"]))
    lat2, lon2 = radians(float(pos2["lat"])), radians(float(pos2["lon"]))
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_current_position():
    current_time = time.time()
    start_time = current_time % (ROUTE["duration_hours"] * 3600)
    progress = start_time / (ROUTE["duration_hours"] * 3600)
    
    # Find current segment
    waypoints = ROUTE["waypoints"]
    num_segments = len(waypoints) - 1
    segment_progress = progress * num_segments
    current_segment = int(segment_progress)
    
    if current_segment >= num_segments:
        return waypoints[-1]
    
    # Calculate position within current segment
    segment_pos = segment_progress - current_segment
    pos = interpolate_position(
        waypoints[current_segment],
        waypoints[current_segment + 1],
        segment_pos
    )
    
    # Add slight randomness for realism
    pos["lat"] += random.uniform(-0.001, 0.001)
    pos["lon"] += random.uniform(-0.001, 0.001)
    pos["alt"] += random.randint(-5, 5)
    
    # Check if we're in railway station geofence
    distance_to_railway = calculate_distance(pos, BANDAR_RAILWAY)
    if distance_to_railway <= GEOFENCE_RADIUS:
        print(f"\nALERT: Container has entered Bandar Abbas Railway Station zone!")
        print(f"Distance to railway station: {distance_to_railway:.2f} km")
        print("SMS notification would be sent to cargo owner")
    
    return pos

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
            
            time.sleep(180)  # Wait 3 minutes between different message types

if __name__ == "__main__":
    try:
        print("Starting smart lock data simulation...")
        send_data()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
