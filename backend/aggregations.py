"""
PulseCare AI - MongoDB Aggregation Pipelines
Implements advanced analytical pipelines using $match, $group, $unwind, $lookup,
$project, $facet, $bucket, and $dateDiff for clinical intelligence.
"""

from db import get_db, serialize_mongo
from datetime import datetime, timezone

def get_triage_analytics():
    """
    Pipeline 1: Emergency Triage Severity & Length-of-Stay Analytics
    Computes patient count, average length of stay in hours, and age distribution per triage level.
    """
    db = get_db()
    pipeline = [
        {
            "$match": {
                "status": {"$ne": "Discharged"}
            }
        },
        {
            "$project": {
                "patient_id": 1,
                "name": 1,
                "age": 1,
                "triage_level": 1,
                "status": 1,
                "stay_hours": {
                    "$round": [
                        {
                            "$divide": [
                                {"$subtract": ["$$NOW", "$admission_date"]},
                                1000 * 60 * 60
                            ]
                        },
                        1
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$triage_level",
                "total_patients": {"$sum": 1},
                "avg_stay_hours": {"$avg": "$stay_hours"},
                "avg_age": {"$avg": "$age"},
                "patient_list": {
                    "$push": {
                        "patient_id": "$patient_id",
                        "name": "$name",
                        "stay_hours": "$stay_hours",
                        "status": "$status"
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "triage_level": "$_id",
                "total_patients": 1,
                "avg_stay_hours": {"$round": ["$avg_stay_hours", 1]},
                "avg_age": {"$round": ["$avg_age", 1]},
                "patient_list": 1
            }
        },
        {
            "$sort": {"total_patients": -1, "triage_level": 1}
        }
    ]
    results = list(db.patients.aggregate(pipeline))
    return serialize_mongo(results), pipeline

def get_ward_occupancy_heatmap():
    """
    Pipeline 2: Clinical Ward & Bed Occupancy Analytics
    Uses $lookup to correlate wards with actively admitted patients and compute real-time utilization.
    """
    db = get_db()
    pipeline = [
        {
            "$lookup": {
                "from": "patients",
                "let": {"wardId": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$assigned_ward.ward_id", "$$wardId"]},
                                    {"$ne": ["$status", "Discharged"]}
                                ]
                            }
                        }
                    }
                ],
                "as": "current_admissions"
            }
        },
        {
            "$project": {
                "_id": 0,
                "ward_code": 1,
                "name": 1,
                "ward_type": 1,
                "floor": 1,
                "total_beds": 1,
                "ventilators_available": 1,
                "active_patients_count": {"$size": "$current_admissions"},
                "occupancy_rate": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {"$size": "$current_admissions"},
                                        "$total_beds"
                                    ]
                                },
                                100
                            ]
                        },
                        1
                    ]
                },
                "available_beds": {
                    "$subtract": ["$total_beds", {"$size": "$current_admissions"}]
                }
            }
        },
        {
            "$sort": {"occupancy_rate": -1}
        }
    ]
    results = list(db.wards.aggregate(pipeline))
    return serialize_mongo(results), pipeline

def get_telemetry_anomalies():
    """
    Pipeline 3: Time-Series Vitals Anomaly & Critical Risk Detector
    Deconstructs vitals_history using $unwind, detects life-threatening readings,
    and aggregates risk profile per patient.
    """
    db = get_db()
    pipeline = [
        {
            "$match": {
                "status": {"$in": ["ICU", "Admitted", "Triage", "Under Observation"]}
            }
        },
        {
            "$unwind": "$vitals_history"
        },
        {
            "$match": {
                "$or": [
                    {"vitals_history.spo2": {"$lt": 92}},
                    {"vitals_history.heart_rate": {"$gt": 120}},
                    {"vitals_history.systolic": {"$gt": 160}},
                    {"vitals_history.systolic": {"$lt": 90}},
                    {"vitals_history.temperature": {"$gt": 101.0}}
                ]
            }
        },
        {
            "$group": {
                "_id": "$patient_id",
                "patient_name": {"$first": "$name"},
                "age": {"$first": "$age"},
                "triage_level": {"$first": "$triage_level"},
                "status": {"$first": "$status"},
                "primary_complaint": {"$first": "$primary_complaint"},
                "assigned_doctor_id": {"$first": "$assigned_doctor_id"},
                "anomaly_count": {"$sum": 1},
                "min_spo2": {"$min": "$vitals_history.spo2"},
                "max_heart_rate": {"$max": "$vitals_history.heart_rate"},
                "max_systolic": {"$max": "$vitals_history.systolic"},
                "latest_anomalous_reading": {"$last": "$vitals_history"}
            }
        },
        {
            "$lookup": {
                "from": "doctors",
                "localField": "assigned_doctor_id",
                "foreignField": "_id",
                "as": "doctor"
            }
        },
        {
            "$unwind": {
                "path": "$doctor",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "patient_id": "$_id",
                "patient_name": 1,
                "age": 1,
                "triage_level": 1,
                "status": 1,
                "primary_complaint": 1,
                "attending_physician": "$doctor.name",
                "doctor_specialty": "$doctor.specialization",
                "anomaly_count": 1,
                "min_spo2": 1,
                "max_heart_rate": 1,
                "max_systolic": 1,
                "latest_anomalous_reading": 1,
                "risk_category": {
                    "$cond": {
                        "if": {
                            "$or": [
                                {"$lt": ["$min_spo2", 88]},
                                {"$gt": ["$max_heart_rate", 135]}
                            ]
                        },
                        "then": "CRITICAL EMERGENCY",
                        "else": "HIGH RISK WARNING"
                    }
                }
            }
        },
        {
            "$sort": {"anomaly_count": -1, "min_spo2": 1}
        }
    ]
    results = list(db.patients.aggregate(pipeline))
    return serialize_mongo(results), pipeline

