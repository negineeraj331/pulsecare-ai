/**
 * PulseCare AI - Frontend Interactive Controller
 * Enterprise Clinical Telemetry & Resource Intelligence Platform
 */

// Global State
let currentPatients = [];
let doctorsList = [];
let wardsList = [];
let selectedPatient = null;

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  fetchHealthStatus();
  fetchDoctorsAndWards();
  loadOverviewData();
  loadPatients();

  // Search and filter listeners
  document.getElementById("patientSearchInput")?.addEventListener("input", debounce(filterPatients, 300));
  document.getElementById("triageFilterSelect")?.addEventListener("change", filterPatients);
  document.getElementById("statusFilterSelect")?.addEventListener("change", filterPatients);
});

// Utility Debounce
function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// -------------------------------------------------------------
// Navigation Tabs
// -------------------------------------------------------------
function initTabs() {
  const tabButtons = document.querySelectorAll(".nav-tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }

      // Trigger data loads on specific tabs
      if (targetId === "tab-analytics") {
        loadAnalyticsPipelines();
      } else if (targetId === "tab-overview") {
        loadOverviewData();
      }
    });
  });
}

// -------------------------------------------------------------
// System Health
// -------------------------------------------------------------
async function fetchHealthStatus() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (data.connected) {
      document.getElementById("mongoStatusPill").innerHTML = `
        <span class="pulse-dot"></span>
        <span>Telemetry Ingestion Active (${data.latency_ms}ms)</span>
      `;
    } else {
      document.getElementById("mongoStatusPill").innerHTML = `
        <span class="pulse-dot" style="background:#f43f5e; box-shadow:0 0 10px #f43f5e"></span>
        <span>MongoDB Disconnected</span>
      `;
    }
  } catch (err) {
    console.error("Health check error:", err);
  }
}

async function fetchDoctorsAndWards() {
  try {
    const [docsRes, wardsRes] = await Promise.all([
      fetch("/api/doctors"),
      fetch("/api/wards")
    ]);
    const docsData = await docsRes.json();
    const wardsData = await wardsRes.json();

    if (docsData.success) doctorsList = docsData.data;
    if (wardsData.success) wardsList = wardsData.data;

    populateFormSelects();
  } catch (err) {
    console.error("Error fetching references:", err);
  }
}

function populateFormSelects() {
  const docSelect = document.getElementById("admitDoctorSelect");
  if (docSelect) {
    docSelect.innerHTML = `<option value="">Select Specialist</option>` +
      doctorsList.map(d => `<option value="${d._id}">${d.name} (${d.specialization})</option>`).join("");
  }

  const wardSelect = document.getElementById("admitWardSelect");
  if (wardSelect) {
    wardSelect.innerHTML = `<option value="">Select Ward / Unit</option>` +
      wardsList.map(w => `<option value="${w._id}" data-type="${w.ward_type}" data-name="${w.name}">${w.name} [${w.ward_type}] (${w.occupied_beds}/${w.total_beds} beds)</option>`).join("");
  }
}

// -------------------------------------------------------------
// Overview Dashboard Data
// -------------------------------------------------------------
async function loadOverviewData() {
  try {
    const [triageRes, wardsRes, anomaliesRes, execRes] = await Promise.all([
      fetch("/api/analytics/triage"),
      fetch("/api/analytics/wards"),
      fetch("/api/analytics/anomalies"),
      fetch("/api/analytics/executive")
    ]);

    const triage = await triageRes.json();
    const wards = await wardsRes.json();
    const anomalies = await anomaliesRes.json();
    const exec = await execRes.json();

    // Update KPI Cards
    const totalPatients = (exec.data && exec.data.status_distribution) 
      ? exec.data.status_distribution.reduce((acc, curr) => acc + curr.count, 0)
      : 10;
    
    const icuCount = (exec.data && exec.data.status_distribution)
      ? (exec.data.status_distribution.find(s => s._id === "ICU")?.count || 0)
      : 0;

    document.getElementById("kpiTotalAdmissions").innerText = totalPatients;
    document.getElementById("kpiIcuActive").innerText = icuCount;
    document.getElementById("kpiAnomalies").innerText = anomalies.data?.length || 0;

    // Calculate total available beds across all wards
    const freeBeds = wards.data?.reduce((acc, w) => acc + (w.available_beds || 0), 0) || 0;
    document.getElementById("kpiBedsFree").innerText = freeBeds;

    // Render Recent Critical Telemetry Feed
    renderOverviewAnomalies(anomalies.data || []);

    // Render Ward Capacity snapshot
    renderOverviewWards(wards.data || []);
  } catch (err) {
    console.error("Error loading overview data:", err);
  }
}

