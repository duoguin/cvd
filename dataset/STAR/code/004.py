import requests

def query_doctor_appointment_api(doctor_name, patient_name):
    # Assuming there is a URL to the API endpoint
    api_url = "http://example.com/api/followup_doctor_appointment"
    data = {
        "Name": doctor_name,
        "PatientName": patient_name
    }
    
    # Sending a POST request to the API and returning the response
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"Message": "Failed to schedule an appointment. Please try again later."}

def followup_doctor_appointment():
    print("Welcome to the Follow-Up Doctor Appointment Scheduler.")
    
    # 1. Ask the user for their name
    patient_name = input("Please enter your name: ")
    
    # 2. Request the name of the doctor for the follow-up appointment
    doctor_name = input("Please enter the name of the doctor for the follow-up appointment: ")
    
    # Validating the doctor's name (Assuming the names are case sensitive)
    valid_doctors = ["Dr. Johnson", "Dr. Morgan", "Dr. Alexis"]
    if doctor_name not in valid_doctors:
        print("Invalid doctor name. Please enter a valid doctor name from the following list:")
        print(", ".join(valid_doctors))
        return
    
    # 3. Perform a query for the follow-up doctor appointment
    result = query_doctor_appointment_api(doctor_name, patient_name)
    
    # 4. Inform the user of the doctor's instructions based on the query result
    print(result.get("Message", "There was an error processing your request."))
    
    # 5. Check if the user needs more assistance with anything else
    more_help = input("Do you need assistance with anything else? (yes/no): ")
    if more_help.lower() == "yes":
        print("Please specify how we can assist you further.")
        # Additional assistance logic goes here
    else:
        print("Thank you for using our service. Have a great day!")

if __name__ == "__main__":
    followup_doctor_appointment()