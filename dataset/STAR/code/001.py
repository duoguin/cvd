import random

def generic_sample_api(level=None, max_level=None, has_balcony=None, balcony_side=None, has_elevator=None, num_rooms=None, floor_square_meters=None, nearby_pois=None, name=None, price=None):
    # This is a mock function to simulate the API call.
    # In a real scenario, this function would make an HTTP request to the actual API endpoint.
    # Here, we'll just return a sample response based on the input parameters.
    sample_response = [
        {"Level": 2, "MaxLevel": 10, "HasBalcony": True, "BalconySide": "south", "HasElevator": True, "NumRooms": 3, "FloorSquareMeters": 120, "Price": 1500, "NearbyPOIs": ["Park", "University"], "Name": "Shadyside Apartments"},
        {"Level": 5, "MaxLevel": 15, "HasBalcony": False, "BalconySide": None, "HasElevator": True, "NumRooms": 2, "FloorSquareMeters": 90, "Price": 1200, "NearbyPOIs": ["TrainStation", "Museum"], "Name": "North Hill Apartments"}
    ]
    # For simplicity, return a random choice from the sample response
    return random.choice(sample_response)

def get_search_criteria():
    # Ask the user for search criteria. This is simplified for demonstration.
    # In a real scenario, you would validate the input and ask for each parameter specifically.
    print("Please provide your search criteria for the apartment (This is a simplified example).")
    # Example criteria, in a real scenario, collect actual user input
    criteria = {"num_rooms": 2}
    return criteria

def search_apartments():
    while True:
        criteria = get_search_criteria()
        results = generic_sample_api(num_rooms=criteria.get("num_rooms"))
        
        if results:
            print("We found an apartment matching your criteria:", results)
        else:
            print("No results found based on your criteria.")
        
        user_decision = input("Do you want to conduct another search? (yes/no): ")
        if user_decision.lower() != "yes":
            print("Thank you for using our apartment search. Goodbye!")
            break

if __name__ == "__main__":
    search_apartments()