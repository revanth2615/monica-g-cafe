const user = requireAuth(["admin", "staff", "kitchen"]);

if (user) {
  renderNav("kitchen.html");
  loadQueue();
  setInterval(loadQueue, 20000); // auto-refresh every 20s
}

async function loadQueue() {
  const grid = document.getElementById("kitchen-grid");
  try {
    const orders = await API.orders.kitchenQueue();
    if (orders.length === 0) {
      grid.innerHTML = `<div class="empty-state">No active orders right now. 🎉</div>`;
      return;
    }
    grid.innerHTML = "";
    orders.forEach((order) => grid.appendChild(renderTicket(order)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderTicket(order) {
  const div = document.createElement("div");
  div.className = `ticket ${order.status}`;
  const itemsHtml = order.items
    .map((i) => `<li>${i.quantity}× ${i.menu_item_name}${i.special_request ? ` <span class="meta">(${i.special_request})</span>` : ""}</li>`)
    .join("");

  const nextAction = order.status === "pending"
    ? { label: "Start preparing", next: "preparing" }
    : { label: "Mark ready", next: "ready" };

  div.innerHTML = `
    <h3>#${order.id} <span class="badge badge-${order.status}">${order.status}</span></h3>
    <p class="meta">${order.table_number ? "Table " + order.table_number : order.order_type.replace("_", " ")} · ${formatDate(order.created_at)}</p>
    <ul>${itemsHtml}</ul>
    ${order.notes ? `<p class="meta">Note: ${order.notes}</p>` : ""}
    <button class="btn btn-primary btn-sm btn-block" data-advance>${nextAction.label}</button>
  `;
  div.querySelector("[data-advance]").addEventListener("click", () => advance(order.id, nextAction.next));
  return div;
}

async function advance(orderId, nextStatus) {
  try {
    await API.orders.updateStatus(orderId, nextStatus);
    toast(`Order #${orderId} marked ${nextStatus}.`, "success");
    loadQueue();
  } catch (err) {
    toast(err.message, "error");
  }
}
