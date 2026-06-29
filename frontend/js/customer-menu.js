const user = requireAuth(["customer"]);
let cart = {}; // menu_item_id -> { item, quantity }

if (user) {
  renderNav("customer-menu.html");
  loadMenu();
}

async function loadMenu() {
  const grid = document.getElementById("customer-menu-grid");
  try {
    const items = await API.menu.list({ available_only: true });
    if (items.length === 0) {
      grid.innerHTML = `<div class="empty-state">The menu is empty right now — check back soon.</div>`;
      return;
    }
    grid.innerHTML = "";
    items.forEach((item) => grid.appendChild(renderItemCard(item)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderItemCard(item) {
  const card = document.createElement("div");
  card.className = "menu-item-card";
  card.innerHTML = `
    <h3>${item.name}</h3>
    <p class="desc">${item.description || ""}</p>
    <div class="flex justify-between items-center">
      <span class="price">${formatCurrency(item.price)}</span>
      <div class="qty-stepper">
        <button type="button" data-dec="${item.id}">−</button>
        <span id="cust-qty-${item.id}">0</span>
        <button type="button" data-inc="${item.id}">+</button>
      </div>
    </div>
  `;
  card.querySelector(`[data-inc="${item.id}"]`).addEventListener("click", () => changeCartQty(item, 1));
  card.querySelector(`[data-dec="${item.id}"]`).addEventListener("click", () => changeCartQty(item, -1));
  return card;
}

function changeCartQty(item, delta) {
  const existing = cart[item.id] || { item, quantity: 0 };
  existing.quantity = Math.max(0, existing.quantity + delta);
  if (existing.quantity === 0) delete cart[item.id];
  else cart[item.id] = existing;

  const qtyLabel = document.getElementById(`cust-qty-${item.id}`);
  if (qtyLabel) qtyLabel.textContent = existing.quantity || 0;

  renderCart();
}

function renderCart() {
  const itemsContainer = document.getElementById("cart-items");
  const entries = Object.values(cart);

  document.getElementById("cart-count").textContent = `${entries.reduce((sum, e) => sum + e.quantity, 0)} items`;
  document.getElementById("place-order-btn").disabled = entries.length === 0;

  if (entries.length === 0) {
    itemsContainer.innerHTML = `<p class="text-muted" style="font-size:0.85rem">Your cart is empty.</p>`;
    document.getElementById("cart-total").textContent = formatCurrency(0);
    return;
  }

  let total = 0;
  itemsContainer.innerHTML = "";
  entries.forEach(({ item, quantity }) => {
    total += item.price * quantity;
    const line = document.createElement("div");
    line.className = "cart-line";
    line.innerHTML = `<span>${quantity}× ${item.name}</span><span>${formatCurrency(item.price * quantity)}</span>`;
    itemsContainer.appendChild(line);
  });
  document.getElementById("cart-total").textContent = formatCurrency(total);
}

async function placeOrder() {
  const entries = Object.values(cart);
  if (entries.length === 0) return;

  const payload = {
    order_type: "takeaway",
    items: entries.map(({ item, quantity }) => ({ menu_item_id: item.id, quantity })),
  };

  const btn = document.getElementById("place-order-btn");
  btn.disabled = true;
  try {
    const order = await API.orders.create(payload);
    toast(`Order #${order.id} placed! We'll let you know when it's ready.`, "success");
    cart = {};
    renderCart();
    loadMenu(); // reset quantity steppers
  } catch (err) {
    toast(err.message, "error");
    btn.disabled = false;
  }
}