function renderOverviewAnomalies(anomalies) {
  const container = document.getElementById("overviewAnomalyFeed");
  if (!container) return;

  if (anomalies.length === 0) {
    container.innerHTML = `<div style="padding:1.5rem; text-align:center; color:var(--text-dim)">No active critical telemetry anomalies detected.</div>`;
    return;
  }

  container.innerHTML = anomalies.slice(0, 4).map(a => `
    <div style="display:flex; align-items:center; justify-content:space-between; padding:0.9rem 1.25rem; border-bottom:1px solid rgba(255,255,255,0.05)">
      <div>
        <div style="font-weight:700; font-size:0.9rem; display:flex; align-items:center; gap:0.5rem">
          <span>${a.patient_name}</span>
          <span style="font-size:0.75rem; color:var(--text-dim); font-family:var(--font-mono)">${a.patient_id}</span>
        </div>
        <div style="font-size:0.78rem; color:var(--text-muted); margin-top:2px">${a.primary_complaint}</div>
      </div>
      <div style="text-align:right">
        <span class="triage-badge ${a.risk_category === 'CRITICAL EMERGENCY' ? 'triage-level-1' : 'triage-level-2'}">${a.risk_category}</span>
        <div style="font-family:var(--font-mono); font-size:0.78rem; margin-top:4px">
          SpO2: <b style="color:${a.min_spo2 < 90 ? '#f43f5e' : '#38bdf8'}">${a.min_spo2}%</b> | 
          HR: <b style="color:${a.max_heart_rate > 125 ? '#f43f5e' : '#38bdf8'}">${a.max_heart_rate} bpm</b>
        </div>
      </div>
    </div>
  `).join("");
}

function renderOverviewWards(wards) {
  const container = document.getElementById("overviewWardList");
  if (!container) return;

  container.innerHTML = wards.map(w => `
    <div style="padding:0.9rem 1.25rem; border-bottom:1px solid rgba(255,255,255,0.05)">
      <div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:600; margin-bottom:0.35rem">
        <span>${w.name} (${w.ward_type})</span>
        <span style="color:var(--cyan-glow); font-family:var(--font-mono)">${w.occupancy_rate}% occupied</span>
      </div>
      <div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px; overflow:hidden">
        <div style="background:${w.occupancy_rate > 80 ? '#f43f5e' : 'var(--cyan-glow)'}; height:100%; width:${w.occupancy_rate}%"></div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:0.74rem; color:var(--text-dim); margin-top:4px">
        <span>${w.available_beds} beds free / ${w.total_beds} total</span>
        <span>Ventilators: ${w.ventilators_available} available</span>
      </div>
    </div>
  `).join("");
}

// -------------------------------------------------------------
// Patients Directory (CRUD)
// -------------------------------------------------------------
async function loadPatients() {
  const search = document.getElementById("patientSearchInput")?.value || "";
  const triage = document.getElementById("triageFilterSelect")?.value || "";
  const status = document.getElementById("statusFilterSelect")?.value || "";

  const queryParams = new URLSearchParams();
  if (search) queryParams.append("search", search);
  if (triage) queryParams.append("triage_level", triage);
  if (status) queryParams.append("status", status);

  try {
    const res = await fetch(`/api/patients?${queryParams.toString()}`);
    const data = await res.json();
    if (data.success) {
      currentPatients = data.data;
      renderPatientsTable(currentPatients);
      
      // Update PyMongo code preview banner
      const codeBox = document.getElementById("patientQueryCode");
      if (codeBox) {
        codeBox.innerText = data.pymongo_code + `  # (${data.count} matches, ${data.execution_time_ms}ms)`;
      }
    }
  } catch (err) {
    console.error("Error loading patients:", err);
  }
}

function filterPatients() {
  loadPatients();
}

