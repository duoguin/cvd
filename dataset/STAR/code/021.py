import json

def get_user_input(prompt):
    return input(prompt)

def trip_directions_api(travel_mode, departure_time, departure_location, arrival_location):
    # This function is a placeholder for calling the actual API.
    # It should be replaced with the actual API call code.
    # For demonstration, it returns a mocked response.
    return {
        "TravelMode": travel_mode,
        "DepartureTime": departure_time,
        "TransitInstructions": ["Take bus 20 from A to B", "Switch to subway 5 from B to C"],
        "DrivingInstructions": ["Drive through Main St.", "Turn left on 2nd Ave."],
        "WalkingInstructions": ["Walk to the end of the road", "Turn right into the park"],
        "Price": 2.5
    }

def main():
    print("Welcome to the Trip Directions Assistant!")
    
    travel_mode = get_user_input("What is your preferred mode of travel? (Transit/Driving/Walking): ")
    departure_location = get_user_input("What is your departure location?: ")
    arrival_location = get_user_input("What is your arrival location?: ")
    departure_time = get_user_input("What is your preferred departure time? (e.g., 9 am, 5 pm): ")
    
    directions = trip_directions_api(travel_mode, departure_time, departure_location, arrival_location)
    
    if travel_mode.lower() == "transit":
        print(f"The first step of your trip is: {directions['TransitInstructions'][0]}")
    elif travel_mode.lower() == "driving":
        print(f"The first step of your trip is: {directions['DrivingInstructions'][0]}")
    elif travel_mode.lower() == "walking":
        print(f"The first step of your trip is: {directions['WalkingInstructions'][0]}")
    
    more_details = get_user_input("Do you want more detailed instructions? (yes/no): ")
    if more_details.lower() == "yes":
        if travel_mode.lower() == "transit":
            for step in directions["TransitInstructions"]:
                print(step)
        elif travel_mode.lower() == "driving":
            for step in directions["DrivingInstructions"]:
                print(step)
        elif travel_mode.lower() == "walking":
            for step in directions["WalkingInstructions"]:
                print(step)
    
    done = get_user_input("Are you done with the trip instructions? (yes/no): ")
    if done.lower() == "yes":
        print("Thank you for using the Trip Directions Assistant. Have a safe trip!")
    
    else_help = get_user_input("Is there anything else I can help you with? (yes/no): ")
    if else_help.lower() == "yes":
        print("Please describe what you need help with:")
        # Implement further assistance logic here
    else:
        print("Thank you for using our service. Goodbye!")

if __name__ == "__main__":
    main()