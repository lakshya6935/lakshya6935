# 🏨 StayLuxe — Hotel Management System

A full-stack Hotel Management System with **three completely separate interfaces**:

| Interface | Who it's for | Access |
|---|---|---|
| **Customer** | Anyone browsing/booking hotels | Public — `frontend/customer/` |
| **Hotel Owner** | Hotel partners who list & manage their properties | Not linked from customer nav bar; owners register at `frontend/owner/register.html` and log in at `frontend/owner/login.html` (requires admin approval first) |
| **Admin** | Platform administrator | **Hidden** — no public link anywhere. Reach it directly at `frontend/admin/login.html`. Default credentials are created by `backend/seed.py` (see below). |

There is **no dropdown / toggle anywhere that lets a visitor pick "admin" or "owner"** — each interface lives on its own set of pages with its own login, and the admin portal is never linked from the public site.

---

## 🧱 Tech Stack

- **Frontend:** HTML5, CSS3 (pastel purple/pink/teal theme, animations, modals/toasts), Vanilla JavaScript (fetch API)
- **Backend:** Python 3, Flask, Flask-JWT-Extended (JWT auth), Flask-CORS
- **Database:** MongoDB (via PyMongo)
- **Currency:** All prices are shown in Indian Rupees (₹ / INR)

---

## 📁 Project Structure

```
hotel-management-system/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── config.py               # Env-based configuration
│   ├── db.py                   # MongoDB connection & collections
│   ├── seed.py                 # Creates default admin + sample data
│   ├── requirements.txt
│   ├── .env.example            # Copy to .env and edit
│   ├── routes/
│   │   ├── auth_routes.py      # Register + role-specific login (customer/owner/admin)
│   │   ├── hotel_routes.py     # Hotel & room CRUD
│   │   ├── booking_routes.py   # Booking creation/cancellation
│   │   ├── admin_routes.py     # Admin-only management endpoints
│   │   └── owner_routes.py     # Owner-only endpoints
│   └── utils/
│       └── helpers.py          # Serialization + role_required decorator
└── frontend/
    ├── assets/
    │   ├── css/common.css      # Shared design system (colors, buttons, cards, animations)
    │   └── js/common.js        # Shared API wrapper, toasts, modal, auth helpers
    ├── customer/                # Public-facing site
    │   ├── index.html            (browse & search hotels)
    │   ├── login.html / register.html
    │   ├── hotel-details.html    (room list + booking popup)
    │   └── my-bookings.html
    ├── owner/                   # Hotel owner dashboard (separate, not publicly linked)
    │   ├── login.html / register.html
    │   ├── dashboard.html        (stats)
    │   ├── add-hotel.html        (manage own hotels & rooms)
    │   └── manage-bookings.html
    └── admin/                   # Admin dashboard (hidden, no public link)
        ├── login.html            (dedicated admin-only login)
        ├── dashboard.html        (platform-wide stats, approve hotels)
        ├── manage-hotels.html    (approve/reject/delete any hotel)
        └── manage-users.html     (approve owners, block/delete users)
```

---

## ⚙️ Setup Instructions

### 1. Install & start MongoDB

Make sure MongoDB is installed and running locally on the default port `27017`.
(Alternatively use a free MongoDB Atlas cluster and paste its connection string into `.env`.)

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env if needed

python seed.py                  # creates the admin account + sample hotels
python app.py                   # starts the API on http://localhost:5000
```

`seed.py` will print the **default admin credentials** to your terminal, e.g.:

```
email:    admin@stayluxe.com
password: Admin@12345
```

⚠️ Change this password (or the values in `.env`) before any real deployment.

It also creates a sample **hotel owner** account (`owner@stayluxe.com` / `Owner@123`) and four sample hotels so the site isn't empty on first run.

### 3. Frontend setup

The frontend is plain HTML/CSS/JS — no build step required. Just serve the `frontend` folder with any static server, e.g.:

```bash
cd frontend
python -m http.server 5500
```

Then open:
- Customer site → `http://localhost:5500/customer/index.html`
- Hotel Owner portal → `http://localhost:5500/owner/login.html`
- Admin portal (hidden) → `http://localhost:5500/admin/login.html`

The frontend talks to the backend at `http://localhost:5000/api` (configured in `frontend/assets/js/common.js` via `API_BASE_URL`).

---

## 🔐 How the "separate, no-choice" access model works

- The **registration form** on the public site only ever creates a `customer` account — there is no role selector.
- **Hotel owners** apply through their own separate registration page (`owner/register.html`). New owner accounts are created with `status: "pending"` and **cannot log in** until an admin approves them from the Admin → Manage Users screen.
- The **admin account is never created through any public form** — it only exists via `backend/seed.py`, and its login page is not linked from the customer or owner interfaces at all.
- Each login endpoint (`/api/auth/login/customer`, `/login/owner`, `/login/admin`) checks the account's role on the server, so even if someone guessed a URL, they can't log in to the wrong interface with the wrong account type.

---

## ✨ UI Features

- Pastel purple / pink / teal gradient theme, soft shadows, rounded cards
- Smooth scroll-reveal animations, hover-lift cards, floating icons, spinner loaders
- Toast notifications and popup modals (e.g. the booking form opens in an animated modal)
- Fully responsive with a mobile nav drawer (customer site) and collapsible sidebar (admin/owner dashboards)
- Hotel & room images, ratings, amenity pills, and all prices formatted in ₹ (INR)

---

## 🔑 Sample Accounts (after running `seed.py`)

| Role | Email | Password |
|---|---|---|
| Admin | admin@stayluxe.com | Admin@12345 |
| Hotel Owner | owner@stayluxe.com | Owner@123 |
| Customer | *(register your own via the site)* | — |
