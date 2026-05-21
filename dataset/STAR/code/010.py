class PartyPlannerBot:
    def __init__(self):
        self.venue = None
        self.name = None
        self.day = None
        self.start_time = None
        self.number_guests = 0
        self.food_request = ""
        self.drinks_request = ""

    def start_planning(self):
        self.ask_for_venue()
        self.ask_for_name()
        self.ask_for_day()
        self.ask_for_start_time()
        self.ask_for_number_guests()
        self.inform_food_and_drink_criteria()
        self.check_venue_availability()

    def ask_for_venue(self):
        self.venue = input("Please enter your preferred venue (Southside Venue, North Heights Venue, West Bay Venue): ")

    def ask_for_name(self):
        self.name = input("Please enter your name: ")

    def ask_for_day(self):
        self.day = input("Please specify the day you want to have the party (Sunday to Saturday): ")

    def ask_for_start_time(self):
        self.start_time = input("Please enter the starting time of the party (e.g., 6 pm): ")

    def ask_for_number_guests(self):
        self.number_guests = int(input("Please enter the number of guests you are expecting: "))

    def inform_food_and_drink_criteria(self):
        print("Please note that the food and drink criteria will be discussed after booking confirmation.")

    def check_venue_availability(self):
        available = self.call_party_plan_api("Check")
        if available:
            self.confirm_booking()
        else:
            print("Unfortunately, the venue is not available. Please try another venue or date.")

    def confirm_booking(self):
        confirm = input("The venue is available. Would you like to confirm the booking? (Yes/No): ")
        if confirm.lower() == 'yes':
            self.book_venue()
        else:
            print("Booking not confirmed. Let us know if there's anything else we can help with.")

    def book_venue(self):
        success = self.call_party_plan_api("Book")
        if success:
            print("Congratulations! Your booking was successful.")
        else:
            print("Unfortunately, the booking failed. Please try again later or contact support.")

    def call_party_plan_api(self, request_type):
        # Simulating an API call to 'party_plan' with the required parameters.
        # In a real scenario, this would involve making an HTTP request to the API endpoint.
        # Here we return True to simulate a successful operation.
        print(f"Simulating API call with RequestType: {request_type}, Venue: {self.venue}, Day: {self.day}, StartTime: {self.start_time}, HostName: {self.name}, NumberGuests: {self.number_guests}")
        return True

# Example usage
bot = PartyPlannerBot()
bot.start_planning()