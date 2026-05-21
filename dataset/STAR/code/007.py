import json

def sample_hotel_data(name=None, cost=None, takes_reservations=None, service=None, average_rating=None, location=None):
    # This function is a placeholder for the actual API call.
    # In a real scenario, this would make a request to the external API.
    # Here, we just return a sample response.
    return [
        {"Name": "Shadyside Inn", "Cost": "Moderate", "TakesReservations": True, "Service": True, "AverageRating": 4, "Location": "East"},
        {"Name": "Hilton Hotel", "Cost": "Expensive", "TakesReservations": True, "Service": True, "AverageRating": 5, "Location": "Center"}
        # Add more sample data as needed
    ]

def get_search_criteria():
    # Ask the user for search criteria. This is a simplified example.
    print("Please enter your search criteria for hotels. Leave blank if no preference.")
    name = input("Hotel Name (Shadyside Inn, Hilton Hotel, Hyatt Hotel, Old Town Inn): ")
    cost = input("Cost (Cheap, Moderate, Expensive): ")
    takes_reservations = input("Takes Reservations (True/False): ")
    service = input("Service (True/False): ")
    average_rating = input("Average Rating (1-5): ")
    location = input("Location (South, West, East, North, Center): ")
    
    # Convert inputs to appropriate types
    if takes_reservations.lower() in ['true', 'false']:
        takes_reservations = takes_reservations.lower() == 'true'
    else:
        takes_reservations = None
    
    if service.lower() in ['true', 'false']:
        service = service.lower() == 'true'
    else:
        service = None
    
    try:
        average_rating = int(average_rating) if average_rating else None
    except ValueError:
        average_rating = None

    return {
        "name": name if name else None,
        "cost": cost if cost else None,
        "takes_reservations": takes_reservations,
        "service": service,
        "average_rating": average_rating,
        "location": location if location else None
    }

def search_hotels():
    while True:
        criteria = get_search_criteria()
        results = sample_hotel_data(**criteria)
        
        if results:
            print("\nFound matching hotels:")
            for hotel in results:
                print(json.dumps(hotel, indent=2))
        else:
            print("No hotels found matching your criteria.")
        
        another_search = input("\nDo you want to search for more hotels? (yes/no): ")
        if another_search.lower() != 'yes':
            print("Thank you for using our hotel search. Goodbye!")
            break

if __name__ == "__main__":
    print("Welcome to the Hotel Search Bot!")
    search_hotels()