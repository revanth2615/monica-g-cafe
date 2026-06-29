const user = requireAuth(["admin", "staff"]);

if (user) {
  renderNav("inventory.html");
  loadInventory();
}

async function loadInventory() {
  const body = document.getElementById("inventory-body");
  const lowStockOnly = document.getElementById("low-stock-toggle").checked;
  try {
    const items = await API.inventory.list(lowStockOnly);
    if (items.length === 0) {
      body.innerHTML = `<tr><td colspan="6" class="empty-state">No inventory items found.</td></tr>`;
      return;
    }
    body.innerHTML = "";
    items.forEach((item) => body.appendChild(renderInventoryRow(item)));
  } catch (err) {
    toast(err.message, "error");
  }
}

function renderInventoryRow(item) {
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${item.name}</td>
    <td>${item.quantity_in_stock} ${item.unit}</td>
    <td>${item.reorder_level} ${item.unit}</td>
    <td>${formatCurrency(item.cost_per_unit)}</td>
    <td><span class="badge ${item.is_low_stock ? "badge-cancelled" : "badge-ready"}">${item.is_low_stock ? "Low stock" : "OK"}</span></td>
    <td>
      <button class="btn btn-secondary btn-sm" data-restock="${item.id}">Adjust</button>
      <button class="btn btn-danger btn-sm" data-delete="${item.id}">Delete</button>
    </td>
  `;
  tr.querySelector("[data-restock]").addEventListener("click", () => openRestockModal(item.id, item.name));
  tr.querySelector("[data-delete]").addEventListener("click", () => deleteInventoryItem(item.id, item.name));
  return tr;
}

function openInventoryModal() {
  ["inv-name", "inv-unit"].forEach((id) => (document.getElementById(id).value = ""));
  document.getElementById("inv-qty").value = "0";
  document.getElementById("inv-reorder").value = "5";
  document.getElementById("inv-cost").value = "0";
  document.getElementById("inventory-modal").classList.remove("hidden");
}

function closeInventoryModal() {
  document.getElementById("inventory-modal").classList.add("hidden");
}

async function saveInventoryItem() {
  const payload = {
    name: document.getElementById("inv-name").value.trim(),
    unit: document.getElementById("inv-unit").value.trim() || "unit",
    quantity_in_stock: parseFloat(document.getElementById("inv-qty").value) || 0,
    reorder_level: parseFloat(document.getElementById("inv-reorder").value) || 0,
    cost_per_unit: parseFloat(document.getElementById("inv-cost").value) || 0,
  };
  if (!payload.name) {
    toast("Item name is required.", "error");
    return;
  }
  try {
    await API.inventory.create(payload);
    toast("Inventory item added.", "success");
    closeInventoryModal();
    loadInventory();
  } catch (err) {
    toast(err.message, "error");
  }
}

function openRestockModal(itemId, name) {
  document.getElementById("restock-item-id").value = itemId;
  document.getElementById("restock-amount").value = "";
  document.getElementById("restock-reason").value = "manual restock";
  document.querySelector("#restock-modal h3").textContent = `Adjust stock — ${name}`;
  document.getElementById("restock-modal").classList.remove("hidden");
}

function closeRestockModal() {
  document.getElementById("restock-modal").classList.add("hidden");
}

async function submitRestock() {
  const itemId = document.getElementById("restock-item-id").value;
  const change_amount = parseFloat(document.getElementById("restock-amount").value);
  const reason = document.getElementById("restock-reason").value.trim() || "manual adjustment";
  if (isNaN(change_amount) || change_amount === 0) {
    toast("Enter a non-zero amount.", "error");
    return;
  }
  try {
    await API.inventory.adjust(itemId, change_amount, reason);
    toast("Stock updated.", "success");
    closeRestockModal();
    loadInventory();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function deleteInventoryItem(id, name) {
  if (!confirm(`Remove "${name}" from inventory?`)) return;
  try {
    await API.inventory.remove(id);
    toast("Item removed.", "success");
    loadInventory();
  } catch (err) {
    toast(err.message, "error");
  }
}
