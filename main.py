step = 0  # Proper initialization

while True:
    data = generate_data(current_province, step)
    print(f"Sending data from: {current_province}...")  # Fixed print + f-string

    try:
        response = requests.post(API_URL, json=data, headers=HEADERS)
        print(f"Status: {response.status_code} | Response: {response.text}")  # Fixed
    except Exception as e:
        print(f"Error: {e}")  # Fixed

    step += 1
    if step % 12 == 0:  # Fixed comparison
        provinces_list = list(PROVINCES.keys())
        current_index = provinces_list.index(current_province)
        current_province = provinces_list[(current_index + 1) % len(provinces_list)]  # Fixed parentheses
        print(f"\nMoving to: {current_province}\n")  # Fixed typo in "Moving"

    time.sleep(10)  # Correct sleep duration