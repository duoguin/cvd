import logging
import os
from collections import Counter
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Literal, Optional, Type
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

try:
    from pymongo import MongoClient
except ImportError:  # Tests inject an in-memory database without requiring pymongo.
    MongoClient = None


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, ".env"))

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(title="FlowAIssistant Backend API")

_database = None
_database_client = None


class DatabaseUnavailable(Exception):
    pass


class PostValidationStats:
    def __init__(self):
        self._lock = Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self.total = 0
            self.passed = 0
            self.failed = 0
            self.restarted = 0
            self.cleaned_up = 0
            self.by_workflow = Counter()
            self.invalid_fields = Counter()

    def record_success(self, workflow: str):
        with self._lock:
            self.total += 1
            self.passed += 1
            self.by_workflow[f"{workflow}.passed"] += 1

    def record_failure(
        self,
        workflow: str,
        invalid_fields: list[str],
        cleaned_up: bool,
    ):
        with self._lock:
            self.total += 1
            self.failed += 1
            self.restarted += 1
            self.cleaned_up += int(cleaned_up)
            self.by_workflow[f"{workflow}.failed"] += 1
            self.invalid_fields.update(invalid_fields)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "restarted": self.restarted,
                "cleaned_up": self.cleaned_up,
                "by_workflow": dict(self.by_workflow),
                "invalid_fields": dict(self.invalid_fields),
            }


post_validation_stats = PostValidationStats()


class AppointmentModel(BaseModel):
    model_config = ConfigDict(strict=True, str_strip_whitespace=True)


class ApartmentViewingRequest(AppointmentModel):
    ApplicationFeePaid: Literal["Yes", "No"]
    Day: Literal[
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
    ]
    Message: Optional[str] = ""
    Name: Literal[
        "One on Center Apartments", "Shadyside Apartments", "North Hill Apartments"
    ]
    RenterName: str = Field(min_length=1)
    RequestType: Literal["Check", "Book"]
    StartTimeHour: str = Field(pattern=r"^(1[0-2]|[1-9]) (am|pm)$")


class DoctorScheduleRequest(AppointmentModel):
    Day: Literal[
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
    ]
    Name: Literal["Dr. Johnson", "Dr. Morgan", "Dr. Alexis"]
    PatientName: str = Field(min_length=1)
    RequestType: Literal["Check", "Book"]
    StartTimeHour: str = Field(pattern=r"^(1[0-2]|[1-9]) (am|pm)$")
    Symptoms: str = Field(min_length=1)


def get_database():
    global _database, _database_client

    if _database is not None:
        return _database

    try:
        if MongoClient is None:
            raise RuntimeError("pymongo is not installed")
        uri = os.getenv("MONGODB_URI") or os.getenv("DB_URI", "mongodb://localhost:27017")
        timeout_ms = int(os.getenv("MONGODB_TIMEOUT_MS", "2000"))
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        client.admin.command("ping")
        _database_client = client
        _database = client[os.getenv("MONGODB_DB_NAME", "pdl")]
        logger.info("Connected to MongoDB database")
        return _database
    except Exception as exc:
        raise DatabaseUnavailable from exc


def database_error(exc: Exception) -> JSONResponse:
    logger.error("MongoDB operation failed: %s", type(exc).__name__)
    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "error_code": "DATABASE_UNAVAILABLE",
            "message": "Database is unavailable. Please retry later.",
            "restart_workflow": False,
        },
    )


@app.exception_handler(DatabaseUnavailable)
async def database_unavailable_handler(_request, exc: DatabaseUnavailable):
    return database_error(exc.__cause__ or exc)


def collection_for(database, collection_name: str):
    return database[collection_name]


def slot_query(req: AppointmentModel) -> dict[str, str]:
    return {
        "Name": req.Name,
        "Day": req.Day,
        "StartTimeHour": req.StartTimeHour,
        "RequestType": "Book",
    }


