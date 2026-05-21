import random

def hotel_reserve_api(name, start_date, end_date, customer_name, customer_request, request_type):
    # This is a mock function to simulate the hotel reservation API.
    # In a real scenario, this would involve sending a request to an actual API endpoint.
    # For demonstration, this function will randomly return a success or failure message.
    return {"Message": random.choice(["Reservation Successful", "Reservation Failed"])}

def hotel_reservation_process():
    print("Welcome to the Hotel Reservation Service!")
    customer_name = input("Please enter your name: ")
    hotel_name = input("Please choose a hotel (Shadyside Inn, Hilton Hotel, Hyatt Hotel, Old Town Inn): ")
    check_in_date = input("Please enter your check-in date (1st - 31st): ")
    check_out_date = input("Please enter your check-out date (1st - 31st): ")
    customer_request = input("Please enter any specific requests for your stay (optional): ")
    
    # Check availability
    availability_response = hotel_reserve_api(hotel_name, check_in_date, check_out_date, customer_name, customer_request, "Check")
    
    if "available" in availability_response.get("Message", "").lower():
        confirm_booking = input("The hotel is available. Would you like to confirm your booking? (yes/no): ")
        
        if confirm_booking.lower() == "yes":
            booking_response = hotel_reserve_api(hotel_name, check_in_date, check_out_date, customer_name, customer_request, "Book")
            
            if "successful" in booking_response.get("Message", "").lower():
                print("Your reservation has been successfully made.")
            else:
                print("Sorry, your reservation could not be completed. Please try again later.")
        else:
            print("Please choose a different hotel or modify your dates.")
            hotel_reservation_process()  # Restart the process for a new choice
    else:
        print("Unfortunately, the hotel is unavailable for the chosen dates. Please choose a different hotel or modify your dates.")
        hotel_reservation_process()  # Restart the process for a new choice
    
    # Ask if the user needs assistance with anything else
    assistance = input("Do you need assistance with anything else? (yes/no): ")
    if assistance.lower() == "yes":
        print("Please specify how we can assist you further.")
    else:
        print("Thank you for using our service. Have a great day!")

if __name__ == "__main__":
    hotel_reservation_process()