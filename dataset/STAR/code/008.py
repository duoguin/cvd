import requests

def hotel_service_request():
    # 1. Ask the guest for their name.
    customer_name = input("Please enter your name: ")
    
    # 2. Ask the guest which hotel they are staying at.
    print("Which hotel are you staying at?")
    print("1. Shadyside Inn\n2. Hilton Hotel\n3. Hyatt Hotel\n4. Old Town Inn")
    hotel_choice = int(input("Please select the number corresponding to your hotel: "))
    hotels = ["Shadyside Inn", "Hilton Hotel", "Hyatt Hotel", "Old Town Inn"]
    hotel_name = hotels[hotel_choice - 1]
    
    # 3. Ask the guest for their room number.
    room_number = int(input("Please enter your room number: "))
    
    # 4. Ask the guest what service they are requesting.
    customer_request = input("What service are you requesting? ")
    
    # 5. Ask the guest when they would like the service.
    print("When would you like the service? (Please specify in 'am' or 'pm')")
    service_time = input("Time: ")
    
    # 6. Process the service request.
    api_url = "http://example.com/hotel_service_request"  # Example API endpoint
    data = {
        "Name": hotel_name,
        "RoomNumber": room_number,
        "Time": service_time,
        "CustomerName": customer_name,
        "CustomerRequest": customer_request
    }
    response = requests.post(api_url, json=data)
    result = response.json()
    
    # 7. If the service request is successful, inform the guest.
    if result["RequestStatus"] == "Request Confirmed":
        print("Your service request was successful.")
    # 8. If the service request fails, inform the guest.
    else:
        print("Your service request failed.")
    
    # 9. Ask the guest if there is anything else they need.
    additional_request = input("Is there anything else you need? (yes/no) ")
    if additional_request.lower() == "yes":
        print("Please let us know what else you need.")
        # Here, you can repeat the process or handle additional requests as needed.
    else:
        print("Thank you! If you need anything else, please don't hesitate to ask.")

# Call the function to start the service request process
hotel_service_request()