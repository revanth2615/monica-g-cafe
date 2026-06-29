# Monika G Cafe Management System

A full cafe management system: orders, billing, inventory, employees, and
reporting, with a FastAPI + MySQL backend and a plain HTML/CSS/JS frontend.

Login supports three methods:
- **Email + OTP** (always OTP, no password)
- **Mobile number + OTP** (via Twilio SMS)
- **Google Sign-In**

### 📖 **Start Here → Read `QUICK_START.md` First**

It has a checklist for setting up Gmail, Twilio, Google OAuth, and MySQL in 30 minutes.

---

## 1. Open the project in VS Code

1. Unzip the project you downloaded.
2. Open VS Code → `File > Open Folder` → select the unzipped `monika-g-cafe` folder.
3. Recommended extensions: **Python** (ms-python.python), **Live Server**
   (ritwickdey.LiveServer) — install both from the Extensions tab if prompted.

Folder layout:
```
monika-g-cafe/
├── backend/      FastAPI app (Python)
└── frontend/     Static HTML/CSS/JS (no build step needed)
```

---

## 2. Set up External Services (30 min)

**⚠️ READ FIRST:** `QUICK_START.md` has step-by-step instructions for:
- Gmail SMTP (for email OTP)
- Twilio (for mobile OTP)
- Google OAuth (for Sign in with Google)
- MySQL database

Follow the checklist there, then come back to continue below.

### Quick MySQL Setup Only
Docker (easiest):
```bash
docker run --name monika-mysql -e MYSQL_ROOT_PASSWORD=yourpassword -p 3306:3306 -d mysql:8
docker exec monika-mysql mysql -uroot -pyourpassword -e "CREATE DATABASE monika_g_cafe;"
```

Or download: https://dev.mysql.com/downloads/mysql/

---

## 3. Set up the Backend

Once you've done the external services (Gmail, Twilio, Google, MySQL):

Open a terminal in VS Code (`` Ctrl+` ``), then:

```bash
cd backend
python -m venv venv

# Activate virtual environment:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env       # macOS/Linux
copy .env.example .env     # Windows
```

Fill in these fields (see `QUICK_START.md` or `SETUP_GUIDE.md` for details):
- `DB_PASSWORD` — MySQL password
- `JWT_SECRET_KEY` — any long random string
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — from Google Cloud Console
- `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_FROM_NUMBER` — from Twilio
- `SMTP_USER` / `SMTP_PASSWORD` — Gmail App Password

Seed the database with an admin account and sample data:
```bash
python seed.py
```

Start the backend:
```bash
uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000**. Visit **http://localhost:8000/docs** for the interactive API docs.

---

## 4. Set up the Frontend

The frontend is plain static files — no npm/build needed.

**Option A — VS Code Live Server (recommended):**
1. Right-click `frontend/login.html` in the file explorer
2. Choose **"Open with Live Server"**
3. It opens at `http://127.0.0.1:5500`

**Option B — Python's HTTP server:**
```bash
cd frontend
python -m http.server 5500
```

Frontend runs at **http://127.0.0.1:5500**

### Connecting Frontend to Backend
By default, frontend calls `http://localhost:8000`. If your backend runs elsewhere, add this in `frontend/index.html` (before the `<script src="js/api.js">` line):
```html
<script>window.MONIKA_API_BASE_URL = "http://your-backend-url:8000";</script>
```

---

## 5. Test Everything

1. **Email OTP**: Login page → **Email tab** → enter your email → check inbox for code
2. **Mobile OTP**: Login page → **Mobile tab** → +919876543210 → check phone for SMS
3. **Google Sign-In**: Login page → **Google button** → sign in with Google
4. **Dashboard**: Once logged in as admin, add menu items, orders, etc.

### Default Admin Account (created by `seed.py`)
- Email: `admin@monikagcafe.com`
- Login: Use Email tab → enter this email → check inbox for OTP

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Email OTP not arriving | Check Gmail **Spam**; verify SMTP password (no spaces) |
| Mobile OTP not arriving | Use format `+countrycodephoneno`; check Twilio balance |
| Google button doesn't work | Check browser console (F12); verify Client ID in `login.js` |
| Backend won't start | Run `pip install -r requirements.txt` again |
| Can't connect to database | Make sure MySQL is running; check password in `.env` |

See `SETUP_GUIDE.md` for detailed troubleshooting and deployment info.
