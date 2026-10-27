"""
PulseCare AI - CRUD Operations with PyMongo
Implements Create, Read, Update, Delete with schema validation handling,
query execution metadata, and atomic array & counter updates ($push, $inc, $set).
"""

from datetime import datetime, timezone
from bson import ObjectId
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError
from db import get_db, serialize_mongo

def get_all_patients(query=None, limit=50, sort_by="admission_date", sort_dir=-1):
    """
    Read: Retrieves patients with optional filter criteria, text search, and sorting.
    """
    db = get_db()
    mongo_filter = {}
    
    if query:
        # Search text
        if "search" in query and query["search"]:
            term = query["search"].strip()
            mongo_filter["$or"] = [
                {"name": {"$regex": term, "$options": "i"}},
                {"patient_id": {"$regex": term, "$options": "i"}},
                {"primary_complaint": {"$regex": term, "$options": "i"}}
            ]
        
        # Triage level filter
        if "triage_level" in query and query["triage_level"]:
            mongo_filter["triage_level"] = query["triage_level"]

        # Status filter
        if "status" in query and query["status"]:
            mongo_filter["status"] = query["status"]

        # Blood group
        if "blood_group" in query and query["blood_group"]:
            mongo_filter["blood_group"] = query["blood_group"]

    cursor = db.patients.find(mongo_filter).sort(sort_by, sort_dir).limit(limit)
    patients = list(cursor)
    return serialize_mongo(patients), mongo_filter

def get_patient_details(patient_id):
    """
    Read: Retrieves a single patient by patient_id with doctor and ward dereferencing.
    """
    db = get_db()
    pipeline = [
        {"$match": {"patient_id": patient_id}},
        {
            "$lookup": {
                "from": "doctors",
                "localField": "assigned_doctor_id",
                "foreignField": "_id",
                "as": "doctor_details"
            }
        },
        {
            "$lookup": {
                "from": "wards",
                "localField": "assigned_ward.ward_id",
                "foreignField": "_id",
                "as": "ward_details"
            }
        },
        {
            "$unwind": {
                "path": "$doctor_details",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$unwind": {
                "path": "$ward_details",
                "preserveNullAndEmptyArrays": True
            }
        }
    ]
    results = list(db.patients.aggregate(pipeline))
    if not results:
        return None
    return serialize_mongo(results[0])

