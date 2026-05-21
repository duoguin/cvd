def plane_book(id, CustomerName, RequestType):
    # This is a placeholder for the actual API call.
    # The real implementation would involve sending a request to the API's endpoint.
    # Here, we'll simulate different responses based on the input.
    if RequestType == "Check":
        if id % 2 == 0:  # Simulate that even-numbered flights are available.
            return {"ReservationStatus": "Available"}
        else:
            return {"ReservationStatus": "Unavailable"}
    elif RequestType == "Book":
        if id % 2 == 0:  # Simulate successful booking for even-numbered flights.
            return {"ReservationStatus": "Confirmed"}
        else:
            return {"ReservationStatus": "Failed"}

def main():
    print("Welcome to the Flight Reservation Service.")
    customer_name = input("Please enter your name: ")
    
    while True:
        flight_id_str = input("Please enter the flight ID you wish to book: ")
        try:
            flight_id = int(flight_id_str)
        except ValueError:
            print("Invalid flight ID. Please enter a numeric value.")
            continue

        availability_check = plane_book(flight_id, customer_name, "Check")
        if availability_check["ReservationStatus"] == "Unavailable":
            print("Unfortunately, the flight is unavailable. Please try a different flight ID.")
            continue
        
        proceed_with_booking = input("The flight is available. Do you want to proceed with the booking? (yes/no): ").lower()
        if proceed_with_booking not in ['yes', 'y']:
            continue
        
        booking_attempt = plane_book(flight_id, customer_name, "Book")
        if booking_attempt["ReservationStatus"] == "Confirmed":
            print("Your reservation was successfully made. Thank you for booking with us.")
            break
        else:
            print("Unfortunately, your reservation could not be processed at this time.")
            break
    
    anything_else = input("Is there anything else I can help you with? (yes/no): ").lower()
    if anything_else in ['yes', 'y']:
        print("Please let us know how we can assist you further.")
    else:
        print("Thank you for using our service. Have a great day!")

if __name__ == "__main__":
    main()