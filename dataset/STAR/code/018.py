import requests

def get_ride_status(customer_name, booking_id):
    """
    Fetch the status of a ride booking.
    
    Parameters:
    - customer_name: The name of the customer.
    - booking_id: The unique identifier for the ride booking.
    
    Returns:
    A dictionary containing the status and details of the ride.
    """
    # Assuming there's a predefined URL for the ride_status API
    API_URL = "http://example.com/api/ride_status"
    payload = {
        "CustomerName": customer_name,
        "id": booking_id
    }
    
    try:
        response = requests.get(API_URL, params=payload)
        response.raise_for_status()  # Raise an error for bad responses
        ride_details = response.json()
        return ride_details
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ride status: {e}")
        return None

def main():
    print("Welcome to the Ride Status Checker!")
    
    # Step 1: Ask the user for their name
    customer_name = input("Please enter your name: ")
    
    # Step 2: Ask the user for their ride booking number
    booking_id = input("Please enter your ride booking number: ")
    
    # Ensure the booking ID is an integer
    try:
        booking_id = int(booking_id)
    except ValueError:
        print("Invalid booking number. Please enter a valid number.")
        return
    
    # Step 3 & 4: Query the ride status and provide the user with the status of their booking
    ride_status = get_ride_status(customer_name, booking_id)
    if ride_status:
        print(f"Ride Status: {ride_status.get('RideStatus', 'Not available')}")
        print(f"Wait Time: {ride_status.get('RideWait', 'Not available')}")
        # Step 5: Provide any updates regarding the booking status
        print("Updates regarding your booking will be sent to you as they come.")
    else:
        print("Failed to retrieve the status of your booking.")
    
    # Step 6: Ask the user if they need assistance with anything else
    assistance = input("Do you need assistance with anything else? (yes/no): ")
    if assistance.lower() == "yes":
        print("Please specify how we can assist you further.")
    else:
        print("Thank you for using the Ride Status Checker. Have a great day!")

if __name__ == "__main__":
    main()