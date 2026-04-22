# 🛒 NexaShop — Full-Stack Django Admin Dashboard

> **Complete working project** — Django 4 · Bootstrap 5 · Chart.js · SQLite

---

## ⚡ Quick Start (3 commands)

```bash
# 1. Install Django
pip install django

# 2. Setup database + demo data
python manage.py migrate
python manage.py seed_data

# 3. Run server
python manage.py runserver
```

Open → **http://127.0.0.1:8000**  
Login → **admin / admin123**

---

## 📁 Full Project Structure

```
nexashop/
├── nexashop/              ← Project config
│   ├── settings.py
│   └── urls.py
├── dashboard/             ← Main app
│   ├── models.py          ← Category, Product, Customer, Order, ActivityLog
│   ├── views.py           ← All views (Dashboard, CRUD)
│   ├── forms.py           ← OrderForm, ProductForm, CustomerForm
│   ├── urls.py            ← All URL routes
│   ├── admin.py           ← Django Admin
│   ├── context_processors.py
│   └── management/commands/seed_data.py
├── templates/
│   ├── base.html          ← Sidebar + Topbar layout
│   ├── auth/login.html    ← Login page
│   ├── dashboard/index.html  ← Main dashboard with charts
│   ├── orders/            ← list, detail, form, confirm_delete
│   ├── products/          ← list (card grid), form, confirm_delete
│   └── customers/         ← list (card grid), detail, form
├── static/css/js/
├── db.sqlite3             ← Pre-seeded database
└── manage.py
```

---

## ✅ Features — A to Z

| Feature | Description |
|---------|-------------|
| 🔐 Login / Logout | Django auth — session based |
| 📊 Dashboard | KPI cards, line chart, donut chart, sparkline |
| 📦 Orders CRUD | Create, Read, Update, Delete + status filter |
| 🛍️ Products CRUD | Card grid + category filter + search |
| 👥 Customers CRUD | Card grid + order history per customer |
| 🔔 Activity Feed | Auto-logged events (new order, status change, low stock) |
| 📄 Pagination | All list views paginated (12 per page) |
| 🔍 Search | Orders, Products, Customers all searchable |
| 💬 Flash Messages | Success / Error alerts on all actions |
| 🌙 Dark Theme | Full dark UI with CSS variables |
| 📱 Responsive | Mobile sidebar toggle (Bootstrap 5) |
| ⚙️ Django Admin | /admin — full model management |

---

## 🔑 Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

---

## 🚀 Production Checklist

- [ ] Change `SECRET_KEY` in settings.py
- [ ] Set `DEBUG = False`
- [ ] Switch to PostgreSQL
- [ ] Add Redis caching
- [ ] Run `python manage.py collectstatic`
- [ ] Deploy with Gunicorn + Nginx