def get_physician_workload():
    """
    Pipeline 4: Physician Caseload & Specialty Efficiency Matrix
    Correlates doctors with assigned emergency cases, breaking down active vs ICU cases.
    """
    db = get_db()
    pipeline = [
        {
            "$lookup": {
                "from": "patients",
                "let": {"docId": "$_id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$assigned_doctor_id", "$$docId"]},
                                    {"$ne": ["$status", "Discharged"]}
                                ]
                            }
                        }
                    }
                ],
                "as": "active_patients"
            }
        },
        {
            "$project": {
                "_id": 0,
                "doctor_id": 1,
                "name": 1,
                "specialization": 1,
                "shift": 1,
                "on_duty": 1,
                "room_number": 1,
                "max_active_patients": 1,
                "current_load": {"$size": "$active_patients"},
                "icu_cases": {
                    "$size": {
                        "$filter": {
                            "input": "$active_patients",
                            "as": "p",
                            "cond": {"$eq": ["$$p.status", "ICU"]}
                        }
                    }
                },
                "utilization_pct": {
                    "$round": [
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {"$size": "$active_patients"},
                                        "$max_active_patients"
                                    ]
                                },
                                100
                            ]
                        },
                        1
                    ]
                }
            }
        },
        {
            "$sort": {"current_load": -1, "icu_cases": -1}
        }
    ]
    results = list(db.doctors.aggregate(pipeline))
    return serialize_mongo(results), pipeline

def get_executive_360_facet():
    """
    Pipeline 5: 360° Hospital Executive Analytics using multi-channel $facet
    Computes triage distribution, age demographics bucket, billing metrics, and status totals in 1 round-trip.
    """
    db = get_db()
    pipeline = [
        {
            "$facet": {
                "triage_distribution": [
                    {
                        "$group": {
                            "_id": "$triage_level",
                            "count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"count": -1}}
                ],
                "status_distribution": [
                    {
                        "$group": {
                            "_id": "$status",
                            "count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"count": -1}}
                ],
                "age_demographics": [
                    {
                        "$bucket": {
                            "groupBy": "$age",
                            "boundaries": [0, 18, 40, 65, 100],
                            "default": "Centenarian",
                            "output": {
                                "count": {"$sum": 1},
                                "avg_age": {"$avg": "$age"}
                            }
                        }
                    },
                    {
                        "$project": {
                            "age_bracket": "$_id",
                            "count": 1,
                            "avg_age": {"$round": ["$avg_age", 1]}
                        }
                    }
                ],
                "financial_metrics": [
                    {
                        "$group": {
                            "_id": None,
                            "total_billed": {"$sum": "$billing.total_amount"},
                            "avg_bill_per_patient": {"$avg": "$billing.total_amount"},
                            "insured_patients": {
                                "$sum": {
                                    "$cond": ["$billing.insurance_covered", 1, 0]
                                }
                            },
                            "total_cases": {"$sum": 1}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "total_billed": {"$round": ["$total_billed", 2]},
                            "avg_bill_per_patient": {"$round": ["$avg_bill_per_patient", 2]},
                            "insurance_coverage_pct": {
                                "$round": [
                                    {
                                        "$multiply": [
                                            {"$divide": ["$insured_patients", "$total_cases"]},
                                            100
                                        ]
                                    },
                                    1
                                ]
                            }
                        }
                    }
                ]
            }
        }
    ]
    results = list(db.patients.aggregate(pipeline))
    return serialize_mongo(results[0]) if results else {}, pipeline
