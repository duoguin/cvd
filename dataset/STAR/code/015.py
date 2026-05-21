def ask_user_for_criteria():
    print("Please provide search criteria for the restaurant search.")
    name = input("Enter restaurant name (optional): ")
    cost = input("Enter cost (Cheap, Moderate, Expensive, or leave blank): ")
    takes_reservations = input("Takes reservations? (yes/no, or leave blank): ")
    does_delivery = input("Does delivery? (yes/no, or leave blank): ")
    food = input("Enter food type (e.g., Pizza, Chinese, or leave blank): ")
    location = input("Enter location (South, West, East, North, Center, or leave blank): ")

    # Convert user inputs to appropriate types
    criteria = {
        "Name": name if name else None,
        "Cost": cost if cost in ["Cheap", "Moderate", "Expensive"] else None,
        "TakesReservations": True if takes_reservations.lower() == 'yes' else False if takes_reservations.lower() == 'no' else None,
        "DoesDelivery": True if does_delivery.lower() == 'yes' else False if does_delivery.lower() == 'no' else None,
        "Food": food if food else None,
        "Location": location if location in ["South", "West", "East", "North", "Center"] else None,
    }
    return {k: v for k, v in criteria.items() if v is not None}

def search_restaurants(criteria):
    # Placeholder for API call
    # This function should implement the actual API call to the 'generic_sample' API with the given criteria
    # For demonstration, it returns a list of dummy restaurants
    return [
        {"Name": "Cactus Club", "Cost": "Moderate", "Food": "Steak", "Location": "West"}
    ]

def main():
    continue_search = True

    while continue_search:
        criteria = ask_user_for_criteria()
        results = search_restaurants(criteria)

        if results:
            print("Search Results:")
            for result in results:
                print(f"Name: {result['Name']}, Cost: {result['Cost']}, Food: {result['Food']}, Location: {result['Location']}")
        else:
            print("No matching restaurants found.")

        user_decision = input("Do you want to continue searching for restaurants? (yes/no): ")
        if user_decision.lower() != 'yes':
            continue_search = False

    print("Thank you for using our restaurant search. Goodbye!")

if __name__ == "__main__":
    main()