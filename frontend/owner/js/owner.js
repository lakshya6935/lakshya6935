/* Owner dashboard shared logic */

function renderOwnerSidebar(activePage) {
  const user = requireRole("owner", "login.html");
  const items = [
    { href: "dashboard.html", icon: "📊", label: "Dashboard" },
    { href: "add-hotel.html", icon: "🏨", label: "My Hotels" },
    { href: "manage-bookings.html", icon: "📅", label: "Bookings" },
  ];
  const html = items.map(i => `<a href="${i.href}" class="${activePage === i.href ? 'active' : ''}">${i.icon} ${i.label}</a>`).join("");

  document.querySelectorAll(".sidebar-links").forEach(el => {
    el.innerHTML = html + `<a href="#" class="logout-btn" onclick="logout('login.html'); return false;">🚪 Logout</a>`;
  });
  document.querySelectorAll(".owner-name-slot").forEach(el => { el.textContent = user.name; });

  const mobileToggle = document.querySelector(".mobile-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => sidebar.classList.toggle("open"));
  }
  return user;
}
