const user = requireAuth(["admin"]);

if (user) {
  renderNav("employees.html");
  loadEmployees();
}

async function loadEmployees() {
  const body = document.getElementById("employees-body");
  try {
    const employees = await API.employees.list();
    if (employees.length === 0) {
      body.innerHTML = `<tr><td colspan="8" class="empty-state">No employees added yet.</td></tr>`;
      return;
    }
    body.innerHTML = "";
    employees.forEach((emp) => body.appendChild(renderEmployeeRow(emp)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderEmployeeRow(emp) {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${emp.name}</td>
    <td>${emp.email || emp.phone || "—"}</td>
    <td style="text-transform:capitalize">${emp.role}</td>
    <td>${emp.designation}</td>
    <td>${formatCurrency(emp.salary)}</td>
    <td>${emp.date_joined}</td>
    <td>
      <select data-attendance="${emp.id}" class="btn-sm" style="padding:5px 8px; border-radius:6px; border:1px solid var(--color-line)">
        <option value="present">Present</option>
        <option value="absent">Absent</option>
        <option value="leave">On leave</option>
      </select>
    </td>
    <td><button class="btn btn-danger btn-sm" data-remove="${emp.id}">Remove</button></td>
  `;
  tr.querySelector("[data-attendance]").addEventListener("change", (e) => markAttendance(emp.id, e.target.value));
  tr.querySelector("[data-remove]").addEventListener("click", () => removeEmployee(emp.id, emp.name));
  return tr;
}

async function markAttendance(employeeId, status) {
  try {
    await API.employees.markAttendance(employeeId, status);
    toast(`Attendance marked: ${status}.`, "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

function openEmployeeModal() {
  ["emp-name", "emp-email", "emp-phone", "emp-shift"].forEach((id) => (document.getElementById(id).value = ""));
  document.getElementById("emp-designation").value = "Staff";
  document.getElementById("emp-salary").value = "0";
  document.getElementById("emp-role").value = "staff";
  document.getElementById("employee-modal").classList.remove("hidden");
}

function closeEmployeeModal() {
  document.getElementById("employee-modal").classList.add("hidden");
}

async function saveEmployee() {
  const payload = {
    name: document.getElementById("emp-name").value.trim(),
    email: document.getElementById("emp-email").value.trim() || null,
    phone: document.getElementById("emp-phone").value.trim() || null,
    role: document.getElementById("emp-role").value,
    designation: document.getElementById("emp-designation").value.trim() || "Staff",
    salary: parseFloat(document.getElementById("emp-salary").value) || 0,
    shift: document.getElementById("emp-shift").value.trim() || null,
  };

  if (!payload.name) {
    toast("Name is required.", "error");
    return;
  }
  if (!payload.email && !payload.phone) {
    toast("Add an email or phone number so they can log in.", "error");
    return;
  }

  try {
    await API.employees.create(payload);
    toast(`${payload.name} added.`, "success");
    closeEmployeeModal();
    loadEmployees();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function removeEmployee(id, name) {
  if (!confirm(`Remove ${name} and deactivate their account?`)) return;
  try {
    await API.employees.remove(id);
    toast(`${name} removed.`, "success");
    loadEmployees();
  } catch (err) {
    toast(err.message, "error");
  }
}
