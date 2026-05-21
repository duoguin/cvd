def check_hospital(hospital_name: str) -> bool:
    """Check if a hospital exists in the system."""

def check_department(hospital_name: str, department_name: str) -> bool:
    """Check if a specific department exists within a given hospital."""

def query_appointment(hospital_name: str, department_name: str, time: str) -> dict:
    """Query available appointment slots for a specific department and time."""

def create_appointment(patient_id: str, hospital_name: str, department_name: str, time: str) -> int:
    """Schedule a new medical appointment."""

def recommend_other_hospitals(department_name: str, time: str) -> dict:
    """Search for available slots at other hospitals for the specified department and time when the preferred hospital doesn't have available slots."""


""" 
Given the following function signatures, figure out their dependencies. 
## Output Format
preconditions:
    function1: [function2]

{{few-shot examples}}

### Function Signatures
{{function_signatures}}
"""

""" 
preconditions:
    check_hospital: []
    check_department: [check_hospital]
    query_appointment: [check_hospital, check_department]
    create_appointment: [query_appointment]
    recommend_other_hospitals: [query_appointment]
"""

def SearchOnewayFlight(airlines: str, departure_date: str, destination_city: str, origin_city: str, passengers: str, refundable: str, seating_class: str) -> dict:
    """Search for one-way flights to a destination"""
def SearchRoundtripFlights(airlines: str, departure_date: str, destination_city: str, origin_city: str, passengers: str, refundable: str, return_date: str, seating_class: str) -> dict:
    """Search for round-trip flights to a destination"""
def ReserveOnewayFlight(airlines: str, departure_date: str, destination_city: str, origin_city: str, passengers: str, refundable: str, seating_class: str) -> dict:
    """Reserve a one-way flight"""
def ReserveRoundtripFlights(airlines: str, departure_date: str, destination_city: str, origin_city: str, passengers: str, refundable: str, return_date: str, seating_class: str) -> dict:
    """Reserve a round-trip flight"""

"""
preconditions:
    ReserveOnewayFlight: [SearchOnewayFlight]
    ReserveRoundtripFlights: [SearchRoundtripFlights]
"""