const user = requireAuth(["admin", "staff"]);
let categories = [];

if (user) {
  renderNav("menu.html");
  init();
}

async function init() {
  await loadCategories();
  await loadMenu();
}

async function loadCategories() {
  try {
    categories = await API.menu.listCategories();
    const select = document.getElementById("item-category");
    select.innerHTML = categories.map((c) => `<option value="${c.id}">${c.name}</option>`).join("");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadMenu() {
  const grid = document.getElementById("menu-grid");
  try {
    const items = await API.menu.list();
    if (items.length === 0) {
      grid.innerHTML = `<div class="empty-state">No menu items yet. Add your first one.</div>`;
      return;
    }
    grid.innerHTML = "";
    items.forEach((item) => grid.appendChild(renderMenuCard(item)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderMenuCard(item) {
  const card = document.createElement("div");
  card.className = "menu-item-card";
  card.innerHTML = `
    <div class="flex justify-between items-center">
      <h3>${item.name}</h3>
      ${!item.is_available ? '<span class="unavailable-tag">Unavailable</span>' : ""}
    </div>
    <p class="desc">${item.description || ""}</p>
    <p class="text-muted" style="font-size:0.78rem">${item.category ? item.category.name : "Uncategorized"}</p>
    <div class="flex justify-between items-center">
      <span class="price">${formatCurrency(item.price)}</span>
      <div class="flex gap-2">
        <button class="btn btn-secondary btn-sm" onclick='openItemModal(${JSON.stringify(item).replace(/'/g, "&#39;")})'>Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteMenuItem(${item.id})">Delete</button>
      </div>
    </div>
  `;
  return card;
}

function openItemModal(item = null) {
  document.getElementById("modal-title").textContent = item ? "Edit menu item" : "Add menu item";
  document.getElementById("item-id").value = item ? item.id : "";
  document.getElementById("item-name").value = item ? item.name : "";
  document.getElementById("item-desc").value = item ? (item.description || "") : "";
  document.getElementById("item-price").value = item ? item.price : "";
  document.getElementById("item-available").checked = item ? item.is_available : true;
  document.getElementById("item-category").value = item && item.category ? item.category.id : (categories[0]?.id || "");
  document.getElementById("item-modal").classList.remove("hidden");
}

function closeItemModal() {
  document.getElementById("item-modal").classList.add("hidden");
}

async function saveMenuItem() {
  const id = document.getElementById("item-id").value;
  const payload = {
    name: document.getElementById("item-name").value.trim(),
    description: document.getElementById("item-desc").value.trim(),
    price: parseFloat(document.getElementById("item-price").value),
    category_id: parseInt(document.getElementById("item-category").value) || null,
    is_available: document.getElementById("item-available").checked,
  };

  if (!payload.name || isNaN(payload.price)) {
    toast("Name and a valid price are required.", "error");
    return;
  }

  try {
    if (id) {
      await API.menu.update(id, payload);
      toast("Menu item updated.", "success");
    } else {
      await API.menu.create(payload);
      toast("Menu item added.", "success");
    }
    closeItemModal();
    loadMenu();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function deleteMenuItem(id) {
  if (!confirm("Remove this item from the menu?")) return;
  try {
    await API.menu.remove(id);
    toast("Item removed.", "success");
    loadMenu();
  } catch (err) {
    toast(err.message, "error");
  }
}
