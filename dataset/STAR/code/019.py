import requests

def spaceship_access_codes_system(user_rank, code_type, code, user_name):
    # Assuming there's an API endpoint to call
    endpoint = "https://api.spaceship.codes/verify"
    data = {
        "UserRank": user_rank,
        "CodeType": code_type,
        "Code": code,
        "UserName": user_name
    }
    response = requests.post(endpoint, json=data)
    if response.status_code == 200:
        return response.json()["Message"]
    else:
        return "There was an error processing your request."

def main():
    print("Welcome to the Spaceship Access Request System.")
    user_name = input("Please enter your name: ")
    user_rank = input("Please enter your rank within the spaceship hierarchy (Captain, First Officer, Chief Engineer, Bartender): ")
    access_code = input("Please enter your access code: ")
    code_type = input("What type of code are you providing? (Clearance, Access Code): ")
    
    # Call the spaceship access codes system to verify the provided information
    result_message = spaceship_access_codes_system(user_rank, code_type, access_code, user_name)
    
    # Inform the user of the outcome of their access request
    print(result_message)
    
    # Ask the user if they need assistance with anything else
    assistance_needed = input("Do you need assistance with anything else? (yes/no): ")
    if assistance_needed.lower() == "no":
        print("Thank you for using the Spaceship Access Request System. Goodbye!")
    else:
        print("Please specify how we can assist you further.")

if __name__ == "__main__":
    main()