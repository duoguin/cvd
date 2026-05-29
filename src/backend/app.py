import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pymongo
from dotenv import load_dotenv

# Load env variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path)

app = FastAPI(title="FlowAIssistant Backend API")

# Connect to MongoDB
db_uri = os.getenv("DB_URI", "mongodb://localhost:27017")
print(f"Connecting to MongoDB at: {db_uri}")
try:
    client = pymongo.MongoClient(db_uri, serverSelectionTimeoutMS=2000)
    # Check connection
    client.list_database_names()
    db = client["pdl"]
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Warning: Failed to connect to MongoDB: {e}")
    # Fallback/mock database if connection fails for robust startup
    class MockCollection:
        def __init__(self):
            self.data = []
        def find_one(self, query):
            for doc in self.data:
                if all(doc.get(k) == v for k, v in query.items()):
                    return doc
            return None
        def insert_one(self, doc):
            self.data.append(doc)
            return type('Result', (object,), {'inserted_id': len(self.data)})()
    class MockDb:
        def __init__(self):
            self.apartment_viewings = MockCollection()
            self.doctor_appointments = MockCollection()
    db = MockDb()

# Models
class ApartmentViewingRequest(BaseModel):
    ApplicationFeePaid: str
    Day: str
    Message: Optional[str] = ""
    Name: str  # Housing Company Name
    RenterName: str
    RequestType: str  # Check or Book
    StartTimeHour: str

class DoctorScheduleRequest(BaseModel):
    Day: str
    Name: str  # Doctor Name
    PatientName: str
    RequestType: str  # Check or Book
    StartTimeHour: str
    Symptoms: str

@app.get("/")
def read_root():
    return {"message": "FlowAIssistant Backend API is running successfully."}

@app.post("/api/book_apartment_viewing")
def book_apartment_viewing(req: ApartmentViewingRequest):
    print(f"Received book_apartment_viewing request: {req.dict()}")
    
    if req.RequestType == "Check":
        # Check if already booked
        query = {
            "Name": req.Name,
            "Day": req.Day,
            "StartTimeHour": req.StartTimeHour
        }
        existing = db.apartment_viewings.find_one(query)
        if existing:
            return {
                "status_code": 200,
                "data": "Viewing is unavailable"
            }
        else:
            return {
                "status_code": 200,
                "data": "Viewing is available"
            }
            
    elif req.RequestType == "Book":
        # Save to database
        booking = req.dict()
        booking["created_at"] = datetime.utcnow()
        db.apartment_viewings.insert_one(booking)
        return {
            "status_code": 200,
            "data": f"Booking was successful. Confirmed viewing for {req.RenterName} at {req.Name} on {req.Day} at {req.StartTimeHour}."
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid RequestType. Must be 'Check' or 'Book'.")

@app.post("/api/doctor_schedule")
def doctor_schedule(req: DoctorScheduleRequest):
    print(f"Received doctor_schedule request: {req.dict()}")
    
    if req.RequestType == "Check":
        # Check if doctor is already booked
        query = {
            "Name": req.Name,
            "Day": req.Day,
            "StartTimeHour": req.StartTimeHour
        }
        existing = db.doctor_appointments.find_one(query)
        if existing:
            return {
                "status_code": 200,
                "data": "Doctor is not available"
            }
        else:
            return {
                "status_code": 200,
                "data": "Doctor is available"
            }
            
    elif req.RequestType == "Book":
        # Save to database
        appointment = req.dict()
        appointment["created_at"] = datetime.utcnow()
        db.doctor_appointments.insert_one(appointment)
        return {
            "status_code": 200,
            "data": f"Booking was successful. Appointment with {req.Name} confirmed for {req.PatientName} on {req.Day} at {req.StartTimeHour}."
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid RequestType. Must be 'Check' or 'Book'.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
