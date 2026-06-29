const user = requireAuth(["admin", "staff"]);
let currentFilter = null;
let menuItemsCache = [];
let orderBuilderLines = {}; // menu_item_id -> quantity

if (user) {
  renderNav("orders.html");
  loadOrders();
}

const STATUS_FLOW = ["pending", "preparing", "ready", "served"];

async function loadOrders() {
  const body = document.getElementById("orders-body");
  try {
    const orders = await API.orders.list(currentFilter);
    if (orders.length === 0) {
      body.innerHTML = `<tr><td colspan="8" class="empty-state">No orders found.</td></tr>`;
      return;
    }
    body.innerHTML = "";
    orders.forEach((order) => body.appendChild(renderOrderRow(order)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function filterOrders(status) {
  currentFilter = status;
  loadOrders();
}

function renderOrderRow(order) {
  const tr = document.createElement("tr");
  const itemsSummary = order.items.map((i) => `${i.quantity}× ${i.menu_item_name}`).join(", ");
  const nextStatus = STATUS_FLOW[STATUS_FLOW.indexOf(order.status) + 1];

  tr.innerHTML = `
    <td>#${order.id}</td>
    <td>${order.table_number || "—"}</td>
    <td>${order.order_type.replace("_", " ")}</td>
    <td style="max-width:240px">${itemsSummary}</td>
    <td>${formatCurrency(order.total_amount)}</td>
    <td><span class="badge badge-${order.status}">${order.status}</span></td>
    <td>${formatDate(order.created_at)}</td>
    <td>
      ${nextStatus ? `<button class="btn btn-secondary btn-sm" data-advance="${order.id}" data-next="${nextStatus}">Mark ${nextStatus}</button>` : ""}
      ${order.status !== "cancelled" && order.status !== "served" ? `<button class="btn btn-danger btn-sm" data-cancel="${order.id}">Cancel</button>` : ""}
    </td>
  `;

  const advanceBtn = tr.querySelector("[data-advance]");
  if (advanceBtn) advanceBtn.addEventListener("click", () => updateStatus(order.id, nextStatus));
  const cancelBtn = tr.querySelector("[data-cancel]");
  if (cancelBtn) cancelBtn.addEventListener("click", () => updateStatus(order.id, "cancelled"));

  return tr;
}

async function updateStatus(orderId, status) {
  try {
    await API.orders.updateStatus(orderId, status);
    toast(`Order #${orderId} marked ${status}.`, "success");
    loadOrders();
  } catch (err) {
    toast(err.message, "error");
  }
}

/* ---------------- New order modal ---------------- */

async function openNewOrderModal() {
  document.getElementById("order-modal").classList.remove("hidden");
  document.getElementById("order-table").value = "";
  document.getElementById("order-notes").value = "";
  orderBuilderLines = {};

  const builder = document.getElementById("order-items-builder");
  builder.innerHTML = "Loading menu…";
  try {
    menuItemsCache = await API.menu.list({ available_only: true });
    if (menuItemsCache.length === 0) {
      builder.innerHTML = `<p class="text-muted">No available menu items. Add some on the Menu page first.</p>`;
      return;
    }
    builder.innerHTML = "";
    menuItemsCache.forEach((item) => builder.appendChild(renderBuilderLine(item)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderBuilderLine(item) {
  const row = document.createElement("div");
  row.className = "flex justify-between items-center";
  row.innerHTML = `
    <div>
      <div style="font-weight:600">${item.name}</div>
      <div class="text-muted" style="font-size:0.8rem">${formatCurrency(item.price)}</div>
    </div>
    <div class="qty-stepper">
      <button type="button" data-dec="${item.id}">−</button>
      <span id="qty-${item.id}">0</span>
      <button type="button" data-inc="${item.id}">+</button>
    </div>
  `;
  row.querySelector(`[data-inc="${item.id}"]`).addEventListener("click", () => changeQty(item.id, 1));
  row.querySelector(`[data-dec="${item.id}"]`).addEventListener("click", () => changeQty(item.id, -1));
  return row;
}

function changeQty(itemId, delta) {
  const current = orderBuilderLines[itemId] || 0;
  const next = Math.max(0, current + delta);
  orderBuilderLines[itemId] = next;
  document.getElementById(`qty-${itemId}`).textContent = next;
}

function closeNewOrderModal() {
  document.getElementById("order-modal").classList.add("hidden");
}

async function submitNewOrder() {
  const items = Object.entries(orderBuilderLines)
    .filter(([, qty]) => qty > 0)
    .map(([menu_item_id, quantity]) => ({ menu_item_id: parseInt(menu_item_id), quantity }));

  if (items.length === 0) {
    toast("Add at least one item to the order.", "error");
    return;
  }

  const payload = {
    table_number: document.getElementById("order-table").value.trim() || null,
    order_type: document.getElementById("order-type").value,
    notes: document.getElementById("order-notes").value.trim() || null,
    items,
  };

  try {
    const order = await API.orders.create(payload);
    toast(`Order #${order.id} placed.`, "success");
    closeNewOrderModal();
    loadOrders();
  } catch (err) {
    toast(err.message, "error");
  }
}
