"""
PulseCare AI - Intelligent Hospital Emergency & Clinical Resource Management
Database initialization, connection, indexes, and JSON Schema validators.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid, OperationFailure
import os
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "pulsecare_hospital_db")

def get_client():
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

def get_db():
    client = get_client()
    return client[DB_NAME]

# -------------------------------------------------------------
# MongoDB $jsonSchema Validation Rules
# These enforce structural and data-type integrity at database level
# -------------------------------------------------------------

PATIENT_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["patient_id", "name", "age", "gender", "triage_level", "admission_date", "status"],
        "properties": {
            "patient_id": {
                "bsonType": "string",
                "pattern": "^PAT-[0-9]{4}-[0-9]{4}$",
                "description": "Must be a string matching PAT-YYYY-XXXX and is required"
            },
            "name": {
                "bsonType": "string",
                "minLength": 2,
                "maxLength": 100,
                "description": "Patient full name is required (2-100 characters)"
            },
            "age": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 125,
                "description": "Age must be an integer between 0 and 125"
            },
            "gender": {
                "enum": ["Male", "Female", "Other"],
                "description": "Gender must be Male, Female, or Other"
            },
            "blood_group": {
                "enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"],
                "description": "Valid ABO/Rh blood group"
            },
            "triage_level": {
                "enum": [
                    "Level 1 - Resuscitation",
                    "Level 2 - Emergent",
                    "Level 3 - Urgent",
                    "Level 4 - Less Urgent",
                    "Level 5 - Non-Urgent"
                ],
                "description": "Valid emergency triage category"
            },
            "status": {
                "enum": ["Triage", "Admitted", "ICU", "Under Observation", "Discharged", "Transferred"],
                "description": "Current clinical encounter status"
            },
            "admission_date": {
                "bsonType": "date",
                "description": "Date and time of patient admission"
            },
            "contact": {
                "bsonType": "object",
                "required": ["phone"],
                "properties": {
                    "phone": {
                        "bsonType": "string",
                        "description": "Valid phone contact"
                    },
                    "emergency_contact": {
                        "bsonType": "string"
                    }
                }
            },
            "vitals_history": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["recorded_at", "heart_rate", "spo2", "temperature"],
                    "properties": {
                        "recorded_at": {"bsonType": "date"},
                        "heart_rate": {
                            "bsonType": "int",
                            "minimum": 30,
                            "maximum": 250,
                            "description": "Heart rate in bpm (30-250)"
                        },
                        "spo2": {
                            "bsonType": "int",
                            "minimum": 40,
                            "maximum": 100,
                            "description": "Oxygen saturation (40-100%)"
                        },
                        "temperature": {
                            "bsonType": ["double", "int"],
                            "minimum": 90.0,
                            "maximum": 110.0,
                            "description": "Body temperature in Fahrenheit (90.0 - 110.0)"
                        },
                        "systolic": {"bsonType": "int"},
                        "diastolic": {"bsonType": "int"},
                        "blood_pressure": {"bsonType": "string"}
                    }
                }
            }
        }
    }
}

DOCTOR_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["doctor_id", "name", "specialization", "on_duty"],
        "properties": {
            "doctor_id": {
                "bsonType": "string",
                "pattern": "^DOC-[0-9]{3}$",
                "description": "Doctor ID must match DOC-XXX"
            },
            "name": {"bsonType": "string", "minLength": 3},
            "specialization": {
                "enum": [
                    "Emergency Medicine",
                    "Cardiology",
                    "Neurology",
                    "General Surgery",
                    "Pediatrics",
                    "Pulmonology",
                    "Critical Care"
                ]
            },
            "on_duty": {"bsonType": "bool"},
            "shift": {"enum": ["Morning", "Evening", "Night"]},
            "room_number": {"bsonType": "string"},
            "max_active_patients": {"bsonType": "int", "minimum": 1, "maximum": 50}
        }
    }
}

WARD_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["ward_code", "name", "ward_type", "total_beds", "occupied_beds"],
        "properties": {
            "ward_code": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "ward_type": {"enum": ["ICU", "Emergency", "Trauma", "General", "Cardiology", "Pediatric"]},
            "total_beds": {"bsonType": "int", "minimum": 1},
            "occupied_beds": {"bsonType": "int", "minimum": 0},
            "floor": {"bsonType": "int"},
            "ventilators_available": {"bsonType": "int", "minimum": 0}
        }
    }
}

def init_database(drop_existing=False):
    """
    Creates collections with strict MongoDB $jsonSchema validators and performance indexes.
    """
    db = get_db()
    if drop_existing:
        db.patients.drop()
        db.doctors.drop()
        db.wards.drop()
        print("Dropped existing collections in pulsecare_hospital_db.")

    existing_collections = db.list_collection_names()

    # 1. Patients collection with validator
    if "patients" not in existing_collections:
        db.create_collection("patients", validator=PATIENT_VALIDATOR)
        print("Created 'patients' collection with $jsonSchema validation.")
    else:
        try:
            db.command({
                "collMod": "patients",
                "validator": PATIENT_VALIDATOR,
                "validationLevel": "moderate"
            })
            print("Updated 'patients' validator successfully.")
        except OperationFailure as e:
            print(f"Warning updating patient validator: {e}")

    # 2. Doctors collection with validator
    if "doctors" not in existing_collections:
        db.create_collection("doctors", validator=DOCTOR_VALIDATOR)
        print("Created 'doctors' collection with $jsonSchema validation.")
    else:
        try:
            db.command({
                "collMod": "doctors",
                "validator": DOCTOR_VALIDATOR,
                "validationLevel": "moderate"
            })
        except OperationFailure:
            pass

    # 3. Wards collection with validator
    if "wards" not in existing_collections:
        db.create_collection("wards", validator=WARD_VALIDATOR)
        print("Created 'wards' collection with $jsonSchema validation.")
    else:
        try:
            db.command({
                "collMod": "wards",
                "validator": WARD_VALIDATOR,
                "validationLevel": "moderate"
            })
        except OperationFailure:
            pass

    # 4. Indexes for query optimization
    # Patient indexes
    db.patients.create_index([("patient_id", ASCENDING)], unique=True)
    db.patients.create_index([("triage_level", ASCENDING)])
    db.patients.create_index([("status", ASCENDING)])
    db.patients.create_index([("assigned_doctor_id", ASCENDING), ("status", ASCENDING)])
    db.patients.create_index([("admission_date", DESCENDING)])
    db.patients.create_index([("name", "text"), ("primary_complaint", "text")])

    # Doctor indexes
    db.doctors.create_index([("doctor_id", ASCENDING)], unique=True)
    db.doctors.create_index([("specialization", ASCENDING)])
    db.doctors.create_index([("on_duty", ASCENDING)])

    # Ward indexes
    db.wards.create_index([("ward_code", ASCENDING)], unique=True)
    db.wards.create_index([("ward_type", ASCENDING)])

    print("Created database indexes successfully.")
    return True

def serialize_mongo(obj):
    """
    Converts MongoDB documents containing ObjectId, datetime, etc., into JSON-serializable dicts.
    """
    if isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]
    elif isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if isinstance(v, ObjectId):
                new_dict[k] = str(v)
            elif isinstance(v, datetime):
                new_dict[k] = v.isoformat()
            elif isinstance(v, (dict, list)):
                new_dict[k] = serialize_mongo(v)
            else:
                new_dict[k] = v
        return new_dict
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj
