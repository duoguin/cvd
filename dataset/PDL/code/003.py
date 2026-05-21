import requests

class DHLServicePointInquiryBot:
    def __init__(self):
        self.api_base_url = "https://api.dhl.com"  # Replace with the actual base URL of the API

    def get_service_point_city_list(self):
        response = requests.get(f"{self.api_base_url}/service_point_cities")
        if response.status_code == 200:
            return response.json().get('service_point_cities', [])
        else:
            return []

    def validate_service_point_city(self, city):
        response = requests.post(f"{self.api_base_url}/validate_service_point_city", json={"city": city})
        if response.status_code == 200:
            return response.json().get('errcode', 500) == 200
        else:
            return False

    def get_service_points(self, city):
        response = requests.post(f"{self.api_base_url}/get_service_points", json={"city": city})
        if response.status_code == 200:
            data = response.json()
            if data.get('errcode', 500) == 200:
                return data.get('service_points', [])
            else:
                return None
        else:
            return None

    def handle_inquiry(self, city):
        # Step 1: Get the list of service point cities
        service_point_cities = self.get_service_point_city_list()
        
        # Step 2: Verify if the city provided by the user is in the supported list
        if city in service_point_cities:
            # Step 3: Call the API to get the service point information for that city
            service_points = self.get_service_points(city)
            
            # Step 4: Provide feedback to the user
            if service_points is not None:
                # Successful retrieval of service point information
                return {
                    "status": "success",
                    "service_points": service_points
                }
            else:
                # Unsuccessful retrieval, inform the user
                return {
                    "status": "error",
                    "message": "No service point information is currently available for this city. Please try querying nearby cities."
                }
        else:
            # City is not in the supported list
            return {
                "status": "error",
                "message": "The city you provided is not supported. Please choose a correct service point city. For more information, visit our self-service query links for PC and mobile.",
                "self_service_links": {
                    "PC": "https://www.dhl.com/self_service_pc",
                    "mobile": "https://www.dhl.com/self_service_mobile"
                }
            }

# Example usage:
bot = DHLServicePointInquiryBot()
city = "Berlin"
result = bot.handle_inquiry(city)
print(result)