def validate_stored_record(
    record: Optional[dict[str, Any]],
    request_model: Type[AppointmentModel],
) -> list[str]:
    if record is None:
        return ["booking_id", "created_at", *request_model.model_fields.keys()]

    invalid_fields = []
    booking_id = record.get("booking_id")
    if not isinstance(booking_id, str) or not booking_id.strip():
        invalid_fields.append("booking_id")
    if not isinstance(record.get("created_at"), datetime):
        invalid_fields.append("created_at")

    stored_payload = {
        field_name: record.get(field_name)
        for field_name in request_model.model_fields
    }
    try:
        request_model.model_validate(stored_payload)
    except ValidationError as exc:
        invalid_fields.extend(str(error["loc"][0]) for error in exc.errors())
    return sorted(set(invalid_fields))


def delete_invalid_record(collection, booking_id: str) -> bool:
    try:
        result = collection.delete_one({"booking_id": booking_id})
        return result.deleted_count == 1
    except Exception as exc:
        logger.error("Could not clean up invalid booking: %s", type(exc).__name__)
        return False


def post_validation_failure(
    workflow: str,
    invalid_fields: list[str],
    cleaned_up: bool,
) -> JSONResponse:
    post_validation_stats.record_failure(workflow, invalid_fields, cleaned_up)
    logger.warning(
        "Post-validation failed workflow=%s invalid_fields=%s stats=%s",
        workflow,
        invalid_fields,
        post_validation_stats.snapshot(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "POST_VALIDATION_FAILED",
            "message": "Appointment information was not stored completely.",
            "missing_fields": invalid_fields,
            "restart_workflow": True,
        },
    )


def book_and_post_validate(
    collection,
    req: AppointmentModel,
    workflow: str,
) -> dict[str, Any] | JSONResponse:
    if collection.find_one(slot_query(req)):
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error_code": "APPOINTMENT_UNAVAILABLE",
                "message": "The requested appointment slot is unavailable.",
                "restart_workflow": False,
            },
        )

    booking = req.model_dump()
    booking["booking_id"] = str(uuid4())
    booking["created_at"] = datetime.now(timezone.utc)
    collection.insert_one(booking)

    stored_booking = collection.find_one({"booking_id": booking["booking_id"]})
    invalid_fields = validate_stored_record(stored_booking, type(req))
    if invalid_fields:
        cleaned_up = delete_invalid_record(collection, booking["booking_id"])
        return post_validation_failure(workflow, invalid_fields, cleaned_up)

    post_validation_stats.record_success(workflow)
    logger.info(
        "Post-validation passed workflow=%s stats=%s",
        workflow,
        post_validation_stats.snapshot(),
    )
    return stored_booking


def serialize_booking(booking: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.isoformat() if isinstance(value, datetime) else str(value) if key == "_id" else value
        for key, value in booking.items()
    }


def process_appointment_request(
    collection,
    req: AppointmentModel,
    workflow: str,
):
    try:
        if req.RequestType == "Check":
            return {
                "success": True,
                "status_code": 200,
                "data": {"available": collection.find_one(slot_query(req)) is None},
            }

        booking = book_and_post_validate(collection, req, workflow)
        if isinstance(booking, JSONResponse):
            return booking
        return {
            "success": True,
            "status_code": 200,
            "data": serialize_booking(booking),
        }
    except Exception as exc:
        return database_error(exc)


@app.get("/")
def read_root():
    return {"message": "FlowAIssistant Backend API is running."}


@app.get("/api/post-validation/stats")
def get_post_validation_stats():
    return {"success": True, "data": post_validation_stats.snapshot()}


@app.post("/api/book_apartment_viewing")
def book_apartment_viewing(
    req: ApartmentViewingRequest,
    database=Depends(get_database),
):
    return process_appointment_request(
        collection_for(database, "apartment_viewings"),
        req,
        workflow="book_apartment_viewing",
    )


@app.post("/api/doctor_schedule")
def doctor_schedule(
    req: DoctorScheduleRequest,
    database=Depends(get_database),
):
    return process_appointment_request(
        collection_for(database, "doctor_appointments"),
        req,
        workflow="doctor_schedule",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
