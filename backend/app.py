"""
PulseCare AI - Flask Application Backend
Enterprise Clinical Telemetry & Hospital Resource Intelligence Platform
"""

import os
import sys
import time
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_db, serialize_mongo
import crud
import aggregations
from seed_data import seed_all

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates"),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
)
CORS(app)

_db_initialized = False

def ensure_db_initialized():
    global _db_initialized
    if _db_initialized:
        return
    try:
        db = get_db()
        cols = db.list_collection_names()
        if "patients" not in cols or db.patients.count_documents({}) == 0:
            print("PulseCare AI: Initializing schema rules and seeding initial clinical database...")
            seed_all()
        _db_initialized = True
    except Exception as e:
        print(f"Notice: Database auto-initialization check skipped ({e})")

@app.before_request
def before_request_hook():
    if not request.path.startswith("/static"):
        ensure_db_initialized()

# -------------------------------------------------------------
# Web Page Route
# -------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------------------------------
# System & Health
# -------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    db = get_db()
    try:
        start = time.time()
        db.command("ping")
        ping_ms = round((time.time() - start) * 1000, 2)
        patient_count = db.patients.count_documents({})
        doctor_count = db.doctors.count_documents({})
        ward_count = db.wards.count_documents({})
        
        return jsonify({
            "status": "healthy",
            "database": db.name,
            "connected": True,
            "latency_ms": ping_ms,
            "counts": {
                "patients": patient_count,
                "doctors": doctor_count,
                "wards": ward_count
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "connected": False,
            "error": str(e)
        }), 500

# -------------------------------------------------------------
# Patient CRUD Endpoints
# -------------------------------------------------------------
@app.route("/api/patients", methods=["GET"])
def list_patients():
    query_params = {
        "search": request.args.get("search", ""),
        "triage_level": request.args.get("triage_level", ""),
        "status": request.args.get("status", ""),
        "blood_group": request.args.get("blood_group", "")
    }
    start = time.time()
    patients, mongo_filter = crud.get_all_patients(query=query_params)
    execution_time_ms = round((time.time() - start) * 1000, 2)

    return jsonify({
        "success": True,
        "count": len(patients),
        "execution_time_ms": execution_time_ms,
        "filter_applied": mongo_filter,
        "pymongo_code": f"db.patients.find({mongo_filter}).sort('admission_date', -1)",
        "data": patients
    })

@app.route("/api/patients/<patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = crud.get_patient_details(patient_id)
    if not patient:
        return jsonify({"success": False, "error": "Patient not found"}), 404
    return jsonify({"success": True, "data": patient})

@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.json or {}
    start = time.time()
    result = crud.create_patient_record(data)
    execution_time_ms = round((time.time() - start) * 1000, 2)
    result["execution_time_ms"] = execution_time_ms
    result["pymongo_code"] = "db.patients.insert_one(document)"
    status_code = 201 if result.get("success") else 400
    return jsonify(result), status_code

@app.route("/api/patients/<patient_id>/vitals", methods=["POST"])
def add_vitals(patient_id):
    vitals = request.json or {}
    start = time.time()
    result = crud.push_vitals_telemetry(patient_id, vitals)
    result["execution_time_ms"] = round((time.time() - start) * 1000, 2)
    result["pymongo_code"] = f"db.patients.update_one({{'patient_id': '{patient_id}'}}, {{'$push': {{'vitals_history': new_reading}}}})"
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code

@app.route("/api/patients/<patient_id>", methods=["PATCH"])
def update_patient(patient_id):
    update_data = request.json or {}
    start = time.time()
    result = crud.update_patient_status(patient_id, update_data)
    result["execution_time_ms"] = round((time.time() - start) * 1000, 2)
    result["pymongo_code"] = f"db.patients.update_one({{'patient_id': '{patient_id}'}}, {{'$set': update_data}})"
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code

@app.route("/api/patients/<patient_id>/discharge", methods=["POST"])
def discharge_patient(patient_id):
    start = time.time()
    result = crud.discharge_patient_record(patient_id)
    result["execution_time_ms"] = round((time.time() - start) * 1000, 2)
    result["pymongo_code"] = f"db.patients.update_one({{'patient_id': '{patient_id}'}}, {{'$set': {{'status': 'Discharged'}}}}) + db.wards.update_one(..., {{'$inc': {{'occupied_beds': -1}}}})"
    status_code = 200 if result.get("success") else 400
    return jsonify(result), status_code

@app.route("/api/patients/<patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    permanent = request.args.get("permanent", "false").lower() == "true"
    start = time.time()
    result = crud.delete_patient_record(patient_id, permanent=permanent)
    result["execution_time_ms"] = round((time.time() - start) * 1000, 2)
    result["pymongo_code"] = f"db.patients.delete_one({{'patient_id': '{patient_id}'}})" if permanent else "db.patients.update_one(..., {'$set': {'status': 'Discharged'}})"
    return jsonify(result)

# -------------------------------------------------------------
# Reference Endpoints (Doctors & Wards)
# -------------------------------------------------------------
@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    doctors = crud.get_doctors_list()
    return jsonify({"success": True, "data": doctors})

@app.route("/api/wards", methods=["GET"])
def get_wards():
    wards = crud.get_wards_list()
    return jsonify({"success": True, "data": wards})

# -------------------------------------------------------------
# Advanced Aggregation Analytics Endpoints
# -------------------------------------------------------------
@app.route("/api/analytics/triage", methods=["GET"])
def analytics_triage():
    start = time.time()
    results, pipeline = aggregations.get_triage_analytics()
    ms = round((time.time() - start) * 1000, 2)
    return jsonify({
        "title": "Emergency Triage Severity & Length-of-Stay Analysis",
        "description": "Calculates stay duration in hours using $divide and $subtract, grouping by triage severity level with average patient age.",
        "execution_time_ms": ms,
        "stages_count": len(pipeline),
        "pipeline": pipeline,
        "data": results
    })

@app.route("/api/analytics/wards", methods=["GET"])
def analytics_wards():
    start = time.time()
    results, pipeline = aggregations.get_ward_occupancy_heatmap()
    ms = round((time.time() - start) * 1000, 2)
    return jsonify({
        "title": "Hospital Ward Capacity & Ventilator Utilization Heatmap",
        "description": "Correlates clinical wards with active patient admissions via $lookup to compute real-time occupancy percentages and bed shortages.",
        "execution_time_ms": ms,
        "stages_count": len(pipeline),
        "pipeline": pipeline,
        "data": results
    })

@app.route("/api/analytics/anomalies", methods=["GET"])
def analytics_anomalies():
    start = time.time()
    results, pipeline = aggregations.get_telemetry_anomalies()
    ms = round((time.time() - start) * 1000, 2)
    return jsonify({
        "title": "Critical Vital Telemetry Anomaly & Risk Detection",
        "description": "Deconstructs time-series vitals using $unwind, detects life-threatening readings (SpO2 < 92, Heart Rate > 120), and aggregates clinical risk level.",
        "execution_time_ms": ms,
        "stages_count": len(pipeline),
        "pipeline": pipeline,
        "data": results
    })

@app.route("/api/analytics/workload", methods=["GET"])
def analytics_workload():
    start = time.time()
    results, pipeline = aggregations.get_physician_workload()
    ms = round((time.time() - start) * 1000, 2)
    return jsonify({
        "title": "Physician Clinical Workload & Emergency Caseload Matrix",
        "description": "Performs cross-collection $lookup between doctors and patients to compute active emergency caseloads, ICU ratios, and doctor capacity utilization.",
        "execution_time_ms": ms,
        "stages_count": len(pipeline),
        "pipeline": pipeline,
        "data": results
    })

@app.route("/api/analytics/executive", methods=["GET"])
def analytics_executive():
    start = time.time()
    results, pipeline = aggregations.get_executive_360_facet()
    ms = round((time.time() - start) * 1000, 2)
    return jsonify({
        "title": "360° Hospital Command Multi-Faceted Performance ($facet)",
        "description": "Executes 4 parallel analytic streams in a single network round-trip: triage distributions, status metrics, age demographic buckets ($bucket), and billing financials.",
        "execution_time_ms": ms,
        "stages_count": len(pipeline),
        "pipeline": pipeline,
        "data": results
    })

# -------------------------------------------------------------
# Live Validation Demonstration
# -------------------------------------------------------------
@app.route("/api/validation-test", methods=["POST"])
def run_validation_test():
    """
    Demonstrates MongoDB rejecting documents violating $jsonSchema
    """
    start = time.time()
    result = crud.test_validation_trigger()
    result["execution_time_ms"] = round((time.time() - start) * 1000, 2)
    return jsonify(result)

# -------------------------------------------------------------
# Interactive Viva Query Sandbox
# -------------------------------------------------------------
@app.route("/api/sandbox/query", methods=["POST"])
def sandbox_query():
    """
    Allows executing pre-defined or custom read/aggregation queries for Viva evaluation.
    """
    body = request.json or {}
    query_type = body.get("type", "find")  # 'find' or 'aggregate'
    collection_name = body.get("collection", "patients")
    db = get_db()

    if collection_name not in ["patients", "doctors", "wards"]:
        return jsonify({"success": False, "error": "Invalid collection specified."}), 400

    col = db[collection_name]
    start = time.time()

    try:
        if query_type == "find":
            filter_doc = body.get("filter", {})
            projection_doc = body.get("projection", None)
            limit = min(int(body.get("limit", 20)), 50)
            
            cursor = col.find(filter_doc, projection_doc).limit(limit)
            results = list(cursor)
            execution_time_ms = round((time.time() - start) * 1000, 2)
            
            return jsonify({
                "success": True,
                "query_type": "find",
                "collection": collection_name,
                "count": len(results),
                "execution_time_ms": execution_time_ms,
                "pymongo_code": f"db.{collection_name}.find({filter_doc}, {projection_doc}).limit({limit})",
                "results": serialize_mongo(results)
            })

        elif query_type == "aggregate":
            pipeline = body.get("pipeline", [])
            if not isinstance(pipeline, list):
                return jsonify({"success": False, "error": "Pipeline must be an array of stages."}), 400

            results = list(col.aggregate(pipeline))
            execution_time_ms = round((time.time() - start) * 1000, 2)
            
            return jsonify({
                "success": True,
                "query_type": "aggregate",
                "collection": collection_name,
                "count": len(results),
                "execution_time_ms": execution_time_ms,
                "pymongo_code": f"db.{collection_name}.aggregate({pipeline})",
                "results": serialize_mongo(results)
            })
        else:
            return jsonify({"success": False, "error": "Unsupported query type."}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# -------------------------------------------------------------
# Database Reset & Reseed
# -------------------------------------------------------------
@app.route("/api/reset-data", methods=["POST"])
def reset_database():
    try:
        start = time.time()
        seed_all()
        ms = round((time.time() - start) * 1000, 2)
        return jsonify({
            "success": True,
            "message": "Database refreshed and seeded with realistic test clinical records.",
            "execution_time_ms": ms
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"Starting PulseCare AI Flask Server on http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=debug)

