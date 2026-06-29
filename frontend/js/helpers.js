/**
 * Shared helpers used across every page: toast notifications,
 * auth guarding (redirect to login if not authenticated / wrong role),
 * and small DOM utilities.
 */

function toast(message, type = "info") {
  let root = document.getElementById("toast-root");
  if (!root) {
    root = document.createElement("div");
    root.id = "toast-root";
    document.body.appendChild(root);
  }
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  root.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === "class") node.className = value;
    else if (key === "html") node.innerHTML = value;
    else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else {
      node.setAttribute(key, value);
    }
  });
  (Array.isArray(children) ? children : [children]).forEach((child) => {
    if (child === null || child === undefined) return;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  });
  return node;
}

/**
 * Call at the top of every protected page.
 * Redirects to login if there's no session, and to an "access denied"
 * fallback if the logged-in user's role isn't allowed on this page.
 */
function requireAuth(allowedRoles = null) {
  const user = API.getUser();
  const token = API.getAccessToken();
  if (!user || !token) {
    window.location.href = "login.html";
    return null;
  }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    toast("You don't have access to that page.", "error");
    window.location.href = "index.html";
    return null;
  }
  return user;
}

function logout() {
  API.clearSession();
  window.location.href = "login.html";
}

function formatCurrency(amount) {
  return `₹${Number(amount).toFixed(2)}`;
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

/** Renders the shared top nav, swapping links based on the logged-in role. */
function renderNav(activePage) {
  const mount = document.getElementById("nav-root");
  if (!mount) return;
  const user = API.getUser();
  if (!user) return;

  const linksByRole = {
    admin: [
      ["dashboard.html", "Dashboard"], ["menu.html", "Menu"], ["orders.html", "Orders"],
      ["billing.html", "Billing"], ["inventory.html", "Inventory"], ["employees.html", "Employees"],
    ],
    staff: [
      ["dashboard.html", "Dashboard"], ["menu.html", "Menu"], ["orders.html", "Orders"],
      ["billing.html", "Billing"], ["inventory.html", "Inventory"],
    ],
    kitchen: [["kitchen.html", "Kitchen Queue"]],
    customer: [["customer-menu.html", "Order"], ["customer-orders.html", "My Orders"]],
  };
  const links = linksByRole[user.role] || [];

  mount.innerHTML = "";
  mount.appendChild(
    el("div", { class: "nav-inner" }, [
      el("a", { href: "#", class: "nav-brand" }, "Monika G Cafe"),
      el("div", { class: "nav-links" }, links.map(([href, label]) =>
        el("a", { href, class: href === activePage ? "nav-link active" : "nav-link" }, label)
      )),
      el("div", { class: "nav-user" }, [
        el("span", { class: "nav-user-name" }, `${user.name} · ${user.role}`),
        el("button", { class: "btn btn-secondary btn-sm", onClick: logout }, "Log out"),
      ]),
    ])
  );
}
