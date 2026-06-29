const user = requireAuth(["admin", "staff"]);

if (user) {
  renderNav("billing.html");
  loadBills();
}

async function loadBills() {
  const body = document.getElementById("bills-body");
  const unpaidOnly = document.getElementById("unpaid-only-toggle").checked;
  try {
    const bills = await API.bills.list(unpaidOnly);
    if (bills.length === 0) {
      body.innerHTML = `<tr><td colspan="8" class="empty-state">No bills found.</td></tr>`;
      return;
    }
    body.innerHTML = "";
    bills.forEach((bill) => body.appendChild(renderBillRow(bill)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderBillRow(bill) {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>#${bill.id}</td>
    <td>#${bill.order_id}</td>
    <td>${formatCurrency(bill.subtotal)}</td>
    <td>${formatCurrency(bill.tax_amount)}</td>
    <td>${formatCurrency(bill.discount_amount)}</td>
    <td style="font-weight:700">${formatCurrency(bill.total_amount)}</td>
    <td>
      <span class="badge ${bill.is_paid ? "badge-ready" : "badge-pending"}">
        ${bill.is_paid ? "Paid" : "Unpaid"}${bill.payment_method ? " · " + bill.payment_method : ""}
      </span>
    </td>
    <td>
      ${!bill.is_paid ? `<button class="btn btn-primary btn-sm" data-mark-paid="${bill.id}">Mark paid</button>` : ""}
    </td>
  `;
  const markPaidBtn = tr.querySelector("[data-mark-paid]");
  if (markPaidBtn) {
    markPaidBtn.addEventListener("click", () => markBillPaid(bill.id, bill.payment_method));
  }
  return tr;
}

async function markBillPaid(billId, paymentMethod) {
  try {
    await API.bills.updatePayment(billId, true, paymentMethod || "cash");
    toast(`Bill #${billId} marked as paid.`, "success");
    loadBills();
  } catch (err) {
    toast(err.message, "error");
  }
}

function openGenerateBillModal() {
  document.getElementById("bill-order-id").value = "";
  document.getElementById("bill-tax").value = "5";
  document.getElementById("bill-discount").value = "0";
  document.getElementById("bill-modal").classList.remove("hidden");
}

function closeGenerateBillModal() {
  document.getElementById("bill-modal").classList.add("hidden");
}

async function submitGenerateBill() {
  const order_id = parseInt(document.getElementById("bill-order-id").value);
  if (!order_id) {
    toast("Enter a valid order ID.", "error");
    return;
  }
  const payload = {
    order_id,
    tax_percent: parseFloat(document.getElementById("bill-tax").value) || 0,
    discount_amount: parseFloat(document.getElementById("bill-discount").value) || 0,
    payment_method: document.getElementById("bill-payment-method").value,
  };
  try {
    const bill = await API.bills.create(payload);
    toast(`Bill #${bill.id} generated for order #${order_id}.`, "success");
    closeGenerateBillModal();
    loadBills();
  } catch (err) {
    toast(err.message, "error");
  }
}
