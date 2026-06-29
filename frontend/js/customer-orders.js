const user = requireAuth(["customer"]);

if (user) {
  renderNav("customer-orders.html");
  loadMyOrders();
}

async function loadMyOrders() {
  const list = document.getElementById("my-orders-list");
  try {
    const orders = await API.orders.list();
    if (orders.length === 0) {
      list.innerHTML = `<div class="empty-state">You haven't placed any orders yet.</div>`;
      return;
    }
    list.innerHTML = "";
    orders.forEach((order) => list.appendChild(renderOrderCard(order)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderOrderCard(order) {
  const card = document.createElement("div");
  card.className = "card";
  const itemsHtml = order.items.map((i) => `<li>${i.quantity}× ${i.menu_item_name} — ${formatCurrency(i.subtotal)}</li>`).join("");
  card.innerHTML = `
    <div class="flex justify-between items-center">
      <h3>Order #${order.id}</h3>
      <span class="badge badge-${order.status}">${order.status}</span>
    </div>
    <p class="text-muted" style="font-size:0.82rem; margin:6px 0">${formatDate(order.created_at)} · ${order.order_type.replace("_", " ")}</p>
    <ul style="padding-left:18px; font-size:0.9rem">${itemsHtml}</ul>
    <div class="flex justify-between" style="margin-top:10px; font-weight:700">
      <span>Total</span><span>${formatCurrency(order.total_amount)}</span>
    </div>
  `;
  return card;
}
