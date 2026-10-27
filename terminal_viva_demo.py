"""
PulseCare AI - Terminal Database & Operations Demo
System: Intelligent Emergency Healthcare & Clinical Telemetry System
Run this script in terminal to demonstrate live CRUD, Validation rejection,
and Aggregation queries directly.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from backend.db import serialize_mongo
    from backend import crud
    from backend import aggregations
    from backend.seed_data import seed_all
except ImportError:
    from db import serialize_mongo  # type: ignore
    import crud  # type: ignore
    import aggregations  # type: ignore
    from seed_data import seed_all  # type: ignore

# ANSI Terminal Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title):
    print("\n" + "=" * 70)
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print("=" * 70)

def demo_1_schema_validation():
    print_header("DEMO 1: MongoDB $jsonSchema Validation Rules")
    print(f"{YELLOW}Testing what happens when an invalid document (age=250, invalid triage) is inserted:{RESET}")
    result = crud.test_validation_trigger()
    if not result.get("passed_validation"):
        print(f"\n{GREEN}✔ SUCCESS: MongoDB Engine successfully REJECTED invalid document!{RESET}")
        print(f"Error Type: {RED}{result.get('error_type')}{RESET}")
        print(f"Explanation: {result.get('explanation')}")
        print("\nRejection Details:")
        print(json.dumps(serialize_mongo(result.get("details")), indent=2))
    else:
        print(f"{RED}Validation failed to trigger.{RESET}")

def demo_2_crud_operations():
    print_header("DEMO 2: Complete PyMongo CRUD Operations")
    
    # 1. CREATE
    print(f"\n{BOLD}1. CREATE (db.patients.insert_one with schema validation):{RESET}")
    new_patient = {
        "name": "Alexander Sterling",
        "age": 42,
        "gender": "Male",
        "blood_group": "A+",
        "triage_level": "Level 2 - Emergent",
        "primary_complaint": "Acute abdominal pain and suspected perforation",
        "contact": {"phone": "+1-555-449-0123", "emergency_contact": "Claire Sterling"},
        "admission_date": datetime.now(timezone.utc),
        "status": "Admitted",
        "initial_heart_rate": 115,
        "initial_spo2": 94,
        "initial_temperature": 100.8,
        "systolic": 145,
        "diastolic": 92
    }
    create_res = crud.create_patient_record(new_patient)
    print(f"Result: {GREEN}{create_res}{RESET}")
    pid = create_res.get("patient_id")

    # 2. READ
    print(f"\n{BOLD}2. READ (db.patients.find with regex and criteria):{RESET}")
    patients, _ = crud.get_all_patients({"search": "Alexander"})
    print(f"Found {len(patients)} matching patient(s):")
    for p in patients:
        print(f" - [{p['patient_id']}] {p['name']} | Age: {p['age']} | Triage: {p['triage_level']} | Status: {p['status']}")

    # 3. UPDATE with $push
    print(f"\n{BOLD}3. UPDATE with $push (Appending new vitals reading to embedded array):{RESET}")
    new_vitals = {
        "heart_rate": 88,
        "spo2": 98,
        "temperature": 98.6,
        "systolic": 124,
        "diastolic": 80,
        "respiratory_rate": 16,
        "recorded_by": "ICU Attending Nurse"
    }
    push_res = crud.push_vitals_telemetry(pid, new_vitals)
    print(f"Result: {GREEN}{push_res['message']}{RESET}")

    # 4. UPDATE with $set
    print(f"\n{BOLD}4. UPDATE with $set (Modifying patient clinical status):{RESET}")
    update_res = crud.update_patient_status(pid, {"status": "Under Observation"})
    print(f"Result: {GREEN}{update_res['message']}{RESET}")

    # 5. DISCHARGE with $inc
    print(f"\n{BOLD}5. DISCHARGE & BED DECREMENT with $inc:{RESET}")
    disch_res = crud.discharge_patient_record(pid)
    print(f"Result: {GREEN}{disch_res['message']}{RESET}")

def demo_3_aggregations():
    print_header("DEMO 3: Advanced MongoDB Aggregation Pipelines")
    
    # Pipeline 1: Triage Analytics
    print(f"\n{BOLD}Pipeline 1: Emergency Triage Severity & Length-of-Stay Analysis ($match, $group, $project):{RESET}")
    triage_data, _ = aggregations.get_triage_analytics()
    for item in triage_data:
        print(f" • Triage: {YELLOW}{item['triage_level']}{RESET} | Patients: {BOLD}{item['total_patients']}{RESET} | Avg Stay: {item['avg_stay_hours']} hrs | Avg Age: {item['avg_age']} yrs")

    # Pipeline 2: Ward Heatmap
    print(f"\n{BOLD}Pipeline 2: Hospital Ward Capacity & Ventilator Utilization ($lookup, $project):{RESET}")
    ward_data, _ = aggregations.get_ward_occupancy_heatmap()
    for w in ward_data:
        print(f" • [{w['ward_code']}] {w['name']} | Occupancy: {BOLD}{w['occupancy_rate']}%{RESET} | Beds Free: {w['available_beds']} | Vents: {w['ventilators_available']}")

    # Pipeline 3: Telemetry Anomaly Detection
    print(f"\n{BOLD}Pipeline 3: Telemetry Vitals Anomaly & Critical Risk Detector ($unwind, $match, $group, $cond):{RESET}")
    anomalies, _ = aggregations.get_telemetry_anomalies()
    for a in anomalies[:4]:
        risk_color = RED if a['risk_category'] == 'CRITICAL EMERGENCY' else YELLOW
        print(f" • [{a['patient_id']}] {a['patient_name']} ({a['age']}y) | Risk: {risk_color}{a['risk_category']}{RESET} | Min SpO2: {a['min_spo2']}% | Max HR: {a['max_heart_rate']} bpm")

    # Pipeline 4: Physician Caseload
    print(f"\n{BOLD}Pipeline 4: Physician Caseload & ICU Caseload Matrix ($lookup, $filter, $size):{RESET}")
    workload, _ = aggregations.get_physician_workload()
    for doc in workload[:4]:
        print(f" • {doc['name']} ({doc['specialization']}) | Active Cases: {BOLD}{doc['current_load']}{RESET} | ICU: {doc['icu_cases']} | Load: {doc['utilization_pct']}%")

    # Pipeline 5: Executive $facet
    print(f"\n{BOLD}Pipeline 5: 360° Hospital Executive Analytics Multi-Stream Facet ($facet, $bucket):{RESET}")
    facet_data, _ = aggregations.get_executive_360_facet()
    fin = facet_data.get("financial_metrics", [{}])[0]
    print(f" • Total Billed: ${fin.get('total_billed', 0):,} | Avg Bill: ${fin.get('avg_bill_per_patient', 0):,} | Insured: {fin.get('insurance_coverage_pct', 0)}%")
    print(f" • Demographic Age Buckets:")
    for b in facet_data.get("age_demographics", []):
        print(f"    - Bracket: {b['age_bracket']} | Count: {b['count']} | Avg Age: {b['avg_age']}")

def main_menu():
    print(f"""
{CYAN}======================================================================
    PulseCare AI - Intelligent Healthcare Telemetry Database Demo
======================================================================{RESET}
1. Run Complete Demonstration (All CRUD, Validation & Aggregations)
2. Test MongoDB $jsonSchema Validation Rules
3. Test PyMongo CRUD Operations
4. Test 5 MongoDB Aggregation Pipelines
5. Reseed Database with Fresh Data
6. Exit
""")
    choice = input("Enter choice (1-6) [Default 1]: ").strip() or "1"
    if choice == "1":
        demo_1_schema_validation()
        demo_2_crud_operations()
        demo_3_aggregations()
        print(f"\n{GREEN}✔ All demonstration modules executed successfully!{RESET}\n")
    elif choice == "2":
        demo_1_schema_validation()
    elif choice == "3":
        demo_2_crud_operations()
    elif choice == "4":
        demo_3_aggregations()
    elif choice == "5":
        seed_all()
    elif choice == "6":
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        demo_1_schema_validation()
        demo_2_crud_operations()
        demo_3_aggregations()
    else:
        demo_1_schema_validation()
        demo_2_crud_operations()
        demo_3_aggregations()
