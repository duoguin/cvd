def doctor_schedule(name, day, start_time_hour, patient_name, symptoms, request_type):
    """
    Mock function to simulate checking or booking an appointment with a doctor.
    """
    # For simplicity, let's assume all doctors are available at all times in this mock function.
    # In a real scenario, this would involve API calls to check the doctor's availability.
    if request_type == "Check":
        return {"Message": f"{name} is available on {day} at {start_time_hour}."}
    elif request_type == "Book":
        return {"Message": f"Appointment booked with {name} on {day} at {start_time_hour} for {patient_name}."}
    else:
        return {"Message": "Invalid request type."}

def book_doctor_appointment():
    while True:
        patient_name = input("Please enter your name: ")
        doctor_name = input("Please specify the doctor's name you wish to book an appointment with: ")
        day = input("Please enter the day you prefer for the appointment: ")
        start_time = input("Please enter the preferred start time of the appointment: ")
        symptoms = input("Please describe your symptoms: ")

        # Check the doctor's availability
        check_response = doctor_schedule(doctor_name, day, start_time, patient_name, symptoms, "Check")
        print(check_response["Message"])

        confirmation = input("Do you want to proceed with booking? (yes/no): ").lower()
        if confirmation == "yes":
            book_response = doctor_schedule(doctor_name, day, start_time, patient_name, symptoms, "Book")
            print(book_response["Message"])
            break
        elif confirmation == "no":
            continue
        else:
            print("Invalid response. Please try again.")
            continue

        anything_else = input("Is there anything else you need assistance with? (yes/no): ").lower()
        if anything_else == "no":
            print("Thank you for using our service. Have a great day!")
            break

if __name__ == "__main__":
    book_doctor_appointment()