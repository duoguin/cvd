def collect_user_input():
    user_info = {
        "FullName": input("Please enter your name: "),
        "AccountNumber": input("Please enter your bank account number: "),
        "PIN": input("Please enter your PIN: "),
    }

    # Check if AccountNumber or PIN is missing
    if not user_info["AccountNumber"] or not user_info["PIN"]:
        user_info["DateOfBirth"] = input("Please enter your date of birth: ")
        user_info["SecurityAnswer1"] = input("Please enter your mother's maiden name: ")
        user_info["SecurityAnswer2"] = input("Please enter your childhood pet's name: ")

    return user_info

def submit_fraud_report(user_info):
    # Assuming there's a function available to submit the fraud report to the bank API
    # This function is a placeholder to represent the process of submitting the report
    print("Attempting to submit your fraud report...")
    # Here, you would normally call the actual bank_fraud_report API with the user_info
    # For demonstration, we'll simulate a successful submission
    submission_successful = True  # This should be the result from the API call
    return submission_successful

def main():
    print("Welcome to the Bank Fraud Report Assistant")
    user_info = collect_user_input()

    # Check if essential information is missing after collecting additional info
    if not user_info["AccountNumber"] or not user_info["PIN"]:
        print("Authentication cannot be completed due to missing information.")
        return

    # Ask for details regarding the fraud
    user_info["FraudReport"] = input("Please provide details regarding the fraud: ")

    # Attempt to submit the fraud report
    submission_successful = submit_fraud_report(user_info)

    if submission_successful:
        print("Your fraud report has been submitted successfully.")
    else:
        print("There was an issue submitting your fraud report. Authentication cannot be completed.")

    print("Thank you for using the Bank Fraud Report Assistant. Goodbye.")

if __name__ == "__main__":
    main()