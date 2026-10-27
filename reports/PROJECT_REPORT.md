# LOVELY PROFESSIONAL UNIVERSITY
## School of Computer Science and Engineering
### Academic Task 2: Comprehensive Project Report
**Course Code:** CSE494  
**Course Title:** INTELLIGENT NOSQL DATABASES  
**Academic Task Type:** Project Report & Demonstration  
**Date of Allotment:** 31st August, 2026  
**Date of Submission:** 19th October, 2026  
**Maximum Marks:** 30 (Implementation: 15 | Report: 5 | Presentation & Viva: 10)  
**Applicable Course Outcomes:** CO4, CO5, CO6  
**Bloom's Taxonomy Levels:** L2 (Understanding), L3 (Applying & Analyzing)  

---

# PulseCare AI: Intelligent Emergency Healthcare & Clinical Resource Telemetry System
**Author:** Individual Project Submission  
**Environment:** MongoDB 7.0.26 Server, Python 3.13.2, PyMongo 4.19.0, Flask REST API, Modern Clinical Command Center UI  
**GitHub Repository:** [https://github.com/negineeraj331/pulsecare-ai](https://github.com/negineeraj331/pulsecare-ai)  
**Live Production Deployment:** [https://pulsecare-ai-twh4.onrender.com/](https://pulsecare-ai-twh4.onrender.com/)  

---

## TABLE OF CONTENTS
1. [Executive Summary & Abstract](#1-executive-summary--abstract)
2. [Problem Statement & Real-World Relevance](#2-problem-statement--real-world-relevance)
3. [Database & Document Architecture Design](#3-database--document-architecture-design)
   - 3.1 Relational SQL vs. MongoDB NoSQL Comparison
   - 3.2 Data Modeling Strategy: Embedding vs. Referencing
   - 3.3 Collections & Formal Schema Definitions
   - 3.4 Indexing Strategy & Query Optimization
4. [MongoDB Validation Rules ($jsonSchema)](#4-mongodb-validation-rules-jsonschema)
   - 4.1 Implementation of Engine-Level Validation
   - 4.2 Error Code 121 Write Rejection Proof
5. [PyMongo CRUD Implementation & Atomic Operators](#5-pymongo-crud-implementation--atomic-operators)
   - 5.1 Create Operation (`insert_one`) with Atomic Bed Allocation
   - 5.2 Read Operations (`find`) with Regex & Multi-Field Filters
   - 5.3 Update Operations with Atomic Operators (`$push`, `$set`, `$inc`)
   - 5.4 Delete Operations (`delete_one` vs. Soft Archival)
6. [Advanced Aggregation Pipelines & Analytics](#6-advanced-aggregation-pipelines--analytics)
   - 6.1 Pipeline 1: Emergency Triage Acuity & Length-of-Stay Analysis
   - 6.2 Pipeline 2: Ward Capacity & Ventilator Utilization Heatmap
   - 6.3 Pipeline 3: Telemetry Vitals Anomaly & Critical Risk Detector
   - 6.4 Pipeline 4: Physician Caseload & ICU Caseload Matrix
   - 6.5 Pipeline 5: 360° Hospital Command Multi-Stream Performance (`$facet`)
7. [System Screenshots & Operation Demonstrations](#7-system-screenshots--operation-demonstrations)
8. [Viva & Oral Defense Preparation Guide](#8-viva--oral-defense-preparation-guide)
9. [Conclusion & Future Enhancements](#9-conclusion--future-enhancements)

---

## 1. Executive Summary & Abstract
In acute clinical environments, real-time access to patient health data and resource metrics directly impacts patient survival rates. Traditional relational database management systems (RDBMS) struggle with the high-velocity, irregular telemetry streams emitted by modern bedside vital monitors and the polymorphic nature of emergency health records. 

**PulseCare AI** is an intelligent, high-throughput NoSQL database platform built using MongoDB 7.0 and PyMongo. It introduces a clinical command center that resolves emergency triage prioritization bottlenecks, detects life-threatening vital anomalies in real time, and balances ward bed and physician allocations. 

The project demonstrates:
* **CO4 (Design & Modeling):** A hybrid embedded-referenced document architecture balancing sub-millisecond read access with entity normalization.
* **CO5 (CRUD & Validation):** Complete PyMongo integration with database-enforced `$jsonSchema` validation and atomic operators (`$push`, `$set`, `$inc`).
* **CO6 (Aggregations & Analytics):** Five multi-stage analytical aggregation pipelines employing `$match`, `$group`, `$unwind`, `$lookup`, `$facet`, `$bucket`, and `$cond` to extract actionable operational intelligence.

---

## 2. Problem Statement & Real-World Relevance

### 2.1 Clinical Challenges in Emergency Departments
1. **Triage Lag & Acuity Classification Misjudgments:** Emergency rooms (ERs) receive patients under varying levels of physiological distress. Delays in classifying patients according to the 5-tier Emergency Severity Index (ESI) lead to dangerous clinical deterioration.
2. **High-Velocity Telemetry Data Handling:** Vital monitoring sensors record heart rate, blood pressure, SpO2, and respiratory rate at short intervals. Relational schemas require rigid columns, leading to sparse tables filled with `NULL` values when different departments record differing telemetry parameters.
3. **Bed Allocation & Critical Equipment Bottlenecks:** Intensive Care Units (ICUs) and emergency wards often experience severe capacity crises. Relational queries across millions of rows to determine real-time bed and ventilator availability create heavy database lock contention.

### 2.2 Real-World Solution with MongoDB NoSQL
MongoDB provides an optimal solution for these healthcare challenges:
* **Polymorphic Medical Encounters:** Allows each patient record to contain specialty-specific clinical markers (e.g., cardiac enzymes for cardiology vs. Glasgow Coma Scale for trauma) without requiring global schema migrations.
* **Single-Seek Read Performance:** Embedding historical vitals inside the patient document enables the entire patient clinical history to be loaded in a single atomic disk seek ($O(1)$) during emergency resuscitations.
* **Atomic Multi-Field Updates:** Using operators such as `$push` (for appending vitals telemetry) and `$inc` (for incrementing/decrementing ward bed occupancy) ensures atomicity without locking table spaces.

---

## 3. Database & Document Architecture Design

### 3.1 Relational SQL vs. MongoDB NoSQL Comparison

| Architectural Feature | Traditional Relational SQL | PulseCare AI (MongoDB NoSQL) |
| :--- | :--- | :--- |
| **Data Representation** | Normalized rows split across multiple tables (`patients`, `vitals`, `contacts`). | Hierarchical, rich JSON/BSON document storing all patient context in a cohesive unit. |
| **Telemetry Ingestion** | Requires foreign-key inserts into a `patient_vitals` table; joins required for every read. | Telemetry readings appended directly into embedded `vitals_history` array using `$push`. |
| **Schema Flexibility** | Rigid schema; DDL `ALTER TABLE` statements required to introduce new sensor metrics. | Dynamic and polymorphic; documents adapt to variable diagnostic parameters effortlessly. |
| **Read Complexity** | Multi-table relational `JOIN` operations requiring significant CPU and buffer cache. | Single document lookup by indexed `patient_id` with embedded timeline. |
| **Horizontal Scaling** | Sharding relational databases with foreign-key constraints is notoriously brittle. | Native horizontal scaling through configurable compound shard keys. |

---

### 3.2 Data Modeling Strategy: Embedding vs. Referencing

```
+-----------------------------------------------------------------------------------------+
|                                    PATIENT DOCUMENT                                     |
|  - _id: ObjectId                                                                        |
|  - patient_id: "PAT-2026-1001" (Indexed, Unique)                                        |
|  - name, age, gender, blood_group, triage_level, status                                 |
|  - contact: { phone, emergency_contact }                  <-- EMBEDDED OBJECT           |
|  - assigned_doctor_id: ObjectId("661000000000000000000003")<-- REFERENCED OBJECTID     |
|  - assigned_ward: { ward_id: Ref, ward_name, bed_number } <-- HYBRID EMBEDDED SNAPSHOT   |
|  - vitals_history: [                                      <-- EMBEDDED TIME-SERIES      |
|      { recorded_at, heart_rate, spo2, blood_pressure, temp, recorded_by },              |
|      { recorded_at, heart_rate, spo2, blood_pressure, temp, recorded_by }               |
|    ]                                                                                    |
|  - allergies: ["Penicillin", "Sulfa drugs"]                                             |
|  - current_medications: [{ name, dosage, frequency }]                                   |
|  - billing: { total_amount, insurance_covered, payment_status }                         |
+-----------------------------------------------------------------------------------------+
                     |                                              |
        Referenced by ObjectId                         Referenced by ObjectId
                     v                                              v
+-----------------------------------------+    +-----------------------------------------+
|            DOCTORS COLLECTION           |    |             WARDS COLLECTION            |
|  - _id: ObjectId                        |    |  - _id: ObjectId                        |
|  - doctor_id: "DOC-101"                 |    |  - ward_code: "WARD-ICU-A"              |
|  - name: "Dr. Sarah Chen, MD"           |    |  - name: "Intensive Care Unit (Alpha)"  |
|  - specialization: "Emergency Medicine" |    |  - ward_type: "ICU"                     |
|  - on_duty: true | shift: "Morning"     |    |  - total_beds: 12 | occupied_beds: 9    |
|  - max_active_patients: 15              |    |  - ventilators_available: 4             |
+-----------------------------------------+    +-----------------------------------------+
```

1. **Embedded Pattern Justification:**
   - **`vitals_history`:** Clinicians reviewing an emergency admission require immediate access to all vital trends over the past 24 hours. Placing vitals inside an embedded array eliminates costly cross-table joins during life-critical decisions.
   - **`contact` & `billing`:** Strictly 1-to-1 data belonging solely to the patient encounter.
2. **Referenced Pattern Justification:**
   - **`doctors`:** Physicians have independent lifecycles, work multiple shifts, and care for multiple patients concurrently. Duplicating doctor records inside patient documents would cause update anomalies whenever a physician changes shift or phone number.
   - **`wards`:** Hospital wards have static operational capacities and inventories. Patients store the foreign reference `assigned_ward.ward_id` along with a lightweight denormalized snapshot of the bed number.

---

### 3.3 Collections & Formal Schema Definitions

#### Collection 1: `patients`
```json
{
  "_id": {"$oid": "660000000000000000000010"},
  "patient_id": "PAT-2026-1001",
  "name": "Eleanor Vance",
  "age": 64,
  "gender": "Female",
  "blood_group": "O+",
  "contact": {
    "phone": "+1-555-019-2831",
    "emergency_contact": "Arthur Vance (Husband)"
  },
  "admission_date": {"$date": "2026-10-19T17:40:00.000Z"},
  "triage_level": "Level 1 - Resuscitation",
  "primary_complaint": "Acute Myocardial Infarction with diaphoresis",
  "assigned_doctor_id": {"$oid": "661000000000000000000003"},
  "assigned_ward": {
    "ward_id": {"$oid": "660000000000000000000004"},
    "ward_name": "Coronary Care Unit (CCU)",
    "bed_number": "CCU-B02",
    "ward_type": "Cardiology"
  },
  "status": "ICU",
  "vitals_history": [
    {
      "recorded_at": {"$date": "2026-10-19T18:00:00.000Z"},
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
      "recorded_at": {"$date": "2026-10-19T19:15:00.000Z"},
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
    {"name": "Nitroglycerin", "dosage": "0.4 mg", "frequency": "SL q5min prn"}
  ],
  "billing": {
    "total_amount": 14200.0,
    "insurance_covered": true,
    "payment_status": "Pending Claims"
  }
}
```

#### Collection 2: `doctors`
```json
{
  "_id": {"$oid": "661000000000000000000001"},
  "doctor_id": "DOC-101",
  "name": "Dr. Sarah Chen, MD",
  "specialization": "Emergency Medicine",
  "on_duty": true,
  "shift": "Morning",
  "room_number": "ER-101",
  "max_active_patients": 15
}
```

#### Collection 3: `wards`
```json
{
  "_id": {"$oid": "660000000000000000000001"},
  "ward_code": "WARD-ICU-A",
  "name": "Intensive Care Unit (Alpha Wing)",
  "ward_type": "ICU",
  "total_beds": 12,
  "occupied_beds": 9,
  "floor": 3,
  "ventilators_available": 4
}
```

---

### 3.4 Indexing Strategy & Query Optimization

Indexes are programmatically constructed during database bootstrap in [`backend/db.py`](file:///Users/neerajnegi/Desktop/mongodb_project/backend/db.py):

| Target Collection | Index Definition | Index Type | Optimization Rationale |
| :--- | :--- | :--- | :--- |
| `patients` | `{"patient_id": 1}` | Unique B-Tree | Guarantees uniqueness of medical record numbers; enables $O(1)$ lookups. |
| `patients` | `{"triage_level": 1}` | Single Field | Optimizes urgent triage queries during ER volume surges. |
| `patients` | `{"status": 1}` | Single Field | Speeds up filtering for active inpatients vs. discharged records. |
| `patients` | `{"assigned_doctor_id": 1, "status": 1}` | Compound | Accelerates physician caseload calculations in Pipeline 4. |
| `patients` | `{"admission_date": -1}` | Descending | Powers reverse-chronological sorting on the patient directory view. |
| `patients` | `{"name": "text", "primary_complaint": "text"}` | Text Index | Enables fast text search across clinical notes and patient names. |
| `doctors` | `{"doctor_id": 1}` | Unique B-Tree | Ensures distinct identifiers for medical staff. |
| `wards` | `{"ward_code": 1}` | Unique B-Tree | Accelerates ward lookup by hospital division code. |

---

## 4. MongoDB Validation Rules ($jsonSchema)

### 4.1 Implementation of Engine-Level Validation
In strict compliance with **CO5**, schema validation is enforced at the database layer using MongoDB's `$jsonSchema` operator:

```python
PATIENT_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["patient_id", "name", "age", "gender", "triage_level", "admission_date", "status"],
        "properties": {
            "patient_id": {
                "bsonType": "string",
                "pattern": "^PAT-[0-9]{4}-[0-9]{4}$",
                "description": "Must match regex PAT-YYYY-XXXX and is mandatory"
            },
            "name": {
                "bsonType": "string",
                "minLength": 2,
                "maxLength": 100
            },
            "age": {
                "bsonType": "int",
                "minimum": 0,
                "maximum": 125,
                "description": "Age must be an integer between 0 and 125"
            },
            "gender": {
                "enum": ["Male", "Female", "Other"]
            },
            "blood_group": {
                "enum": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]
            },
            "triage_level": {
                "enum": [
                    "Level 1 - Resuscitation",
                    "Level 2 - Emergent",
                    "Level 3 - Urgent",
                    "Level 4 - Less Urgent",
                    "Level 5 - Non-Urgent"
                ]
            },
            "status": {
                "enum": ["Triage", "Admitted", "ICU", "Under Observation", "Discharged", "Transferred"]
            },
            "vitals_history": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["recorded_at", "heart_rate", "spo2", "temperature"],
                    "properties": {
                        "heart_rate": {"bsonType": "int", "minimum": 30, "maximum": 250},
                        "spo2": {"bsonType": "int", "minimum": 40, "maximum": 100},
                        "temperature": {"bsonType": ["double", "int"], "minimum": 90.0, "maximum": 110.0}
                    }
                }
            }
        }
    }
}
```

### 4.2 Error Code 121 Write Rejection Proof
When an invalid document violates these schema boundaries (e.g., `age: 250`, `name: "X"`, `gender: "Alien"`, `triage_level: "Code Black"`), MongoDB aborts the write operation with error code `121`:

```json
{
  "index": 0,
  "code": 121,
  "errmsg": "Document failed validation",
  "errInfo": {
    "operatorName": "$jsonSchema",
    "schemaRulesNotSatisfied": [
      {
        "operatorName": "properties",
        "propertiesNotSatisfied": [
          {
            "propertyName": "age",
            "reason": "comparison failed",
            "consideredValue": 250
          },
          {
            "propertyName": "name",
            "reason": "specified string length was not satisfied",
            "consideredValue": "X"
          },
          {
            "propertyName": "gender",
            "reason": "value was not found in enum",
            "consideredValue": "Alien"
          },
          {
            "propertyName": "triage_level",
            "reason": "value was not found in enum",
            "consideredValue": "Code Black"
          }
        ]
      }
    ]
  }
}
```

---

## 5. PyMongo CRUD Implementation & Atomic Operators

### 5.1 Create Operation (`insert_one`) with Atomic Bed Allocation
Creates a new patient record and atomically updates the assigned ward's occupied bed counter using `$inc`:

```python
def create_patient_record(data):
    db = get_db()
    # Format and type parsing
    data["age"] = int(data["age"])
    data["admission_date"] = datetime.now(timezone.utc)
    
    # Execute document insertion
    result = db.patients.insert_one(data)
    
    # Atomically increment ward occupied bed counter
    if "assigned_ward" in data and "ward_id" in data["assigned_ward"]:
        db.wards.update_one(
            {"_id": data["assigned_ward"]["ward_id"]},
            {"$inc": {"occupied_beds": 1}}
        )
    return {"success": True, "patient_id": data["patient_id"], "inserted_id": str(result.inserted_id)}
```

### 5.2 Read Operations (`find`) with Regex & Multi-Field Filters
Enables case-insensitive text searching, categorical filtering, and sorting:

```python
def get_all_patients(query=None, limit=50):
    db = get_db()
    mongo_filter = {}
    if query:
        if query.get("search"):
            term = query["search"].strip()
            mongo_filter["$or"] = [
                {"name": {"$regex": term, "$options": "i"}},
                {"patient_id": {"$regex": term, "$options": "i"}},
                {"primary_complaint": {"$regex": term, "$options": "i"}}
            ]
        if query.get("triage_level"):
            mongo_filter["triage_level"] = query["triage_level"]
        if query.get("status"):
            mongo_filter["status"] = query["status"]

    cursor = db.patients.find(mongo_filter).sort("admission_date", -1).limit(limit)
    return list(cursor), mongo_filter
```

### 5.3 Update Operations with Atomic Operators (`$push`, `$set`, `$inc`)

1. **`$push` for Time-Series Ingestion:** Appends an incoming telemetry record into `vitals_history`:
   ```python
   def push_vitals_telemetry(patient_id, vitals):
       db = get_db()
       vitals_doc = {
           "recorded_at": datetime.now(timezone.utc),
           "heart_rate": int(vitals["heart_rate"]),
           "spo2": int(vitals["spo2"]),
           "temperature": float(vitals["temperature"]),
           "systolic": int(vitals["systolic"]),
           "diastolic": int(vitals["diastolic"]),
           "blood_pressure": f"{vitals['systolic']}/{vitals['diastolic']}",
           "respiratory_rate": int(vitals.get("respiratory_rate", 18)),
           "recorded_by": vitals.get("recorded_by", "Bedside IoT Monitor")
       }
       return db.patients.update_one(
           {"patient_id": patient_id},
           {"$push": {"vitals_history": vitals_doc}}
       )
   ```

2. **`$set` for Clinical Status Transitions:**
   ```python
   def update_patient_status(patient_id, update_fields):
       db = get_db()
       return db.patients.update_one(
           {"patient_id": patient_id},
           {"$set": update_fields}
       )
   ```

3. **`$inc` for Patient Discharge & Bed Release:**
   ```python
   def discharge_patient_record(patient_id):
       db = get_db()
       patient = db.patients.find_one({"patient_id": patient_id})
       db.patients.update_one(
           {"patient_id": patient_id},
           {"$set": {"status": "Discharged", "discharge_date": datetime.now(timezone.utc)}}
       )
       if "assigned_ward" in patient and "ward_id" in patient["assigned_ward"]:
           db.wards.update_one(
               {"_id": patient["assigned_ward"]["ward_id"], "occupied_beds": {"$gt": 0}},
               {"$inc": {"occupied_beds": -1}}
           )
   ```

### 5.4 Delete Operations (`delete_one` vs. Soft Archival)
```python
def delete_patient_record(patient_id, permanent=False):
    db = get_db()
    if permanent:
        return db.patients.delete_one({"patient_id": patient_id})
    else:
        return db.patients.update_one({"patient_id": patient_id}, {"$set": {"status": "Discharged"}})
```

---

## 6. Advanced Aggregation Pipelines & Analytics

### 6.1 Pipeline 1: Emergency Triage Acuity & Length-of-Stay Analysis
* **Purpose:** Computes inpatient volume, average stay in hours (derived using `$subtract` and `$divide` between `$$NOW` and `admission_date`), and average age per triage acuity category.
* **Stages:**
  1. `$match`: `{ status: { $ne: "Discharged" } }`
  2. `$project`: Calculates `stay_hours` using mathematical date expressions.
  3. `$group`: Groups by `triage_level`, calculating `$sum`, `$avg` stay hours, and `$avg` age.
  4. `$project`: Formats and rounds numeric averages.
  5. `$sort`: `{ total_patients: -1 }`

**Actual Output:**
```json
[
  {
    "triage_level": "Level 2 - Emergent",
    "total_patients": 4,
    "avg_stay_hours": 5.5,
    "avg_age": 41.2
  },
  {
    "triage_level": "Level 1 - Resuscitation",
    "total_patients": 2,
    "avg_stay_hours": 2.3,
    "avg_age": 48.0
  },
  {
    "triage_level": "Level 3 - Urgent",
    "total_patients": 2,
    "avg_stay_hours": 5.1,
    "avg_age": 32.0
  },
  {
    "triage_level": "Level 4 - Less Urgent",
    "total_patients": 1,
    "avg_stay_hours": 1.8,
    "avg_age": 24.0
  }
]
```

---

### 6.2 Pipeline 2: Ward Capacity & Ventilator Utilization Heatmap
* **Purpose:** Correlates clinical wards with active patient admissions via a correlated `$lookup` sub-pipeline to determine real-time occupancy percentages and ventilator surpluses.
* **Stages:**
  1. `$lookup`: Correlates `wards` with `patients` matching `assigned_ward.ward_id == ward._id` where `status != "Discharged"`.
  2. `$project`: Computes `occupancy_rate` via `(($size(current_admissions) / total_beds) * 100)` and `available_beds`.
  3. `$sort`: `{ occupancy_rate: -1 }`

**Actual Output:**
```json
[
  {
    "ward_code": "WARD-ICU-A",
    "name": "Intensive Care Unit (Alpha Wing)",
    "ward_type": "ICU",
    "total_beds": 12,
    "occupancy_rate": 25.0,
    "available_beds": 9,
    "ventilators_available": 4
  },
  {
    "ward_code": "WARD-EMERG-01",
    "name": "Acute Emergency Bay 1",
    "ward_type": "Emergency",
    "total_beds": 20,
    "occupancy_rate": 15.0,
    "available_beds": 17,
    "ventilators_available": 3
  },
  {
    "ward_code": "WARD-TRAUMA-01",
    "name": "Level-1 Trauma Resuscitation Suite",
    "ward_type": "Trauma",
    "total_beds": 8,
    "occupancy_rate": 12.5,
    "available_beds": 7,
    "ventilators_available": 5
  }
]
```

---

### 6.3 Pipeline 3: Telemetry Vitals Anomaly & Critical Risk Detector
* **Purpose:** Unwinds time-series vitals arrays, filters critical thresholds (SpO2 < 92%, HR > 120 bpm, systolic > 160 mmHg), groups by patient, joins attending physicians, and assigns clinical risk using `$cond`.
* **Stages:**
  1. `$match`: Active clinical encounters.
  2. `$unwind`: Unrolls `$vitals_history`.
  3. `$match`: Evaluates critical telemetry triggers (`spo2 < 92` OR `heart_rate > 120` OR `systolic > 160`).
  4. `$group`: Groups by `patient_id`, evaluating `$min` SpO2 and `$max` heart rate.
  5. `$lookup`: Joins doctor information from `doctors`.
  6. `$project`: Uses conditional logic `$cond` to assign `CRITICAL EMERGENCY` vs `HIGH RISK WARNING`.
  7. `$sort`: `{ anomaly_count: -1, min_spo2: 1 }`

**Actual Output:**
```json
[
  {
    "patient_id": "PAT-2026-1002",
    "patient_name": "Marcus Sterling",
    "age": 32,
    "triage_level": "Level 1 - Resuscitation",
    "attending_physician": "Dr. Marcus Brody, MD",
    "doctor_specialty": "Critical Care",
    "anomaly_count": 2,
    "min_spo2": 84,
    "max_heart_rate": 145,
    "risk_category": "CRITICAL EMERGENCY"
  },
  {
    "patient_id": "PAT-2026-1001",
    "patient_name": "Eleanor Vance",
    "age": 64,
    "triage_level": "Level 1 - Resuscitation",
    "attending_physician": "Dr. Priya Nair, MD",
    "doctor_specialty": "Cardiology",
    "anomaly_count": 2,
    "min_spo2": 88,
    "max_heart_rate": 138,
    "risk_category": "CRITICAL EMERGENCY"
  }
]
```

---

### 6.4 Pipeline 4: Physician Caseload & ICU Caseload Matrix
* **Purpose:** Correlates physicians with assigned active cases, calculates the critical ICU patient ratio using `$filter` and `$size`, and evaluates physician capacity utilization against quotas.
* **Stages:**
  1. `$lookup`: Foreign key match between `doctors._id` and `patients.assigned_doctor_id`.
  2. `$project`: Evaluates `current_load` via `$size` and calculates `icu_cases` using array `$filter`.
  3. `$sort`: `{ current_load: -1, icu_cases: -1 }`

**Actual Output:**
```json
[
  {
    "doctor_id": "DOC-101",
    "name": "Dr. Sarah Chen, MD",
    "specialization": "Emergency Medicine",
    "shift": "Morning",
    "current_load": 4,
    "icu_cases": 0,
    "utilization_pct": 26.7
  },
  {
    "doctor_id": "DOC-102",
    "name": "Dr. Marcus Brody, MD",
    "specialization": "Critical Care",
    "shift": "Morning",
    "current_load": 2,
    "icu_cases": 2,
    "utilization_pct": 20.0
  }
]
```

---

### 6.5 Pipeline 5: 360° Hospital Command Multi-Stream Performance (`$facet`)
* **Purpose:** Executes 4 analytical streams simultaneously in a single round-trip: triage distributions, status distributions, age demographic intervals using `$bucket`, and financial metrics.

**BSON Pipeline:**
```javascript
db.patients.aggregate([
  {
    "$facet": {
      "triage_distribution": [
        { "$group": { "_id": "$triage_level", "count": { "$sum": 1 } } },
        { "$sort": { "count": -1 } }
      ],
      "status_distribution": [
        { "$group": { "_id": "$status", "count": { "$sum": 1 } } }
      ],
      "age_demographics": [
        {
          "$bucket": {
            "groupBy": "$age",
            "boundaries": [0, 18, 40, 65, 100],
            "default": "Centenarian",
            "output": {
              "count": { "$sum": 1 },
              "avg_age": { "$avg": "$age" }
            }
          }
        },
        {
          "$project": {
            "age_bracket": "$_id",
            "count": 1,
            "avg_age": { "$round": ["$avg_age", 1] }
          }
        }
      ],
      "financial_metrics": [
        {
          "$group": {
            "_id": null,
            "total_billed": { "$sum": "$billing.total_amount" },
            "avg_bill_per_patient": { "$avg": "$billing.total_amount" },
            "insured_patients": {
              "$sum": { "$cond": ["$billing.insurance_covered", 1, 0] }
            },
            "total_cases": { "$sum": 1 }
          }
        },
        {
          "$project": {
            "_id": 0,
            "total_billed": { "$round": ["$total_billed", 2] },
            "avg_bill_per_patient": { "$round": ["$avg_bill_per_patient", 2] },
            "insurance_coverage_pct": {
              "$round": [
                { "$multiply": [{ "$divide": ["$insured_patients", "$total_cases"] }, 100] },
                1
              ]
            }
          }
        }
      ]
    }
  }
])
```

**Actual Output:**
```json
{
  "triage_distribution": [
    {"_id": "Level 2 - Emergent", "count": 4},
    {"_id": "Level 1 - Resuscitation", "count": 2},
    {"_id": "Level 3 - Urgent", "count": 2},
    {"_id": "Level 4 - Less Urgent", "count": 1}
  ],
  "age_demographics": [
    {"age_bracket": 0, "count": 1, "avg_age": 8.0},
    {"age_bracket": 18, "count": 4, "avg_age": 25.8},
    {"age_bracket": 40, "count": 5, "avg_age": 52.2},
    {"age_bracket": 65, "count": 1, "avg_age": 71.0}
  ],
  "financial_metrics": [
    {
      "total_billed": 110850.0,
      "avg_bill_per_patient": 11085.0,
      "insurance_coverage_pct": 81.8
    }
  ]
}
```

---

## 7. System Screenshots & Operation Demonstrations

The following high-resolution captures demonstrate the live execution of all system capabilities:

### Figure 1: Hospital Command Center Overview & Real-Time KPIs
![Figure 1: Hospital Command Center Overview](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/01_command_center_overview.png)
*Description: Live command center displaying database connection telemetry (`pulsecare_hospital_db`, 3.07ms latency), glowing KPI cards (Active Admissions, Critical ICU Patients, Telemetry Anomalies, Available Beds), real-time telemetry anomaly alert feed (Pipeline 3), and ward capacity meters (Pipeline 2).*

---

### Figure 2: Patient Management Directory & CRUD Operations Table
![Figure 2: Patient Directory CRUD Table](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/02_patient_crud_directory.png)
*Description: Patient directory view demonstrating CRUD reading with formatted badges for ESI Triage Levels, clinical statuses, and latest vital readings. The top preview box dynamically outputs the exact PyMongo find query executed against MongoDB.*

---

### Figure 3: Full-Text Regex Search & Multi-Field Filtering
![Figure 3: Search & Filtering](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/03_patient_search_filtering.png)
*Description: Case-insensitive regex query filtering for patient 'Eleanor Vance'. Notice how the query bar reflects `db.patients.find({'$or': [{'name': {'$regex': 'Eleanor', '$options': 'i'}}, ...]}).sort('admission_date', -1)` with instant response times.*

---

### Figure 4: Patient Clinical Chart Modal & Embedded Vitals Timeline
![Figure 4: Patient Clinical Chart Modal](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/04_patient_clinical_chart_vitals.png)
*Description: Deep clinical view of an admitted patient displaying patient demographics, attending physician, assigned ward, recorded allergies, active medication orders, and chronological time-series vitals history retrieved from the embedded array.*

---

### Figure 5: Advanced Aggregation Intelligence Dashboard (5 Pipelines)
![Figure 5: Aggregation Analytics Dashboard](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/05_aggregation_analytics_dashboard.png)
*Description: Interactive visualizer rendering the live outputs of Pipeline 1 (Triage Acuity & Length-of-Stay Analysis), Pipeline 2 (Ward Capacity & Ventilator Utilization Heatmap), Pipeline 3 (Critical Telemetry Risk Detector), Pipeline 4 (Physician Caseload Matrix), and Pipeline 5 (Executive 360° Facet Analytics).*

---

### Figure 6: Aggregation Pipeline BSON Code Inspector
![Figure 6: Aggregation Code Viewer](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/06_aggregation_pipeline_code.png)
*Description: In-app code viewer showing the multi-stage MongoDB BSON aggregation pipeline definition, stage-by-stage descriptions, and PyMongo execution handles.*

---

### Figure 7: Interactive Viva Query Sandbox with Latency Metrics
![Figure 7: Viva Query Sandbox](file:///Users/neerajnegi/Desktop/mongodb_project/reports/screenshots/07_viva_query_sandbox.png)
*Description: Interactive query console enabling evaluators to run custom MongoDB queries live. The screenshot demonstrates the execution of the preset query 'ICU Patients > 30 yrs', returning matched documents in 3.65ms alongside the corresponding PyMongo code.*

---

## 8. Viva & Oral Defense Preparation Guide

### 8.1 Bloom's Taxonomy Level 2 (Understanding) Questions

**Q1: Why was MongoDB chosen over a relational SQL database for patient vitals?**  
*Answer:* Vital telemetry streams are high-frequency and variable across clinical departments. Relational databases require rigid column definitions, resulting in sparse tables with numerous NULL values and requiring expensive SQL `JOIN` operations across millions of rows. MongoDB allows vital readings to be appended directly into an embedded array (`vitals_history`) in a single disk write, providing $O(1)$ single-seek read performance during emergency triage.

**Q2: Explain the trade-offs between Embedding and Referencing in your schema.**  
*Answer:* We adopted a hybrid model. Embedding was chosen for `vitals_history`, `contact`, and `billing` because these entities are 1-to-few, have bounded lifecycles, and are always accessed alongside the patient record. Referencing (using `ObjectId`) was chosen for `doctors` and `wards` because doctors work across multiple shifts and wards have fixed physical capacities. Embedding doctors would lead to data duplication and update anomalies whenever a physician changes shift or contact details.

**Q3: How does the `$unwind` stage work in Pipeline 3?**  
*Answer:* In MongoDB, `$unwind` deconstructs an array field from the input documents to output a document for each element in the array. In Pipeline 3, unwinding `vitals_history` breaks the array into individual vital sign readings. This enables the subsequent `$match` stage to evaluate specific physiological thresholds (`spo2 < 92` or `heart_rate > 120`) and the `$group` stage to compute the lowest recorded SpO2 and highest heart rate per patient.

---

### 8.2 Bloom's Taxonomy Level 3 (Applying & Analyzing) Questions

**Q4: If the examiner asks you to modify a query during the viva:**  
*"Modify your query to find all Female patients in ICU over the age of 50."*  
*PyMongo Command:*
```python
db.patients.find({
    "gender": "Female",
    "status": "ICU",
    "age": {"$gt": 50}
}, {"name": 1, "age": 1, "primary_complaint": 1, "triage_level": 1})
```

**Q5: How does your application ensure database-layer data integrity?**  
*Answer:* Data integrity is enforced at the MongoDB storage engine level using `$jsonSchema` validators defined during collection creation (`db.create_collection("patients", validator=PATIENT_VALIDATOR)`). Any attempt to write a document violating data types, required fields, regex patterns (e.g., `PAT-YYYY-XXXX`), or enum lists is rejected by MongoDB with error code `121` (`Document failed validation`), independent of application-level logic.

**Q6: What is the purpose of `$facet` in Pipeline 5?**  
*Answer:* In high-throughput clinical dashboards, executing multiple round-trip queries over the network introduces latency. The `$facet` stage allows the execution of multiple aggregation pipelines simultaneously within a single stage on the same set of input documents. In PulseCare AI, Pipeline 5 returns triage distributions, status counters, age demographic buckets (`$bucket`), and billing totals in a single round-trip.

---

## 9. Conclusion & Future Enhancements

### 9.1 Summary of Achievements
PulseCare AI successfully satisfies all criteria outlined in **Academic Task 2 (CSE494)**:
1. **Suitable Document Structure (CO4):** Implemented an embedded-referenced hybrid schema tailored for acute hospital encounters.
2. **Schema Validation & CRUD (CO5):** Built database-level `$jsonSchema` validation and atomic PyMongo operations (`$push`, `$set`, `$inc`, `insert_one`, `find`, `delete_one`).
3. **Aggregation Intelligence (CO6):** Developed 5 multi-stage aggregation pipelines providing operational insights into triage acuity, ward capacity, and vital anomalies.
4. **Execution & Demonstration:** Delivered an operational web platform and standalone terminal evaluation suite.

### 9.2 Future Enhancements
* **MongoDB Change Streams:** Implementing real-time WebSocket push notifications from MongoDB change streams to alert nurse stations the instant an SpO2 reading drops below 90%.
* **Time-Series Collections:** Migrating historical vitals to MongoDB Time-Series collections (`timeseries` option with `timeField` and `metaField`) for columnar compression across millions of telemetry data points.
* **Geospatial Sharding:** Sharding patient records across regional healthcare clusters using 2dsphere indexes for multi-hospital network telemetry.