def create_patient_record(data):
    """
    Create: Inserts a new patient admission. Enforces MongoDB $jsonSchema.
    Atomically updates ward occupied_beds counter using $inc.
    """
    db = get_db()
    
    # Auto-generate patient ID if missing
    if "patient_id" not in data or not data["patient_id"]:
        last_patient = db.patients.find_one({}, sort=[("patient_id", -1)])
        if last_patient and "patient_id" in last_patient:
            try:
                num = int(last_patient["patient_id"].split("-")[-1]) + 1
            except Exception:
                num = 1011
        else:
            num = 1001
        data["patient_id"] = f"PAT-2026-{num}"

    # Parse and enforce BSON types
    if "age" in data:
        data["age"] = int(data["age"])
    
    if "admission_date" not in data or not data["admission_date"]:
        data["admission_date"] = datetime.now(timezone.utc)
    elif isinstance(data["admission_date"], str):
        data["admission_date"] = datetime.fromisoformat(data["admission_date"].replace("Z", "+00:00"))

    # Parse ObjectIds for referencing
    if "assigned_doctor_id" in data and data["assigned_doctor_id"]:
        if isinstance(data["assigned_doctor_id"], str):
            if ObjectId.is_valid(data["assigned_doctor_id"]):
                data["assigned_doctor_id"] = ObjectId(data["assigned_doctor_id"])
            else:
                doc = db.doctors.find_one({"doctor_id": data["assigned_doctor_id"]})
                if doc:
                    data["assigned_doctor_id"] = doc["_id"]
                else:
                    data.pop("assigned_doctor_id", None)

    if "assigned_ward" in data and isinstance(data["assigned_ward"], dict):
        if "ward_id" in data["assigned_ward"] and isinstance(data["assigned_ward"]["ward_id"], str):
            if ObjectId.is_valid(data["assigned_ward"]["ward_id"]):
                data["assigned_ward"]["ward_id"] = ObjectId(data["assigned_ward"]["ward_id"])
            else:
                ward = db.wards.find_one({"ward_code": data["assigned_ward"]["ward_id"]})
                if ward:
                    data["assigned_ward"]["ward_id"] = ward["_id"]
                else:
                    data["assigned_ward"].pop("ward_id", None)

    # Baseline vitals history
    if "vitals_history" not in data or not data["vitals_history"]:
        initial_hr = int(data.get("initial_heart_rate", 82))
        initial_spo2 = int(data.get("initial_spo2", 98))
        initial_temp = float(data.get("initial_temperature", 98.6))
        systolic = int(data.get("systolic", 120))
        diastolic = int(data.get("diastolic", 80))
        data["vitals_history"] = [
            {
                "recorded_at": datetime.now(timezone.utc),
                "heart_rate": initial_hr,
                "spo2": initial_spo2,
                "temperature": initial_temp,
                "systolic": systolic,
                "diastolic": diastolic,
                "blood_pressure": f"{systolic}/{diastolic}",
                "respiratory_rate": int(data.get("respiratory_rate", 18)),
                "recorded_by": "Triage Admission Nurse"
            }
        ]
    
    # Remove temporary form keys
    for temp_key in ["initial_heart_rate", "initial_spo2", "initial_temperature", "systolic", "diastolic", "respiratory_rate"]:
        data.pop(temp_key, None)

    try:
        result = db.patients.insert_one(data)
        
        # Atomically increment ward occupied beds if assigned
        if "assigned_ward" in data and "ward_id" in data["assigned_ward"]:
            db.wards.update_one(
                {"_id": data["assigned_ward"]["ward_id"]},
                {"$inc": {"occupied_beds": 1}}
            )

        return {
            "success": True,
            "patient_id": data["patient_id"],
            "inserted_id": str(result.inserted_id),
            "message": "Patient admission record created and validated successfully."
        }
    except DuplicateKeyError:
        return {"success": False, "error": f"Patient with ID '{data['patient_id']}' already exists."}
    except WriteError as e:
        return {"success": False, "error": f"MongoDB $jsonSchema validation failed: {e.details.get('errmsg', str(e))}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def push_vitals_telemetry(patient_id, vitals):
    """
    Update: Pushes a new vital telemetry data point into the patient's embedded vitals_history array.
    Demonstrates $push atomic array operator.
    """
    db = get_db()
    recorded_at = datetime.now(timezone.utc)
    vitals_doc = {
        "recorded_at": recorded_at,
        "heart_rate": int(vitals.get("heart_rate", 80)),
        "spo2": int(vitals.get("spo2", 98)),
        "temperature": float(vitals.get("temperature", 98.6)),
        "systolic": int(vitals.get("systolic", 120)),
        "diastolic": int(vitals.get("diastolic", 80)),
        "blood_pressure": f"{vitals.get('systolic', 120)}/{vitals.get('diastolic', 80)}",
        "respiratory_rate": int(vitals.get("respiratory_rate", 18)),
        "recorded_by": vitals.get("recorded_by", "Bedside IoT Monitor")
    }

    try:
        result = db.patients.update_one(
            {"patient_id": patient_id},
            {"$push": {"vitals_history": vitals_doc}}
        )
        if result.matched_count == 0:
            return {"success": False, "error": "Patient not found."}
        return {
            "success": True,
            "message": "Telemetry vitals logged successfully using $push operator.",
            "data": serialize_mongo(vitals_doc)
        }
    except WriteError as e:
        return {"success": False, "error": f"Validation failed: {e.details.get('errmsg', str(e))}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_patient_status(patient_id, update_fields):
    """
    Update: Modifies specific fields such as status, triage_level, or assigned ward using $set.
    """
    db = get_db()
    set_doc = {}
    
    if "status" in update_fields:
        set_doc["status"] = update_fields["status"]
    if "triage_level" in update_fields:
        set_doc["triage_level"] = update_fields["triage_level"]
    if "primary_complaint" in update_fields:
        set_doc["primary_complaint"] = update_fields["primary_complaint"]

    if not set_doc:
        return {"success": False, "error": "No valid fields to update."}

    try:
        res = db.patients.update_one(
            {"patient_id": patient_id},
            {"$set": set_doc}
        )
        return {
            "success": True,
            "matched_count": res.matched_count,
            "modified_count": res.modified_count,
            "message": f"Updated patient {patient_id} successfully with $set."
        }
    except WriteError as e:
        return {"success": False, "error": f"MongoDB Validation error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def discharge_patient_record(patient_id):
    """
    Update / Delete workflow: Discharges a patient, updates status to 'Discharged',
    and atomically decrements the assigned ward bed count via $inc.
    """
    db = get_db()
    patient = db.patients.find_one({"patient_id": patient_id})
    if not patient:
        return {"success": False, "error": "Patient not found."}

    res = db.patients.update_one(
        {"patient_id": patient_id},
        {"$set": {"status": "Discharged", "discharge_date": datetime.now(timezone.utc)}}
    )

    # Decrement ward beds if was admitted
    if "assigned_ward" in patient and "ward_id" in patient["assigned_ward"]:
        db.wards.update_one(
            {"_id": patient["assigned_ward"]["ward_id"], "occupied_beds": {"$gt": 0}},
            {"$inc": {"occupied_beds": -1}}
        )

    return {
        "success": True,
        "message": f"Patient {patient_id} successfully discharged. Ward bed availability updated via $inc."
    }

def delete_patient_record(patient_id, permanent=False):
    """
    Delete: Demonstrates delete_one for hard-delete or status update for soft-delete.
    """
    db = get_db()
    if permanent:
        res = db.patients.delete_one({"patient_id": patient_id})
        return {
            "success": True,
            "deleted_count": res.deleted_count,
            "message": f"Patient {patient_id} permanently removed via delete_one()."
        }
    else:
        # Soft delete
        res = db.patients.update_one(
            {"patient_id": patient_id},
            {"$set": {"status": "Discharged"}}
        )
        return {
            "success": True,
            "message": f"Patient {patient_id} soft-deleted (status set to Discharged)."
        }

def get_doctors_list():
    db = get_db()
    doctors = list(db.doctors.find().sort("name", 1))
    return serialize_mongo(doctors)

def get_wards_list():
    db = get_db()
    wards = list(db.wards.find().sort("floor", 1))
    return serialize_mongo(wards)

def test_validation_trigger():
    """
    Demonstration method for Viva/Presentation:
    Attempts to insert an intentionally invalid document (age=250, invalid phone, missing triage level)
    to visually demonstrate that MongoDB's $jsonSchema engine enforces strict validation.
    """
    db = get_db()
    invalid_doc = {
        "patient_id": "PAT-INVALID-9999", # Invalid pattern
        "name": "X",                      # Less than 2 chars
        "age": 250,                       # Greater than 125
        "gender": "UnknownGender",        # Not in enum
        "triage_level": "Code Black",     # Not in enum
        "admission_date": datetime.now(timezone.utc),
        "status": "In Limbo",             # Not in enum
        "contact": {"phone": "none"}
    }
    try:
        db.patients.insert_one(invalid_doc)
        return {
            "passed_validation": True,
            "message": "Document unexpectedly passed validation."
        }
    except WriteError as e:
        return {
            "passed_validation": False,
            "error_type": "MongoDB WriteError (Document failed validation)",
            "details": e.details,
            "explanation": "MongoDB successfully caught and rejected the malformed document according to $jsonSchema rules defined in database collection."
        }
    except Exception as e:
        return {
            "passed_validation": False,
            "error_type": type(e).__name__,
            "details": str(e),
            "explanation": "Validation rejected document."
        }
