def book_apartment_viewing():
    print("Welcome to the Apartment Viewing Booking System!")
    
    # Step 1: Ask for the user's name
    renter_name = input("Please enter your name: ")
    
    # Step 2: Request the name of the apartment
    print("Available apartments for viewing are: One on Center Apartments, Shadyside Apartments, North Hill Apartments")
    apartment_name = input("Which apartment are you interested in? ")
    
    # Step 3: Ask for the day of viewing
    print("Available days are: Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday")
    day = input("On which day would you like to view the apartment? ")
    
    # Step 4: Ask for the start time of the viewing
    print("Available start times are every hour from 12 am to 11 pm.")
    start_time_hour = input("At what time would you like your viewing to start? (e.g., 2 pm) ")
    
    # Step 5: Inquire if the application fee has been paid
    application_fee_paid = input("Have you paid the application fee? (Yes/No) ")
    
    # Step 6: Request any custom message the user might want to add
    custom_message = input("Do you have any special requests or additional messages? (If none, just press Enter) ")
    
    # Step 7: Check the availability for the requested viewing
    availability = check_availability(apartment_name, day, start_time_hour, renter_name, application_fee_paid, custom_message)
    
    # Step 8: If the viewing is available, inform the user and ask if they want to proceed with booking
    if availability == "Available":
        proceed = input("The viewing is available. Would you like to proceed with booking? (Yes/No) ")
        
        # Step 9: If the user says yes, book the viewing
        if proceed.lower() == "yes":
            booking_status = book_viewing(apartment_name, day, start_time_hour, renter_name, application_fee_paid, custom_message)
            print(booking_status)
        # Step 10: If the user says no, ask again for the apartment name to modify search criteria
        else:
            print("Let's try modifying your search criteria.")
            return book_apartment_viewing()
    
    # Step 11: If the viewing is not available, inform the user
    else:
        print("Unfortunately, the viewing is not available. Please try another time or apartment.")
    
    # Step 12: Finally, ask if there's anything else the user needs assistance with
    additional_assistance = input("Is there anything else you need assistance with? (Yes/No) ")
    if additional_assistance.lower() == "yes":
        return book_apartment_viewing()
    else:
        print("Thank you for using the Apartment Viewing Booking System. Have a great day!")

def check_availability(apartment_name, day, start_time_hour, renter_name, application_fee_paid, custom_message):
    # This function simulates checking availability. In a real application, this would call an API.
    # For the sake of this example, let's assume everything is always available.
    return "Available"

def book_viewing(apartment_name, day, start_time_hour, renter_name, application_fee_paid, custom_message):
    # This function simulates booking a viewing. In a real application, this would call an API.
    # For the sake of this example, let's assume the booking is always successful.
    return "Your viewing has been successfully booked!"

# Start the process
book_apartment_viewing()