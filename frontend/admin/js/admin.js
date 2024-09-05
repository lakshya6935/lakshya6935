/* Admin dashboard shared logic */

function renderAdminSidebar(activePage) {
  const user = requireRole("admin", "login.html");
  const items = [
    { href: "dashboard.html", icon: "📊", label: "Dashboard" },
    { href: "manage-hotels.html", icon: "🏨", label: "Manage Hotels" },
    { href: "manage-users.html", icon: "👥", label: "Manage Users" },
  ];
  const html = items.map(i => `<a href="${i.href}" class="${activePage === i.href ? 'active' : ''}">${i.icon} ${i.label}</a>`).join("");

  document.querySelectorAll(".sidebar-links").forEach(el => {
    el.innerHTML = html + `<a href="#" class="logout-btn" onclick="logout('login.html'); return false;">🚪 Logout</a>`;
  });
  document.querySelectorAll(".admin-name-slot").forEach(el => { el.textContent = user.name; });

  const mobileToggle = document.querySelector(".mobile-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => sidebar.classList.toggle("open"));
  }
  return user;
}
