/* Customer interface logic */

function loadNavAuthSlot() {
  const slot = document.getElementById("authNavSlot");
  if (!slot) return;
  const user = getCurrentUser();
  if (user && user.role === "customer") {
    slot.innerHTML = `<a href="#" onclick="logout('login.html'); return false;">Logout (${user.name.split(" ")[0]})</a>`;
  } else {
    slot.innerHTML = `<a href="login.html" class="btn btn-primary btn-sm">Login</a>`;
  }
}

async function loadHotels(filters = {}) {
  const grid = document.getElementById("hotelGrid");
  if (!grid) return;
  grid.innerHTML = `<div class="loader"></div>`;

  const params = new URLSearchParams();
  if (filters.city) params.append("city", filters.city);
  if (filters.max_price) params.append("max_price", filters.max_price);

  const { ok, data } = await apiRequest(`/hotels?${params.toString()}`);

  if (!ok || !data.hotels || data.hotels.length === 0) {
    grid.innerHTML = `<div class="empty-state">
        <div class="icon">🏝️</div>
        <h3>No hotels found</h3>
        <p>Try a different city or price range.</p>
      </div>`;
    return;
  }

  grid.innerHTML = data.hotels.map(hotelCardHtml).join("");
}

function hotelCardHtml(hotel) {
  const amenities = (hotel.amenities || []).slice(0, 3)
    .map(a => `<span class="amenity-pill">${a}</span>`).join("");

  return `
    <a href="hotel-details.html?id=${hotel._id}" class="card hotel-card reveal">
      <div class="img-wrap">
        <img src="${hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80'}" alt="${hotel.name}">
        <span class="badge">⭐ ${hotel.rating || 4.5}</span>
        <span class="price-tag">${formatINR(hotel.starting_price)} / night</span>
      </div>
      <div class="info">
        <h3>${hotel.name}</h3>
        <div class="city">📍 ${hotel.city}</div>
        <p style="color:var(--text-muted); font-size:.85rem; margin-top:4px;">
          ${(hotel.description || "").substring(0, 80)}${hotel.description && hotel.description.length > 80 ? "…" : ""}
        </p>
        <div style="margin-top:8px;">${amenities}</div>
      </div>
    </a>
  `;
}
