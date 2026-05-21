def meeting_schedule(name, day, start_time_hour, end_time_hour, user_name, meeting_reason=None):
    # This is a placeholder for the actual API call.
    # Assume it returns a success message or an error based on availability.
    # For demonstration purposes, let's assume all scheduling attempts are successful.
    return {"Message": "Meeting successfully scheduled."}

def ask_user_for_input(prompt):
    return input(prompt)

def schedule_meeting():
    user_name = ask_user_for_input("What is your name? ")
    guest_name = ask_user_for_input("Enter the name of the guest you want to invite: ")
    while True:
        day = ask_user_for_input("Specify the day for the meeting: ")
        start_time = ask_user_for_input("Enter the start time of the meeting: ")
        end_time = ask_user_for_input("Enter the end time of the meeting: ")
        meeting_reason = ask_user_for_input("Provide a reason for the meeting: ")

        # Attempt to schedule the meeting
        response = meeting_schedule(guest_name, day, start_time, end_time, user_name, meeting_reason)
        print(response["Message"])

        if response["Message"] == "Meeting successfully scheduled.":
            print("Your meeting has been confirmed.")
            break
        else:
            print("The requested time is unavailable.")
            try_again = ask_user_for_input("Do you want to choose a different time? (yes/no) ")
            if try_again.lower() != 'yes':
                print("Goodbye.")
                break

    anything_else = ask_user_for_input("Is there anything else you need help with? (yes/no) ")
    if anything_else.lower() == 'yes':
        print("Please specify what you need help with.")
    else:
        print("Goodbye.")

if __name__ == "__main__":
    schedule_meeting()