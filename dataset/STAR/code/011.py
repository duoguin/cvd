class PartyRSVPBot:
    def __init__(self):
        self.api_url = "http://example.com/party_rsvp"  # Placeholder API URL

    def ask_question(self, prompt):
        return input(prompt)

    def call_party_rsvp_api(self, data):
        # Simulate calling the party RSVP API and getting a response
        # In a real scenario, you would make an HTTP request here
        print("Calling the Party RSVP API with the following data:")
        for key, value in data.items():
            print(f"{key}: {value}")
        # Simulate API response
        return {"Message": "RSVP confirmed. Thank you!"}

    def process_rsvp(self):
        print("Welcome to the Party RSVP Bot!")
        guest_name = self.ask_question("What is your name? ")
        venue = self.ask_question("What is the venue of the party? (Southside Venue, North Heights Venue, West Bay Venue) ")
        host_name = self.ask_question("Who is hosting the party? ")
        arrival_time = self.ask_question("What is your planned arrival time? (e.g., 7 pm) ")
        number_guests = int(self.ask_question("How many guests will you bring? "))
        need_parking = self.ask_question("Do you need parking? (Yes/No) ")
        dietary_restrictions = self.ask_question("Do you or your guests have any dietary restrictions? ")

        rsvp_data = {
            "GuestName": guest_name,
            "Name": venue,
            "HostName": host_name,
            "ArrivalTime": arrival_time,
            "NumberGuests": number_guests,
            "NeedParking": need_parking,
            "DietaryRestrictions": dietary_restrictions
        }

        response = self.call_party_rsvp_api(rsvp_data)
        print(response["Message"])  # Display the message from the API response

        additional_needs = self.ask_question("Is there anything else you need? ")
        if additional_needs.lower() != "no":
            print("Thank you for sharing. We will try to accommodate your needs.")
        else:
            print("Great! We look forward to seeing you at the party.")

if __name__ == "__main__":
    bot = PartyRSVPBot()
    bot.process_rsvp()