function renderPatientsTable(patients) {
  const tbody = document.getElementById("patientsTableBody");
  if (!tbody) return;

  if (patients.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--text-dim)">No matching clinical patient records found.</td></tr>`;
    return;
  }

  tbody.innerHTML = patients.map(p => {
    const latestVitals = (p.vitals_history && p.vitals_history.length > 0)
      ? p.vitals_history[p.vitals_history.length - 1]
      : null;

    const triageClass = getTriageClass(p.triage_level);
    const statusClass = getStatusClass(p.status);

    return `
      <tr>
        <td>
          <div style="font-weight:700; color:var(--text-main); font-size:0.92rem">${p.name}</div>
          <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--cyan-glow)">${p.patient_id}</div>
        </td>
        <td>
          <div>${p.age} yrs / ${p.gender}</div>
          <span style="font-size:0.75rem; color:var(--text-dim)">Blood: <b>${p.blood_group || 'N/A'}</b></span>
        </td>
        <td>
          <span class="triage-badge ${triageClass}">${p.triage_level || 'N/A'}</span>
          <div style="font-size:0.78rem; color:var(--text-muted); margin-top:4px; max-width:220px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis" title="${p.primary_complaint || ''}">
            ${p.primary_complaint || 'No complaint listed'}
          </div>
        </td>
        <td>
          <span class="status-tag ${statusClass}">${p.status}</span>
          <div style="font-size:0.75rem; color:var(--text-dim); margin-top:2px">
            ${p.assigned_ward ? p.assigned_ward.ward_name : 'Unassigned'}
          </div>
        </td>
        <td>
          ${latestVitals ? `
            <div style="font-family:var(--font-mono); font-size:0.8rem">
              HR: <b style="color:${latestVitals.heart_rate > 120 ? '#f43f5e' : '#38bdf8'}">${latestVitals.heart_rate}</b> | 
              SpO2: <b style="color:${latestVitals.spo2 < 92 ? '#f43f5e' : '#10b981'}">${latestVitals.spo2}%</b>
            </div>
            <div style="font-size:0.74rem; color:var(--text-dim)">BP: ${latestVitals.blood_pressure || 'N/A'} | ${latestVitals.temperature}°F</div>
          ` : '<span style="color:var(--text-dim)">No vitals</span>'}
        </td>
        <td>
          <div style="display:flex; gap:0.4rem; flex-wrap:wrap">
            <button class="btn-secondary" style="padding:0.25rem 0.6rem; font-size:0.75rem" onclick="openPatientChart('${p.patient_id}')" title="View Patient Clinical Chart">
              📋 Chart
            </button>
            <button class="btn-secondary" style="padding:0.25rem 0.6rem; font-size:0.75rem" onclick="openPushVitalsModal('${p.patient_id}')" title="Record Bedside Telemetry Vitals">
              🩺 +Vitals
            </button>
            <button class="btn-secondary" style="padding:0.25rem 0.6rem; font-size:0.75rem" onclick="openUpdateStatusModal('${p.patient_id}', '${p.status}', '${p.triage_level}')" title="Update Patient Status">
              ⚙️ Status
            </button>
            ${p.status !== 'Discharged' ? `
              <button class="btn-secondary" style="padding:0.25rem 0.6rem; font-size:0.75rem; color:#fde68a" onclick="dischargePatient('${p.patient_id}')" title="Discharge Patient">
                🚪 Discharge
              </button>
            ` : ''}
            <button class="btn-danger" style="padding:0.25rem 0.5rem" onclick="deletePatient('${p.patient_id}')" title="Delete Patient Record">
              🗑️
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

function getTriageClass(level) {
  if (!level) return "triage-level-5";
  if (level.includes("Level 1")) return "triage-level-1";
  if (level.includes("Level 2")) return "triage-level-2";
  if (level.includes("Level 3")) return "triage-level-3";
  if (level.includes("Level 4")) return "triage-level-4";
  return "triage-level-5";
}

function getStatusClass(status) {
  switch (status) {
    case "ICU": return "status-icu";
    case "Admitted": return "status-admitted";
    case "Triage": return "status-triage";
    case "Under Observation": return "status-observation";
    case "Discharged": return "status-discharged";
    default: return "";
  }
}

// -------------------------------------------------------------
// Admission Modal (Create with $jsonSchema)
// -------------------------------------------------------------
function openAdmitModal() {
  document.getElementById("admitPatientForm").reset();
  document.getElementById("admitModal").classList.add("active");
}

function closeAdmitModal() {
  document.getElementById("admitModal").classList.remove("active");
}

async function handleAdmitPatientSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const wardSelect = form.admitWard;
  const selectedWardOpt = wardSelect.options[wardSelect.selectedIndex];

  let assignedWard = null;
  if (wardSelect.value) {
    assignedWard = {
      ward_id: wardSelect.value,
      ward_name: selectedWardOpt.getAttribute("data-name") || "General Ward",
      ward_type: selectedWardOpt.getAttribute("data-type") || "Emergency",
      bed_number: form.admitBedNumber.value || "ER-01"
    };
  }

  const payload = {
    name: form.admitName.value,
    age: parseInt(form.admitAge.value, 10),
    gender: form.admitGender.value,
    blood_group: form.admitBloodGroup.value,
    triage_level: form.admitTriageLevel.value,
    primary_complaint: form.admitComplaint.value,
    status: form.admitStatus.value,
    contact: {
      phone: form.admitPhone.value,
      emergency_contact: form.admitEmergencyContact.value
    },
    assigned_doctor_id: form.admitDoctor.value || null,
    assigned_ward: assignedWard,
    initial_heart_rate: parseInt(form.admitHeartRate.value || 80, 10),
    initial_spo2: parseInt(form.admitSpO2.value || 98, 10),
    initial_temperature: parseFloat(form.admitTemperature.value || 98.6),
    systolic: parseInt(form.admitSystolic.value || 120, 10),
    diastolic: parseInt(form.admitDiastolic.value || 80, 10),
    allergies: form.admitAllergies.value ? form.admitAllergies.value.split(",").map(s => s.trim()) : []
  };

  try {
    const res = await fetch("/api/patients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.success) {
      showToast(`Patient ${result.patient_id} admitted successfully!`, "success");
      closeAdmitModal();
      loadPatients();
      loadOverviewData();
    } else {
      showToast(`Validation Error: ${result.error}`, "error");
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

// -------------------------------------------------------------
// Push Telemetry Vitals Modal ($push)
// -------------------------------------------------------------
function openPushVitalsModal(patientId) {
  document.getElementById("vitalsPatientId").value = patientId;
  document.getElementById("pushVitalsForm").reset();
  document.getElementById("pushVitalsModal").classList.add("active");
}

function closePushVitalsModal() {
  document.getElementById("pushVitalsModal").classList.remove("active");
}

async function handlePushVitalsSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const patientId = document.getElementById("vitalsPatientId").value;

  const payload = {
    heart_rate: parseInt(form.vitalHeartRate.value, 10),
    spo2: parseInt(form.vitalSpO2.value, 10),
    temperature: parseFloat(form.vitalTemperature.value),
    systolic: parseInt(form.vitalSystolic.value, 10),
    diastolic: parseInt(form.vitalDiastolic.value, 10),
    respiratory_rate: parseInt(form.vitalRespRate.value || 18, 10),
    recorded_by: form.vitalRecordedBy.value || "Bedside Telemetry"
  };

  try {
    const res = await fetch(`/api/patients/${patientId}/vitals`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();

    if (result.success) {
      showToast(result.message, "success");
      closePushVitalsModal();
      loadPatients();
      loadOverviewData();
    } else {
      showToast(`Failed: ${result.error}`, "error");
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

// -------------------------------------------------------------
// Update Status Modal ($set)
// -------------------------------------------------------------
function openUpdateStatusModal(patientId, currentStatus, currentTriage) {
  document.getElementById("updateStatusPatientId").value = patientId;
  document.getElementById("updateStatusSelect").value = currentStatus;
  document.getElementById("updateTriageSelect").value = currentTriage;
  document.getElementById("updateStatusModal").classList.add("active");
}

function closeUpdateStatusModal() {
  document.getElementById("updateStatusModal").classList.remove("active");
}

async function handleUpdateStatusSubmit(e) {
  e.preventDefault();
  const patientId = document.getElementById("updateStatusPatientId").value;
  const status = document.getElementById("updateStatusSelect").value;
  const triage = document.getElementById("updateTriageSelect").value;

  try {
    const res = await fetch(`/api/patients/${patientId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status, triage_level: triage })
    });
    const result = await res.json();

    if (result.success) {
      showToast(result.message, "success");
      closeUpdateStatusModal();
      loadPatients();
      loadOverviewData();
    } else {
      showToast(`Error: ${result.error}`, "error");
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

// -------------------------------------------------------------
// Discharge & Delete Actions
// -------------------------------------------------------------
async function dischargePatient(patientId) {
  if (!confirm(`Are you sure you want to discharge patient ${patientId}? This will free their assigned ward bed via $inc.`)) {
    return;
  }

  try {
    const res = await fetch(`/api/patients/${patientId}/discharge`, { method: "POST" });
    const result = await res.json();
    if (result.success) {
      showToast(result.message, "success");
      loadPatients();
      loadOverviewData();
    } else {
      showToast(`Error: ${result.error}`, "error");
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

async function deletePatient(patientId) {
  if (!confirm(`Permanently remove record ${patientId}? (Uses db.patients.delete_one)`)) {
    return;
  }

  try {
    const res = await fetch(`/api/patients/${patientId}?permanent=true`, { method: "DELETE" });
    const result = await res.json();
    if (result.success) {
      showToast(result.message, "info");
      loadPatients();
      loadOverviewData();
    } else {
      showToast(`Error: ${result.error}`, "error");
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

// -------------------------------------------------------------
// Patient Clinical Chart Drawer
// -------------------------------------------------------------
async function openPatientChart(patientId) {
  try {
    const res = await fetch(`/api/patients/${patientId}`);
    const data = await res.json();
    if (!data.success) {
      showToast("Could not load patient details", "error");
      return;
    }
    const p = data.data;
    selectedPatient = p;

    document.getElementById("chartPatientName").innerText = p.name;
    document.getElementById("chartPatientId").innerText = p.patient_id;
    document.getElementById("chartAgeGender").innerText = `${p.age}y / ${p.gender} (Blood: ${p.blood_group || 'N/A'})`;
    document.getElementById("chartComplaint").innerText = p.primary_complaint || 'N/A';
    document.getElementById("chartDoctor").innerText = p.doctor_details ? `${p.doctor_details.name} [${p.doctor_details.specialization}]` : 'Unassigned';
    document.getElementById("chartWard").innerText = p.ward_details ? `${p.ward_details.name} (Bed: ${p.assigned_ward?.bed_number || 'N/A'})` : 'None';
    
    // Allergies & Meds
    const allergyElem = document.getElementById("chartAllergies");
    allergyElem.innerHTML = (p.allergies && p.allergies.length > 0)
      ? p.allergies.map(a => `<span style="background:rgba(244,63,94,0.15); color:#fda4af; padding:2px 8px; border-radius:4px; font-size:0.75rem; border:1px solid rgba(244,63,94,0.3)">${a}</span>`).join(" ")
      : `<span style="color:var(--text-dim)">None reported (NKDA)</span>`;

    const medsElem = document.getElementById("chartMeds");
    medsElem.innerHTML = (p.current_medications && p.current_medications.length > 0)
      ? p.current_medications.map(m => `<li><b>${m.name}</b> - ${m.dosage} (${m.frequency})</li>`).join("")
      : `<span style="color:var(--text-dim)">No active orders</span>`;

    // Render Vitals History Timeline
    const vitalsTimeline = document.getElementById("chartVitalsTimeline");
    const history = p.vitals_history || [];
    if (history.length === 0) {
      vitalsTimeline.innerHTML = `<div style="color:var(--text-dim)">No telemetry logs available.</div>`;
    } else {
      vitalsTimeline.innerHTML = history.slice().reverse().map((v, i) => `
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); padding:0.85rem; border-radius:8px; margin-bottom:0.6rem">
          <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:var(--text-dim); margin-bottom:4px">
            <span>Entry #${history.length - i} (${v.recorded_by || 'Monitor'})</span>
            <span style="font-family:var(--font-mono)">${new Date(v.recorded_at).toLocaleTimeString()}</span>
          </div>
          <div style="display:flex; gap:1.25rem; font-family:var(--font-mono); font-size:0.85rem">
            <span>Heart Rate: <b style="color:${v.heart_rate > 120 ? '#f43f5e' : '#38bdf8'}">${v.heart_rate} bpm</b></span>
            <span>SpO2: <b style="color:${v.spo2 < 92 ? '#f43f5e' : '#10b981'}">${v.spo2}%</b></span>
            <span>BP: <b>${v.blood_pressure || `${v.systolic}/${v.diastolic}`}</b></span>
            <span>Temp: <b>${v.temperature}°F</b></span>
          </div>
        </div>
      `).join("");
    }

    document.getElementById("patientChartModal").classList.add("active");
  } catch (err) {
    showToast(`Error: ${err.message}`, "error");
  }
}

function closePatientChartModal() {
  document.getElementById("patientChartModal").classList.remove("active");
}

// -------------------------------------------------------------
// Analytics Tab: 5 Aggregation Pipelines
// -------------------------------------------------------------
async function loadAnalyticsPipelines() {
  try {
    const [triageRes, wardsRes, anomaliesRes, workloadRes, execRes] = await Promise.all([
      fetch("/api/analytics/triage"),
      fetch("/api/analytics/wards"),
      fetch("/api/analytics/anomalies"),
      fetch("/api/analytics/workload"),
      fetch("/api/analytics/executive")
    ]);

    const triage = await triageRes.json();
    const wards = await wardsRes.json();
    const anomalies = await anomaliesRes.json();
    const workload = await workloadRes.json();
    const exec = await execRes.json();

    renderPipeline1(triage);
    renderPipeline2(wards);
    renderPipeline3(anomalies);
    renderPipeline4(workload);
    renderPipeline5(exec);
  } catch (err) {
    console.error("Error loading analytics:", err);
  }
}

function renderPipeline1(data) {
  const container = document.getElementById("pipe1Results");
  if (!container) return;

  container.innerHTML = (data.data || []).map(item => `
    <div style="display:flex; align-items:center; justify-content:space-between; padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.05)">
      <div>
        <span class="triage-badge ${getTriageClass(item.triage_level)}">${item.triage_level}</span>
        <div style="font-size:0.75rem; color:var(--text-dim); margin-top:3px">Avg Age: ${item.avg_age} yrs</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:1.1rem; font-weight:800; font-family:var(--font-mono); color:var(--cyan-glow)">${item.total_patients} Patients</div>
        <div style="font-size:0.75rem; color:var(--text-muted)">Avg Length of Stay: <b>${item.avg_stay_hours} hrs</b></div>
      </div>
    </div>
  `).join("");

  document.getElementById("pipe1Code").innerText = JSON.stringify(data.pipeline, null, 2);
}

function renderPipeline2(data) {
  const container = document.getElementById("pipe2Results");
  if (!container) return;

  container.innerHTML = (data.data || []).map(w => `
    <div style="padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.05)">
      <div style="display:flex; justify-content:space-between; margin-bottom:4px">
        <span style="font-weight:700; font-size:0.9rem">${w.name} [${w.ward_type}]</span>
        <span style="font-family:var(--font-mono); color:${w.occupancy_rate > 75 ? '#f43f5e' : 'var(--cyan-glow)'}">${w.occupancy_rate}% Full</span>
      </div>
      <div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px; overflow:hidden">
        <div style="background:${w.occupancy_rate > 75 ? '#f43f5e' : 'var(--cyan-glow)'}; height:100%; width:${w.occupancy_rate}%"></div>
      </div>
      <div style="display:flex; justify-content:space-between; font-size:0.74rem; color:var(--text-dim); margin-top:4px">
        <span>Active Cases: ${w.active_patients_count} | Available Beds: ${w.available_beds} of ${w.total_beds}</span>
        <span>Ventilators: ${w.ventilators_available}</span>
      </div>
    </div>
  `).join("");

  document.getElementById("pipe2Code").innerText = JSON.stringify(data.pipeline, null, 2);
}

function renderPipeline3(data) {
  const container = document.getElementById("pipe3Results");
  if (!container) return;

  container.innerHTML = (data.data || []).map(a => `
    <div style="padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center">
      <div>
        <div style="font-weight:700">${a.patient_name} <span style="font-size:0.75rem; color:var(--text-dim)">(${a.patient_id})</span></div>
        <div style="font-size:0.78rem; color:var(--text-muted)">Physician: ${a.attending_physician || 'None'} (${a.doctor_specialty || 'General'})</div>
      </div>
      <div style="text-align:right">
        <span class="triage-badge ${a.risk_category === 'CRITICAL EMERGENCY' ? 'triage-level-1' : 'triage-level-2'}">${a.risk_category}</span>
        <div style="font-family:var(--font-mono); font-size:0.78rem; margin-top:3px">
          Lowest SpO2: <b style="color:#f43f5e">${a.min_spo2}%</b> | Peak HR: <b style="color:#f43f5e">${a.max_heart_rate} bpm</b>
        </div>
      </div>
    </div>
  `).join("");

  document.getElementById("pipe3Code").innerText = JSON.stringify(data.pipeline, null, 2);
}

function renderPipeline4(data) {
  const container = document.getElementById("pipe4Results");
  if (!container) return;

  container.innerHTML = (data.data || []).map(doc => `
    <div style="padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.05)">
      <div style="display:flex; justify-content:space-between">
        <div>
          <span style="font-weight:700">${doc.name}</span>
          <span style="font-size:0.75rem; color:var(--text-dim)"> | ${doc.specialization} (${doc.shift} Shift)</span>
        </div>
        <span style="font-family:var(--font-mono); font-size:0.8rem; color:var(--cyan-glow)">${doc.current_load} / ${doc.max_active_patients} cases (${doc.utilization_pct}%)</span>
      </div>
      <div style="font-size:0.74rem; color:var(--text-muted); margin-top:2px">
        ICU Critical Cases Handled: <b style="color:${doc.icu_cases > 0 ? '#fda4af' : 'var(--text-dim)'}">${doc.icu_cases}</b>
      </div>
    </div>
  `).join("");

  document.getElementById("pipe4Code").innerText = JSON.stringify(data.pipeline, null, 2);
}

function renderPipeline5(data) {
  const container = document.getElementById("pipe5Results");
  if (!container) return;

  const fin = data.data?.financial_metrics?.[0] || {};
  const ages = data.data?.age_demographics || [];

  container.innerHTML = `
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; padding:1rem">
      <div style="background:rgba(255,255,255,0.03); padding:1rem; border-radius:8px">
        <div style="font-size:0.75rem; color:var(--text-dim); text-transform:uppercase">Total Incurred Revenue</div>
        <div style="font-size:1.6rem; font-weight:800; font-family:var(--font-mono); color:#10b981">$${(fin.total_billed || 0).toLocaleString()}</div>
        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px">
          Avg/Case: <b>$${(fin.avg_bill_per_patient || 0).toLocaleString()}</b> | Insured: <b>${fin.insurance_coverage_pct || 0}%</b>
        </div>
      </div>

      <div style="background:rgba(255,255,255,0.03); padding:1rem; border-radius:8px">
        <div style="font-size:0.75rem; color:var(--text-dim); text-transform:uppercase">Age Demographics ($bucket)</div>
        <div style="margin-top:0.4rem; font-size:0.8rem">
          ${ages.map(a => `
            <div style="display:flex; justify-content:space-between; margin-bottom:2px">
              <span>Bracket: <b>${a.age_bracket}</b> (${a.avg_age} avg age)</span>
              <span style="font-family:var(--font-mono); color:var(--cyan-glow)">${a.count} patients</span>
            </div>
          `).join("")}
        </div>
      </div>
    </div>
  `;

  document.getElementById("pipe5Code").innerText = JSON.stringify(data.pipeline, null, 2);
}

function toggleCodeAccordion(id) {
  const elem = document.getElementById(id);
  if (elem) {
    elem.classList.toggle("open");
  }
}

// -------------------------------------------------------------
// Interactive Query Sandbox (Prof / Viva Sandbox)
// -------------------------------------------------------------
function setSandboxPreset(preset) {
  const editor = document.getElementById("sandboxQueryInput");
  const typeSelect = document.getElementById("sandboxQueryType");
  const colSelect = document.getElementById("sandboxCollection");

  if (preset === "icu_critical") {
    typeSelect.value = "find";
    colSelect.value = "patients";
    editor.value = JSON.stringify({
      "filter": { "status": "ICU", "age": { "$gt": 30 } },
      "projection": { "name": 1, "age": 1, "primary_complaint": 1, "triage_level": 1, "vitals_history": { "$slice": -1 } }
    }, null, 2);
  } else if (preset === "penicillin_allergy") {
    typeSelect.value = "find";
    colSelect.value = "patients";
    editor.value = JSON.stringify({
      "filter": { "allergies": "Penicillin" },
      "projection": { "name": 1, "patient_id": 1, "allergies": 1, "status": 1 }
    }, null, 2);
  } else if (preset === "blood_group_agg") {
    typeSelect.value = "aggregate";
    colSelect.value = "patients";
    editor.value = JSON.stringify({
      "pipeline": [
        { "$group": { "_id": "$blood_group", "count": { "$sum": 1 }, "avg_age": { "$avg": "$age" } } },
        { "$sort": { "count": -1 } }
      ]
    }, null, 2);
  } else if (preset === "ventilator_deficit") {
    typeSelect.value = "find";
    colSelect.value = "wards";
    editor.value = JSON.stringify({
      "filter": { "ventilators_available": { "$lte": 3 } },
      "projection": { "name": 1, "ward_type": 1, "total_beds": 1, "ventilators_available": 1 }
    }, null, 2);
  }
}

async function executeSandboxQuery() {
  const queryType = document.getElementById("sandboxQueryType").value;
  const collection = document.getElementById("sandboxCollection").value;
  const editorValue = document.getElementById("sandboxQueryInput").value;
  const outputElem = document.getElementById("sandboxResultsJson");
  const codeElem = document.getElementById("sandboxPyMongoCode");
  const metaElem = document.getElementById("sandboxMetaInfo");

  let parsedBody = {};
  try {
    parsedBody = JSON.parse(editorValue);
  } catch (e) {
    showToast("Invalid JSON syntax in query editor!", "error");
    return;
  }

  parsedBody.type = queryType;
  parsedBody.collection = collection;

  outputElem.innerText = "Executing query against MongoDB...";

  try {
    const res = await fetch("/api/sandbox/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(parsedBody)
    });
    const result = await res.json();

    if (result.success) {
      metaElem.innerText = `Matched: ${result.count} documents | Latency: ${result.execution_time_ms} ms`;
      codeElem.innerText = result.pymongo_code;
      outputElem.innerText = JSON.stringify(result.results, null, 2);
    } else {
      metaElem.innerText = "Execution Failed";
      codeElem.innerText = "# Error in query execution";
      outputElem.innerText = result.error;
    }
  } catch (err) {
    outputElem.innerText = "Error: " + err.message;
  }
}

// -------------------------------------------------------------
// Live Schema Validation Test Demonstration
// -------------------------------------------------------------
async function triggerValidationTest() {
  const outputBox = document.getElementById("validationResultBox");
  outputBox.innerHTML = `<span style="color:var(--cyan-glow)">Sending malformed document (age=250, invalid triage, missing fields)...</span>`;

  try {
    const res = await fetch("/api/validation-test", { method: "POST" });
    const result = await res.json();

    if (!result.passed_validation) {
      outputBox.innerHTML = `
        <div style="color:#10b981; font-weight:700; margin-bottom:0.5rem">
          ✔ PASSED: MongoDB $jsonSchema successfully REJECTED the illegal document!
        </div>
        <div style="color:#fda4af; margin-bottom:0.5rem">
          <b>Error Type:</b> ${result.error_type}
        </div>
        <div style="color:var(--text-muted); font-size:0.8rem; margin-bottom:0.75rem">
          ${result.explanation}
        </div>
        <pre style="background:#060911; padding:0.75rem; border-radius:6px; color:#a5f3fc; font-size:0.75rem; overflow-x:auto">${JSON.stringify(result.details, null, 2)}</pre>
      `;
      showToast("MongoDB Schema Validation Enforced!", "success");
    } else {
      outputBox.innerHTML = `<span style="color:#f43f5e">Unexpected: Document passed without rejection!</span>`;
    }
  } catch (err) {
    outputBox.innerText = "Error: " + err.message;
  }
}

// -------------------------------------------------------------
// Reseed Database
// -------------------------------------------------------------
async function resetDatabase() {
  if (!confirm("Reset database to original sample emergency hospital records?")) return;

  try {
    const res = await fetch("/api/reset-data", { method: "POST" });
    const result = await res.json();
    if (result.success) {
      showToast("Database refreshed and reseeded successfully!", "success");
      loadPatients();
      loadOverviewData();
      fetchHealthStatus();
    }
  } catch (err) {
    showToast("Error resetting database: " + err.message, "error");
  }
}

// -------------------------------------------------------------
// Toast Notification Utility
// -------------------------------------------------------------
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✔' : type === 'error' ? '✖' : 'ℹ'}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
