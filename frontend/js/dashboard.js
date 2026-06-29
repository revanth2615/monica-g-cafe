const user = requireAuth(["admin", "staff"]);
if (user) {
  renderNav("dashboard.html");
  loadDashboard();
}

async function loadDashboard() {
  try {
    const [summary, topItems] = await Promise.all([
      API.reports.dashboard(),
      API.reports.topItems(5),
    ]);

    document.getElementById("stat-orders").textContent = summary.orders_today;
    document.getElementById("stat-revenue").textContent = formatCurrency(summary.revenue_today);
    document.getElementById("stat-pending").textContent = summary.pending_orders;
    document.getElementById("stat-lowstock").textContent = summary.low_stock_items;

    const body = document.getElementById("top-items-body");
    if (topItems.length === 0) {
      body.innerHTML = `<tr><td colspan="3" class="empty-state">No sales recorded yet.</td></tr>`;
      return;
    }
    body.innerHTML = "";
    topItems.forEach((item) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${item.name}</td><td>${item.total_sold}</td><td>${formatCurrency(item.total_revenue)}</td>`;
      body.appendChild(row);
    });
  } catch (err) {
    toast(err.message, "error");
  }
}
