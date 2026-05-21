import random

def restaurant_reserve_api(name, time, party_size, customer_name, request_type):
    # Simulation of an API call to reserve a table.
    # In a real scenario, this would involve network communication with a restaurant's reservation system.
    # Here, we'll simulate success or failure randomly for simplicity.
    success = random.choice([True, False])
    return {"ReservationStatus": "Success" if success else "Failed"}

def start_reservation_process():
    print("Welcome to the Restaurant Reservation Bot!")
    customer_name = input("Please enter your name: ")
    
    while True:
        restaurant_name = input("Which restaurant would you like to reserve a table at? ")
        reservation_time = input("What time would you like to make the reservation for? ")
        party_size = int(input("How many people are in your party? "))
        
        # Check table availability
        check_response = restaurant_reserve_api(restaurant_name, reservation_time, party_size, customer_name, "Check")
        
        if check_response["ReservationStatus"] == "Success":
            confirmation = input("A table is available. Would you like to book it? (yes/no): ")
            
            if confirmation.lower() == "yes":
                book_response = restaurant_reserve_api(restaurant_name, reservation_time, party_size, customer_name, "Book")
                
                if book_response["ReservationStatus"] == "Success":
                    print("Your booking was successful!")
                    break
                else:
                    print("Unfortunately, the booking could not be completed. Please try again.")
            else:
                print("Booking not confirmed. Let's try another restaurant or time.")
        else:
            print("Sorry, no table is available at that time. Please try another restaurant or time.")
        
        another_attempt = input("Would you like to try again? (yes/no): ")
        if another_attempt.lower() != "yes":
            break
    
    print("Thank you for using the Restaurant Reservation Bot. Have a great day!")

if __name__ == "__main__":
    start_reservation_process()