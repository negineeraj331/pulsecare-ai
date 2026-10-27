"""
PulseCare AI - Seed Data Generator
Pre-populates MongoDB with realistic emergency hospital records, doctors, wards,
and time-series vital telemetry streams for testing and presentation demo.
"""

from datetime import datetime, timedelta, timezone
from bson import ObjectId
from db import get_db, init_database

def seed_all():
    print("Initializing database collections and JSON Schema validators...")
    init_database(drop_existing=True)
    db = get_db()
    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------
    # 1. Seed Wards
    # -------------------------------------------------------------------------
    wards_data = [
        {
            "_id": ObjectId("660000000000000000000001"),
            "ward_code": "WARD-ICU-A",
            "name": "Intensive Care Unit (Alpha Wing)",
            "ward_type": "ICU",
            "total_beds": 12,
            "occupied_beds": 9,
            "floor": 3,
            "ventilators_available": 4
        },
        {
            "_id": ObjectId("660000000000000000000002"),
            "ward_code": "WARD-EMERG-01",
            "name": "Acute Emergency Bay 1",
            "ward_type": "Emergency",
            "total_beds": 20,
            "occupied_beds": 16,
            "floor": 1,
            "ventilators_available": 3
        },
        {
            "_id": ObjectId("660000000000000000000003"),
            "ward_code": "WARD-TRAUMA-01",
            "name": "Level-1 Trauma Resuscitation Suite",
            "ward_type": "Trauma",
            "total_beds": 8,
            "occupied_beds": 6,
            "floor": 1,
            "ventilators_available": 5
        },
        {
            "_id": ObjectId("660000000000000000000004"),
            "ward_code": "WARD-CCU-01",
            "name": "Coronary Care Unit (CCU)",
            "ward_type": "Cardiology",
            "total_beds": 10,
            "occupied_beds": 7,
            "floor": 2,
            "ventilators_available": 2
        },
        {
            "_id": ObjectId("660000000000000000000005"),
            "ward_code": "WARD-PED-01",
            "name": "Pediatric Emergency Ward",
            "ward_type": "Pediatric",
            "total_beds": 15,
            "occupied_beds": 5,
            "floor": 2,
            "ventilators_available": 2
        },
        {
            "_id": ObjectId("660000000000000000000006"),
            "ward_code": "WARD-OBS-01",
            "name": "24-Hour Clinical Observation Ward",
            "ward_type": "General",
            "total_beds": 25,
            "occupied_beds": 14,
            "floor": 1,
            "ventilators_available": 1
        }
    ]
    db.wards.insert_many(wards_data)
    print(f"Inserted {len(wards_data)} clinical wards.")

    # -------------------------------------------------------------------------
    # 2. Seed Doctors
    # -------------------------------------------------------------------------
    doctors_data = [
        {
            "_id": ObjectId("661000000000000000000001"),
            "doctor_id": "DOC-101",
            "name": "Dr. Sarah Chen, MD",
            "specialization": "Emergency Medicine",
            "on_duty": True,
            "shift": "Morning",
            "room_number": "ER-101",
            "max_active_patients": 15
        },
        {
            "_id": ObjectId("661000000000000000000002"),
            "doctor_id": "DOC-102",
            "name": "Dr. Marcus Brody, MD",
            "specialization": "Critical Care",
            "on_duty": True,
            "shift": "Morning",
            "room_number": "ICU-302",
            "max_active_patients": 10
        },
        {
            "_id": ObjectId("661000000000000000000003"),
            "doctor_id": "DOC-103",
            "name": "Dr. Priya Nair, MD",
            "specialization": "Cardiology",
            "on_duty": True,
            "shift": "Evening",
            "room_number": "CARD-205",
            "max_active_patients": 12
        },
        {
            "_id": ObjectId("661000000000000000000004"),
            "doctor_id": "DOC-104",
            "name": "Dr. Alexander Wright, MD",
            "specialization": "General Surgery",
            "on_duty": False,
            "shift": "Night",
            "room_number": "SURG-410",
            "max_active_patients": 8
        },
        {
            "_id": ObjectId("661000000000000000000005"),
            "doctor_id": "DOC-105",
            "name": "Dr. Elena Rostova, MD",
            "specialization": "Pulmonology",
            "on_duty": True,
            "shift": "Morning",
            "room_number": "PULM-218",
            "max_active_patients": 12
        },
        {
            "_id": ObjectId("661000000000000000000006"),
            "doctor_id": "DOC-106",
            "name": "Dr. Devanshi Sharma, MD",
            "specialization": "Neurology",
            "on_duty": True,
            "shift": "Night",
            "room_number": "NEURO-315",
            "max_active_patients": 10
        }
    ]
    db.doctors.insert_many(doctors_data)
    print(f"Inserted {len(doctors_data)} specialized physicians.")

    # -------------------------------------------------------------------------
    # 3. Seed Patients with Time-Series Vitals and Triage
    # -------------------------------------------------------------------------
    patients_data = [
        {
            "patient_id": "PAT-2026-1001",
            "name": "Eleanor Vance",
            "age": 64,
            "gender": "Female",
            "blood_group": "O+",
            "contact": {
                "phone": "+1-555-019-2831",
                "emergency_contact": "Arthur Vance (Husband)"
            },
            "admission_date": now - timedelta(hours=3, minutes=20),
            "triage_level": "Level 1 - Resuscitation",
            "primary_complaint": "Acute Myocardial Infarction with diaphoresis",
            "assigned_doctor_id": ObjectId("661000000000000000000003"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000004"),
                "ward_name": "Coronary Care Unit (CCU)",
                "bed_number": "CCU-B02",
                "ward_type": "Cardiology"
            },
            "status": "ICU",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=3),
                    "heart_rate": 138,
                    "blood_pressure": "165/105",
                    "systolic": 165,
                    "diastolic": 105,
                    "spo2": 88,
                    "temperature": 99.4,
                    "respiratory_rate": 28,
                    "recorded_by": "Nurse J. Miller"
                },
                {
                    "recorded_at": now - timedelta(hours=1, minutes=45),
                    "heart_rate": 122,
                    "blood_pressure": "150/95",
                    "systolic": 150,
                    "diastolic": 95,
                    "spo2": 92,
                    "temperature": 99.1,
                    "respiratory_rate": 24,
                    "recorded_by": "Nurse J. Miller"
                },
                {
                    "recorded_at": now - timedelta(minutes=25),
                    "heart_rate": 108,
                    "blood_pressure": "135/88",
                    "systolic": 135,
                    "diastolic": 88,
                    "spo2": 95,
                    "temperature": 98.6,
                    "respiratory_rate": 20,
                    "recorded_by": "Nurse T. Becker"
                }
            ],
            "allergies": ["Penicillin", "Sulfa drugs"],
            "current_medications": [
                {"name": "Aspirin", "dosage": "325 mg", "frequency": "Stat"},
                {"name": "Nitroglycerin", "dosage": "0.4 mg", "frequency": "SL q5min prn"},
                {"name": "Heparin IV", "dosage": "5000 units", "frequency": "Continuous"}
            ],
            "billing": {
                "total_amount": 14200.0,
                "insurance_covered": True,
                "payment_status": "Pending Claims"
            }
        },
        {
            "patient_id": "PAT-2026-1002",
            "name": "Marcus Sterling",
            "age": 32,
            "gender": "Male",
            "blood_group": "A-",
            "contact": {
                "phone": "+1-555-082-9912",
                "emergency_contact": "Sarah Sterling (Sister)"
            },
            "admission_date": now - timedelta(hours=1, minutes=15),
            "triage_level": "Level 1 - Resuscitation",
            "primary_complaint": "Severe polytrauma motor vehicle collision with blunt thoracic trauma",
            "assigned_doctor_id": ObjectId("661000000000000000000002"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000003"),
                "ward_name": "Level-1 Trauma Resuscitation Suite",
                "bed_number": "TR-B01",
                "ward_type": "Trauma"
            },
            "status": "ICU",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=1),
                    "heart_rate": 145,
                    "blood_pressure": "85/50",
                    "systolic": 85,
                    "diastolic": 50,
                    "spo2": 84,
                    "temperature": 96.8,
                    "respiratory_rate": 32,
                    "recorded_by": "Dr. Brody"
                },
                {
                    "recorded_at": now - timedelta(minutes=20),
                    "heart_rate": 128,
                    "blood_pressure": "98/62",
                    "systolic": 98,
                    "diastolic": 62,
                    "spo2": 91,
                    "temperature": 97.4,
                    "respiratory_rate": 26,
                    "recorded_by": "Nurse J. Miller"
                }
            ],
            "allergies": [],
            "current_medications": [
                {"name": "Tranexamic Acid", "dosage": "1 g IV", "frequency": "Stat"},
                {"name": "Packed Red Blood Cells", "dosage": "2 Units", "frequency": "Rapid Infusion"}
            ],
            "billing": {
                "total_amount": 28500.0,
                "insurance_covered": True,
                "payment_status": "Processing"
            }
        },
        {
            "patient_id": "PAT-2026-1003",
            "name": "Sophia Reynolds",
            "age": 28,
            "gender": "Female",
            "blood_group": "B+",
            "contact": {
                "phone": "+1-555-033-7744",
                "emergency_contact": "Liam Reynolds (Father)"
            },
            "admission_date": now - timedelta(hours=4, minutes=50),
            "triage_level": "Level 2 - Emergent",
            "primary_complaint": "Acute severe asthma exacerbation unresponsive to albuterol",
            "assigned_doctor_id": ObjectId("661000000000000000000005"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000002"),
                "ward_name": "Acute Emergency Bay 1",
                "bed_number": "ER-B04",
                "ward_type": "Emergency"
            },
            "status": "Admitted",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=4),
                    "heart_rate": 126,
                    "blood_pressure": "130/84",
                    "systolic": 130,
                    "diastolic": 84,
                    "spo2": 89,
                    "temperature": 98.8,
                    "respiratory_rate": 30,
                    "recorded_by": "Nurse K. Adams"
                },
                {
                    "recorded_at": now - timedelta(hours=2),
                    "heart_rate": 110,
                    "blood_pressure": "124/80",
                    "systolic": 124,
                    "diastolic": 80,
                    "spo2": 94,
                    "temperature": 98.6,
                    "respiratory_rate": 22,
                    "recorded_by": "Nurse K. Adams"
                },
                {
                    "recorded_at": now - timedelta(minutes=40),
                    "heart_rate": 96,
                    "blood_pressure": "120/78",
                    "systolic": 120,
                    "diastolic": 78,
                    "spo2": 97,
                    "temperature": 98.4,
                    "respiratory_rate": 18,
                    "recorded_by": "Nurse K. Adams"
                }
            ],
            "allergies": ["NSAIDs", "Aspirin"],
            "current_medications": [
                {"name": "Methylprednisolone", "dosage": "125 mg IV", "frequency": "Single Dose"},
                {"name": "Duoneb Nebulizer", "dosage": "3 ml", "frequency": "q20min x 3"}
            ],
            "billing": {
                "total_amount": 4200.0,
                "insurance_covered": True,
                "payment_status": "Settled"
            }
        },
        {
            "patient_id": "PAT-2026-1004",
            "name": "David Henderson",
            "age": 71,
            "gender": "Male",
            "blood_group": "AB+",
            "contact": {
                "phone": "+1-555-067-1123",
                "emergency_contact": "Ruth Henderson (Wife)"
            },
            "admission_date": now - timedelta(hours=6, minutes=10),
            "triage_level": "Level 2 - Emergent",
            "primary_complaint": "Acute ischemic stroke symptoms: right-sided hemiparesis and aphasia",
            "assigned_doctor_id": ObjectId("661000000000000000000006"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000001"),
                "ward_name": "Intensive Care Unit (Alpha Wing)",
                "bed_number": "ICU-A03",
                "ward_type": "ICU"
            },
            "status": "ICU",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=5),
                    "heart_rate": 88,
                    "blood_pressure": "185/110",
                    "systolic": 185,
                    "diastolic": 110,
                    "spo2": 96,
                    "temperature": 98.9,
                    "respiratory_rate": 18,
                    "recorded_by": "Dr. Sharma"
                },
                {
                    "recorded_at": now - timedelta(hours=2, minutes=30),
                    "heart_rate": 82,
                    "blood_pressure": "160/94",
                    "systolic": 160,
                    "diastolic": 94,
                    "spo2": 98,
                    "temperature": 98.7,
                    "respiratory_rate": 16,
                    "recorded_by": "Nurse R. Vance"
                }
            ],
            "allergies": ["Latex"],
            "current_medications": [
                {"name": "Tenecteplase IV", "dosage": "0.25 mg/kg", "frequency": "Stat Bolus"},
                {"name": "Labetalol IV", "dosage": "10 mg", "frequency": "prn BP > 180/105"}
            ],
            "billing": {
                "total_amount": 19800.0,
                "insurance_covered": True,
                "payment_status": "Processing"
            }
        },
        {
            "patient_id": "PAT-2026-1005",
            "name": "Aarav Patel",
            "age": 19,
            "gender": "Male",
            "blood_group": "O-",
            "contact": {
                "phone": "+1-555-098-4455",
                "emergency_contact": "Sunita Patel (Mother)"
            },
            "admission_date": now - timedelta(hours=2, minutes=40),
            "triage_level": "Level 3 - Urgent",
            "primary_complaint": "Acute appendicitis with localized right lower quadrant rebound tenderness",
            "assigned_doctor_id": ObjectId("661000000000000000000001"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000002"),
                "ward_name": "Acute Emergency Bay 1",
                "bed_number": "ER-B09",
                "ward_type": "Emergency"
            },
            "status": "Admitted",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=2),
                    "heart_rate": 102,
                    "blood_pressure": "118/76",
                    "systolic": 118,
                    "diastolic": 76,
                    "spo2": 99,
                    "temperature": 101.3,
                    "respiratory_rate": 20,
                    "recorded_by": "Nurse T. Becker"
                }
            ],
            "allergies": [],
            "current_medications": [
                {"name": "Ceftriaxone IV", "dosage": "1 g", "frequency": "q24h"},
                {"name": "Acetaminophen IV", "dosage": "1000 mg", "frequency": "q6h prn fever"}
            ],
            "billing": {
                "total_amount": 6300.0,
                "insurance_covered": False,
                "payment_status": "Self Pay Deposit"
            }
        },
        {
            "patient_id": "PAT-2026-1006",
            "name": "Maria Morales",
            "age": 45,
            "gender": "Female",
            "blood_group": "A+",
            "contact": {
                "phone": "+1-555-014-9988",
                "emergency_contact": "Carlos Morales (Brother)"
            },
            "admission_date": now - timedelta(hours=7, minutes=30),
            "triage_level": "Level 3 - Urgent",
            "primary_complaint": "Diabetic ketoacidosis (DKA) with nausea and Kussmaul respirations",
            "assigned_doctor_id": ObjectId("661000000000000000000001"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000006"),
                "ward_name": "24-Hour Clinical Observation Ward",
                "bed_number": "OBS-04",
                "ward_type": "General"
            },
            "status": "Under Observation",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=7),
                    "heart_rate": 118,
                    "blood_pressure": "106/68",
                    "systolic": 106,
                    "diastolic": 68,
                    "spo2": 97,
                    "temperature": 99.2,
                    "respiratory_rate": 26,
                    "recorded_by": "Nurse K. Adams"
                },
                {
                    "recorded_at": now - timedelta(hours=3),
                    "heart_rate": 92,
                    "blood_pressure": "116/74",
                    "systolic": 116,
                    "diastolic": 74,
                    "spo2": 98,
                    "temperature": 98.6,
                    "respiratory_rate": 19,
                    "recorded_by": "Nurse K. Adams"
                }
            ],
            "allergies": ["Codeine"],
            "current_medications": [
                {"name": "Regular Insulin Infusion", "dosage": "0.1 units/kg/hr", "frequency": "IV drip"},
                {"name": "Normal Saline 0.9%", "dosage": "1000 ml", "frequency": "Continuous IV"}
            ],
            "billing": {
                "total_amount": 7800.0,
                "insurance_covered": True,
                "payment_status": "Settled"
            }
        },
        {
            "patient_id": "PAT-2026-1007",
            "name": "Jordan Lee",
            "age": 24,
            "gender": "Other",
            "blood_group": "B-",
            "contact": {
                "phone": "+1-555-072-8811",
                "emergency_contact": "Taylor Lee (Partner)"
            },
            "admission_date": now - timedelta(hours=1, minutes=50),
            "triage_level": "Level 4 - Less Urgent",
            "primary_complaint": "Distal radius fracture following sports injury, neurovascularly intact",
            "assigned_doctor_id": ObjectId("661000000000000000000001"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000002"),
                "ward_name": "Acute Emergency Bay 1",
                "bed_number": "ER-B14",
                "ward_type": "Emergency"
            },
            "status": "Triage",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=1, minutes=30),
                    "heart_rate": 84,
                    "blood_pressure": "122/80",
                    "systolic": 122,
                    "diastolic": 80,
                    "spo2": 99,
                    "temperature": 98.4,
                    "respiratory_rate": 16,
                    "recorded_by": "Triage Nurse L. Perez"
                }
            ],
            "allergies": [],
            "current_medications": [
                {"name": "Ibuprofen", "dosage": "600 mg", "frequency": "Oral single dose"}
            ],
            "billing": {
                "total_amount": 1650.0,
                "insurance_covered": True,
                "payment_status": "Paid"
            }
        },
        {
            "patient_id": "PAT-2026-1008",
            "name": "Evelyn Thorne",
            "age": 58,
            "gender": "Female",
            "blood_group": "O+",
            "contact": {
                "phone": "+1-555-081-4477",
                "emergency_contact": "Gerald Thorne (Spouse)"
            },
            "admission_date": now - timedelta(hours=8, minutes=45),
            "triage_level": "Level 2 - Emergent",
            "primary_complaint": "Sepsis secondary to acute pyelonephritis with high-grade pyrexia",
            "assigned_doctor_id": ObjectId("661000000000000000000002"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000001"),
                "ward_name": "Intensive Care Unit (Alpha Wing)",
                "bed_number": "ICU-A07",
                "ward_type": "ICU"
            },
            "status": "ICU",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=8),
                    "heart_rate": 134,
                    "blood_pressure": "88/54",
                    "systolic": 88,
                    "diastolic": 54,
                    "spo2": 93,
                    "temperature": 103.4,
                    "respiratory_rate": 26,
                    "recorded_by": "Nurse J. Miller"
                },
                {
                    "recorded_at": now - timedelta(hours=4),
                    "heart_rate": 114,
                    "blood_pressure": "98/62",
                    "systolic": 98,
                    "diastolic": 62,
                    "spo2": 95,
                    "temperature": 101.1,
                    "respiratory_rate": 22,
                    "recorded_by": "Nurse J. Miller"
                },
                {
                    "recorded_at": now - timedelta(hours=1),
                    "heart_rate": 96,
                    "blood_pressure": "112/70",
                    "systolic": 112,
                    "diastolic": 70,
                    "spo2": 97,
                    "temperature": 99.8,
                    "respiratory_rate": 18,
                    "recorded_by": "Nurse R. Vance"
                }
            ],
            "allergies": ["Ciprofloxacin"],
            "current_medications": [
                {"name": "Piperacillin-Tazobactam IV", "dosage": "3.375 g", "frequency": "q6h"},
                {"name": "Norepinephrine IV", "dosage": "0.05 mcg/kg/min", "frequency": "Titrated"}
            ],
            "billing": {
                "total_amount": 22100.0,
                "insurance_covered": True,
                "payment_status": "Processing"
            }
        },
        {
            "patient_id": "PAT-2026-1009",
            "name": "Karan Malhotra",
            "age": 52,
            "gender": "Male",
            "blood_group": "A+",
            "contact": {
                "phone": "+1-555-091-7733",
                "emergency_contact": "Ananya Malhotra (Wife)"
            },
            "admission_date": now - timedelta(hours=14),
            "triage_level": "Level 3 - Urgent",
            "primary_complaint": "Severe exacerbation of chronic COPD with purulent sputum",
            "assigned_doctor_id": ObjectId("661000000000000000000005"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000006"),
                "ward_name": "24-Hour Clinical Observation Ward",
                "bed_number": "OBS-09",
                "ward_type": "General"
            },
            "status": "Discharged",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=13),
                    "heart_rate": 104,
                    "blood_pressure": "138/86",
                    "systolic": 138,
                    "diastolic": 86,
                    "spo2": 91,
                    "temperature": 99.1,
                    "respiratory_rate": 24,
                    "recorded_by": "Nurse K. Adams"
                },
                {
                    "recorded_at": now - timedelta(hours=2),
                    "heart_rate": 78,
                    "blood_pressure": "122/78",
                    "systolic": 122,
                    "diastolic": 78,
                    "spo2": 96,
                    "temperature": 98.4,
                    "respiratory_rate": 16,
                    "recorded_by": "Nurse K. Adams"
                }
            ],
            "allergies": [],
            "current_medications": [
                {"name": "Prednisone Oral", "dosage": "40 mg", "frequency": "Daily x 5 days"},
                {"name": "Azithromycin Oral", "dosage": "500 mg", "frequency": "Day 1, then 250 mg"}
            ],
            "billing": {
                "total_amount": 3400.0,
                "insurance_covered": True,
                "payment_status": "Settled"
            }
        },
        {
            "patient_id": "PAT-2026-1010",
            "name": "Chloe Bennett",
            "age": 8,
            "gender": "Female",
            "blood_group": "O+",
            "contact": {
                "phone": "+1-555-045-8899",
                "emergency_contact": "Robert Bennett (Father)"
            },
            "admission_date": now - timedelta(hours=2, minutes=10),
            "triage_level": "Level 2 - Emergent",
            "primary_complaint": "Pediatric anaphylaxis after accidental peanut ingestion",
            "assigned_doctor_id": ObjectId("661000000000000000000001"),
            "assigned_ward": {
                "ward_id": ObjectId("660000000000000000000005"),
                "ward_name": "Pediatric Emergency Ward",
                "bed_number": "PED-B03",
                "ward_type": "Pediatric"
            },
            "status": "Under Observation",
            "vitals_history": [
                {
                    "recorded_at": now - timedelta(hours=2),
                    "heart_rate": 140,
                    "blood_pressure": "84/52",
                    "systolic": 84,
                    "diastolic": 52,
                    "spo2": 91,
                    "temperature": 98.6,
                    "respiratory_rate": 32,
                    "recorded_by": "Pediatric Nurse M. Cruz"
                },
                {
                    "recorded_at": now - timedelta(minutes=45),
                    "heart_rate": 105,
                    "blood_pressure": "96/60",
                    "systolic": 96,
                    "diastolic": 60,
                    "spo2": 98,
                    "temperature": 98.4,
                    "respiratory_rate": 22,
                    "recorded_by": "Pediatric Nurse M. Cruz"
                }
            ],
            "allergies": ["Peanuts", "Tree nuts"],
            "current_medications": [
                {"name": "Epinephrine IM", "dosage": "0.15 mg", "frequency": "Stat"},
                {"name": "Diphenhydramine IV", "dosage": "25 mg", "frequency": "Single dose"}
            ],
            "billing": {
                "total_amount": 2900.0,
                "insurance_covered": True,
                "payment_status": "Settled"
            }
        }
    ]

    db.patients.insert_many(patients_data)
    print(f"Inserted {len(patients_data)} clinical emergency patients with telemetry.")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_all()
