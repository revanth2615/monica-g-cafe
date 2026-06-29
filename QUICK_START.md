# ⚡ Quick Start Checklist — Do These NOW

## Before You Run Anything

### 1. Gmail Setup (5 min) ✅
- [ ] Go to https://myaccount.google.com → **Security**
- [ ] Enable **2-Step Verification**
- [ ] Create **App Password** (Mail, your device)
- [ ] Copy the 16-character password
- [ ] Update `backend/.env`:
  ```
  SMTP_USER=your-email@gmail.com
  SMTP_PASSWORD=xxxx xxxx xxxx xxxx
  ```

### 2. MySQL Setup (5 min) ✅
**Option A — Docker (easiest):**
```bash
docker run --name monika-mysql -e MYSQL_ROOT_PASSWORD=password123 -p 3306:3306 -d mysql:8
```

**Option B — Download & Install:**
- https://dev.mysql.com/downloads/mysql/

Then create database:
```sql
CREATE DATABASE monika_g_cafe;
```

Update `backend/.env`:
```
DB_PASSWORD=password123
```

### 3. Twilio Setup (10 min) ✅
- [ ] Go to https://www.twilio.com/console
- [ ] Sign up
- [ ] Buy a phone number (Phone Numbers → Buy)
- [ ] Copy: **Account SID** and **Auth Token**
- [ ] Note your **Twilio phone number**
- [ ] Update `backend/.env`:
  ```
  TWILIO_ACCOUNT_SID=AC...
  TWILIO_AUTH_TOKEN=...
  TWILIO_FROM_NUMBER=+1234567890
  ```

### 4. Google OAuth Setup (10 min) ✅
- [ ] Go to https://console.cloud.google.com
- [ ] Create new project: `Monika G Cafe`
- [ ] Search & enable: **Google+ API** and **Google Identity Services**
- [ ] Go to **Credentials** → **Create OAuth client ID** → **Web application**
- [ ] Add authorized origins:
  - `http://localhost:5500`
  - `http://127.0.0.1:5500`
- [ ] Add redirect URIs:
  - `http://localhost:8000/auth/google/callback`
- [ ] Copy: **Client ID** and **Client Secret**
- [ ] Update `backend/.env`:
  ```
  GOOGLE_CLIENT_ID=...
  GOOGLE_CLIENT_SECRET=...
  ```
- [ ] Update `frontend/js/login.js` line (search for `GOOGLE_CLIENT_ID`):
  ```javascript
  const GOOGLE_CLIENT_ID = "your_client_id.apps.googleusercontent.com";
  ```

### 5. Backend Setup (5 min) ✅
```bash
cd backend
python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python seed.py              # Creates admin account
```

### 6. Run Backend ✅
```bash
uvicorn app.main:app --reload
# Should say: "Uvicorn running on http://127.0.0.1:8000"
```

### 7. Run Frontend ✅
```bash
cd frontend
python -m http.server 5500
# or use VS Code → right-click login.html → Open with Live Server
```

### 8. Test! ✅
1. Open **http://127.0.0.1:5500/login.html**
2. **Email tab**: Enter your email → check inbox for OTP
3. **Mobile tab**: Enter +919876543210 (or your number) → check phone for SMS
4. **Google button**: Click → sign in with Google
5. You're in! 🎉

---

## Key Points

| Step | If It Fails | Solution |
|------|------------|----------|
| Email OTP | No email arrives | Check Gmail **Spam** folder; verify SMTP password (no spaces) |
| Mobile OTP | No SMS arrives | Use format: `+countrycodephoneno` (no spaces); check Twilio balance |
| Google button | Doesn't appear | Check browser console (F12); verify Client ID in `login.js` |
| Backend won't run | Port/module errors | Run `pip install -r requirements.txt` again; check MySQL running |
| Can't access DB | Connection error | Make sure MySQL running; verify password in `.env` matches |

---

## What Each Service Does

**Gmail** → Email OTP codes  
**Twilio** → SMS OTP codes  
**Google** → "Sign in with Google" button  
**MySQL** → All data storage  

All 4 working = Full login system! ✨

---

## .env Template (copy & paste, fill blanks)

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password123
DB_NAME=monika_g_cafe

JWT_SECRET_KEY=your_long_random_string_here_make_it_long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

OTP_EXPIRE_MINUTES=5
OTP_LENGTH=6

GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_FROM_NUMBER=+1234567890

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

FRONTEND_URL=http://localhost:5500
```

**That's it! You're ready to go.** 🚀
