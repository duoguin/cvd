def plane_search_api(DepartureCity, ArrivalCity, Date, Price=None, ArrivalTime=None, Class=None, DurationHours=None, Airline=None, id=None):
    # This function is a placeholder for the actual API call.
    # It should be replaced with the actual API call to fetch flight details.
    # For demonstration, it returns a mock response.
    return {
        "DepartureCity": DepartureCity,
        "ArrivalCity": ArrivalCity,
        "Date": Date,
        "Price": 200,  # mock data
        "ArrivalTime": "6 pm",  # mock data
        "Class": "Economy",  # mock data
        "DurationHours": 5,  # mock data
        "Airline": "Delta",  # mock data
        "id": 12345  # mock data
    }

def get_user_input(prompt, valid_options=None):
    user_input = input(prompt)
    if valid_options and user_input not in valid_options:
        print("Invalid input. Please try again.")
        return get_user_input(prompt, valid_options)
    return user_input

def plane_search():
    print("Welcome to the Flight Search Bot!")
    user_name = get_user_input("Please enter your name: ")
    print(f"Hello, {user_name}!")
    
    while True:
        DepartureCity = get_user_input("From which city will you depart? ", ["Los Angeles", "San Francisco", "Chicago", "Detroit", "New York City", "Pittsburgh"])
        ArrivalCity = get_user_input("What's your destination city? ", ["Los Angeles", "San Francisco", "Chicago", "Detroit", "New York City", "Pittsburgh"])
        Date = get_user_input("Enter the date of your flight (e.g., '1st', '2nd'): ", [f"{i}st" if i == 1 else (f"{i}nd" if i == 2 else (f"{i}rd" if i == 3 else f"{i}th")) for i in range(1, 32)])
        
        # Optional preferences
        Price = get_user_input("Do you have a price limit? (Press Enter to skip) ")
        Price = int(Price) if Price.isdigit() else None
        Class = get_user_input("Preferred class? (First, Business, Economy, Press Enter to skip) ", ["First", "Business", "Economy", ""])
        Class = None if Class == "" else Class
        
        # Perform search
        flight_details = plane_search_api(DepartureCity, ArrivalCity, Date, Price, Class=Class)
        print("Here are the details of the flight found:")
        for key, value in flight_details.items():
            print(f"{key}: {value}")
        
        more_search = get_user_input("Do you want to search for more flights? (yes/no) ", ["yes", "no"])
        if more_search == "no":
            print("Thank you for using the Flight Search Bot. Goodbye!")
            break

if __name__ == "__main__":
    plane_search()