# 📸 Visual Setup Guide — What to Click

## 1️⃣ Gmail App Password (Email OTP)

### Step 1: Go to Google Account
```
https://myaccount.google.com
↓
Click "Security" on left sidebar
```

### Step 2: Enable 2-Step Verification
```
Scroll down to "2-Step Verification"
↓
Click "2-Step Verification"
↓
Follow prompts (you'll need your phone)
↓
Click "Turn on"
```

### Step 3: Create App Password
```
Go back to Security page (refresh if needed)
↓
Scroll to "App passwords" (only appears after 2FA is on)
↓
Select: App = "Mail", Device = "Windows Computer" (or your OS)
↓
Click "Generate"
↓
Google shows 16 characters: "xxxx xxxx xxxx xxxx"
↓
Copy it
```

### Step 4: Update .env
```bash
# In backend/.env, find these lines and fill them in:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx    # Paste the 16 chars here (no spaces needed when you paste)
SMTP_FROM_NAME=Monika G Cafe
```

---

## 2️⃣ Twilio Phone Number (Mobile OTP)

### Step 1: Create Account
```
https://www.twilio.com/console
↓
Click "Sign up"
↓
Verify email
↓
Fill in your info
↓
Skip the wizard for now
```

### Step 2: Buy a Phone Number
```
Left sidebar → "Phone Numbers"
↓
Click "Manage Phone Numbers"
↓
Click "Buy a Number"
↓
Select Country (e.g. United States, India)
↓
Search for a number
↓
Click the number you want
↓
Click "Buy"
↓
You now own that number (e.g. +1 234 567 8900)
```

### Step 3: Get API Credentials
```
Left sidebar → "Account" → "API Keys & Tokens"
↓
You see two things:
  - Account SID: AC... (copy this)
  - Auth Token: ... (copy this)
```

### Step 4: Update .env
```bash
# In backend/.env:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx    # Your SID
TWILIO_AUTH_TOKEN=your_token_here                        # Your token
TWILIO_FROM_NUMBER=+1 234 567 8900                       # Your Twilio number
```

### Step 5: Test SMS
```
Go to Twilio Console → Phone Numbers
↓
Click your number
↓
Scroll to "Test SMS"
↓
Enter your number as "To" number: +919876543210
↓
Type "Hello" as message
↓
Click "Send Test SMS"
↓
Check your phone!
```

---

## 3️⃣ Google OAuth (Sign in with Google)

### Step 1: Create Google Cloud Project
```
https://console.cloud.google.com
↓
Top left, click "Select a Project"
↓
Click "New Project"
↓
Project name: "Monika G Cafe"
↓
Click "Create"
↓
Wait 30 seconds for it to create
```

### Step 2: Enable APIs
```
Search bar at top: "Google+ API"
↓
Click the first result
↓
Click "Enable"
↓
Search bar again: "Google Identity Services"
↓
Click it
↓
Click "Enable"
```

### Step 3: Create OAuth Credentials
```
Left sidebar → APIs & Services → Credentials
↓
Click "Create Credentials" → "OAuth client ID"
↓
If prompted for consent screen:
  - Click "Create OAuth consent screen"
  - Choose "External"
  - Click "Create"
  - Fill app name: "Monika G Cafe"
  - Fill user support email: your@email.com
  - Click "Save and Continue"
  - Click "Save and Continue" again (skip scopes)
  - Click "Save and Continue" again (skip test users)
```

### Step 4: Configure OAuth
```
Back to Credentials page
↓
Click "Create Credentials" → "OAuth client ID"
↓
Application type: "Web application"
↓
Name: "Monika G Cafe Web"
↓
Authorized JavaScript origins (click "Add URI"):
  http://localhost:5500
  http://127.0.0.1:5500
  (if deployed: your-frontend-url.com)
↓
Authorized redirect URIs (click "Add URI"):
  http://localhost:8000/auth/google/callback
  (if deployed: your-backend-url.com/auth/google/callback)
↓
Click "Create"
```

### Step 5: Copy Credentials
```
A popup shows:
  - Client ID: ...apps.googleusercontent.com
  - Client Secret: ...
↓
Copy both
```

### Step 6: Update .env
```bash
# In backend/.env:
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

### Step 7: Update Frontend
```javascript
// In frontend/js/login.js, find this line:
const GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com";

// Replace with your actual Client ID:
const GOOGLE_CLIENT_ID = "your_client_id.apps.googleusercontent.com";
```

---

## 4️⃣ MySQL Database

### Option A: Docker (Recommended)
```bash
# Run this one command:
docker run --name monika-mysql -e MYSQL_ROOT_PASSWORD=password123 -p 3306:3306 -d mysql:8

# Create database:
docker exec monika-mysql mysql -uroot -ppassword123 -e "CREATE DATABASE monika_g_cafe;"
```

### Option B: Download & Install
```
https://dev.mysql.com/downloads/mysql/
↓
Download for your OS
↓
Install (default port is 3306)
↓
Open MySQL Command Line Client
↓
Type: CREATE DATABASE monika_g_cafe;
```

### Step: Update .env
```bash
# In backend/.env:
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password123        # Whatever you set
DB_NAME=monika_g_cafe
```

---

## ✅ Checklist — Do These in Order

- [ ] **Gmail**: Account → Security → 2FA → App Password → Copy to .env
- [ ] **MySQL**: Docker or download → Create database → Add to .env
- [ ] **Twilio**: Sign up → Buy number → Copy SID + Token → Add to .env
- [ ] **Google**: Cloud Console → Create project → Enable APIs → Create OAuth → Copy credentials → Add to .env + frontend

---

## 🧪 Test Each One

### Test Email OTP
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Go to login → Email tab → enter your email → check inbox

### Test Mobile OTP
Same backend running above
Go to login → Mobile tab → enter +919876543210 → check phone

### Test Google
Same backend running above
Go to login → click Google button → sign in

---

## ❌ If Something Doesn't Work

| What | Check |
|------|-------|
| Email not arriving | Gmail Spam folder; SMTP password has no spaces; backend logs |
| SMS not arriving | Phone number format: +countrycodephonenumber; Twilio balance |
| Google button missing | Browser console (F12); Client ID in login.js correct |
| Backend won't start | `pip install -r requirements.txt` again; MySQL running |

---

## 📍 Your .env Should Look Like This

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password123
DB_NAME=monika_g_cafe

# JWT
JWT_SECRET_KEY=any_long_random_string_here_make_it_long_32_chars_minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# OTP
OTP_EXPIRE_MINUTES=5
OTP_LENGTH=6

# Google
GOOGLE_CLIENT_ID=12345678901-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrs
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=abcdefghijklmnopqrstuvwxyzabcdef
TWILIO_FROM_NUMBER=+1 234 567 8900

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcd abcd abcd abcd
SMTP_FROM_NAME=Monika G Cafe

# Frontend
FRONTEND_URL=http://localhost:5500
```

**That's it!** You're ready to go. 🚀
