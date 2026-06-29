# Monika G Cafe — Complete Setup Guide for OTP, Twilio, Google OAuth & Email

This guide walks you through configuring every external service needed for the system to work.

---

## 1. EMAIL OTP (SMTP) — Google Gmail Setup

### Why Email OTP?
- Users log in with email + OTP (no password needed)
- OTP is sent via email
- Uses SMTP protocol (Gmail, Outlook, or any email provider)

### Step-by-Step: Gmail Setup

#### 1.1 Enable 2-Factor Authentication
1. Go to **https://myaccount.google.com**
2. Click **Security** (left sidebar)
3. Scroll down to **2-Step Verification** → Click it
4. Follow the prompts to enable 2-Factor Authentication

#### 1.2 Create an App Password
1. Go back to **Security** page
2. Scroll to **App passwords** (only appears if 2FA is enabled)
3. Select:
   - App: **Mail**
   - Device: **Windows Computer** (or your OS)
4. Google generates a **16-character password** — copy it (you'll need this)

#### 1.3 Update .env file
In your `backend/.env`, fill in:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx    # The 16-char app password (remove spaces when pasting)
SMTP_FROM_NAME=Monika G Cafe
```

**Example:**
```env
SMTP_USER=revanth.dev@gmail.com
SMTP_PASSWORD=abcdabcdabcdabcd
```

#### 1.4 Test Email OTP
Once configured:
1. Start the backend: `uvicorn app.main:app --reload`
2. Go to login page → **Email tab** → enter your email
3. Click **Send login code**
4. Check your inbox (or spam folder) for the OTP
5. Enter the code → you're logged in!

**If email doesn't arrive:**
- Check Gmail **Spam** folder
- Check backend logs for errors
- Make sure `.env` has correct email/password (no spaces in password)

---

## 2. MOBILE OTP — Twilio SMS Setup

### Why Twilio?
- Sends OTP via SMS to any mobile number
- User logs in with phone + OTP
- More reliable than email for some users

### Step-by-Step: Twilio Setup

#### 2.1 Create a Twilio Account
1. Go to **https://www.twilio.com/console**
2. Click **Sign up** (if not already)
3. Verify your email
4. Create account (fill in your details)
5. Choose **SMS** as your use case

#### 2.2 Get Your Twilio Phone Number
1. In Twilio Console, go to **Phone Numbers** → **Manage**
2. Click **Buy a Number**
3. Choose country (India, USA, etc.) and search
4. Select a number → **Buy** (usually $1/month)
5. You'll get a number like: **+1 234 567 8900**

#### 2.3 Get Your Account Credentials
1. Go to **Account** → **API Keys & Tokens**
2. Copy:
   - **Account SID** (e.g., `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (e.g., `your_auth_token_here`)

#### 2.4 Update .env file
In `backend/.env`:

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1 234 567 8900    # Your Twilio phone number
```

#### 2.5 Test Mobile OTP
1. Restart backend
2. Go to login page → **Mobile tab**
3. Enter your phone number with country code: `+919876543210` (for India)
4. Click **Send OTP via SMS**
5. Check your phone for SMS
6. Enter the code → you're logged in!

**If SMS doesn't arrive:**
- Make sure you're using correct format: **+countrycode phonenumber** (no spaces)
- Check Twilio Console → **Logs** for failed SMS
- Make sure you have SMS credits (Twilio trial accounts are limited to verified numbers)

**For Twilio Trial Account:**
- Only verified phone numbers can receive SMS
- To verify a number: Account → Settings → Verify phone
- To send SMS to non-verified numbers, upgrade account

---

## 3. GOOGLE SIGN-IN (Google OAuth)

### Why Google Login?
- Users can sign in with their Google account
- No OTP needed (uses Google's authentication)
- Fast and secure

### Step-by-Step: Google OAuth Setup

#### 3.1 Create a Google Cloud Project
1. Go to **https://console.cloud.google.com**
2. Create a new project:
   - Click **Select a Project** (top left)
   - Click **New Project**
   - Name: `Monika G Cafe`
   - Click **Create**
3. Wait for project to be created

#### 3.2 Enable Google Sign-In API
1. In Google Cloud Console, search for **"Google+ API"** in the search bar
2. Click on it → Click **Enable**
3. Now search for **"Google Identity Services"** → Click **Enable** as well

#### 3.3 Create OAuth 2.0 Credentials
1. Go to **APIs & Services** → **Credentials** (left sidebar)
2. Click **Create Credentials** → Choose **OAuth client ID**
3. If prompted to create consent screen:
   - Click **Create OAuth consent screen**
   - Choose **External** → Click **Create**
   - Fill in:
     - App name: `Monika G Cafe`
     - User support email: Your email
     - Developer contact: Your email
   - Click **Save and Continue**
   - Skip optional scopes → **Save and Continue**
   - Skip test users → **Save and Continue**
4. Back to **Create Credentials** → **OAuth client ID**
5. Select **Web application**
6. Name: `Monika G Cafe Web Client`
7. Add **Authorized JavaScript origins**:
   - `http://localhost:5500`
   - `http://127.0.0.1:5500`
   - Your deployed frontend URL (if hosted online)
8. Add **Authorized redirect URIs**:
   - `http://localhost:8000/auth/google/callback`
   - Your backend OAuth callback URL (if deployed)
9. Click **Create**
10. A popup shows your **Client ID** and **Client Secret** → Copy both

#### 3.4 Update .env file
In `backend/.env`:

```env
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

#### 3.5 Update Frontend
In `frontend/js/login.js`, replace:
```javascript
const GOOGLE_CLIENT_ID = window.MONIKA_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com";
```
with:
```javascript
const GOOGLE_CLIENT_ID = "your_client_id.apps.googleusercontent.com";
```

#### 3.6 Test Google Sign-In
1. Restart backend
2. Go to login page
3. Click **Google Sign-In button**
4. Log in with your Google account
5. You're logged in as a customer!

**If Google button doesn't appear:**
- Check browser console (F12 → Console) for errors
- Make sure Google Client ID is correct
- Make sure frontend URL is in Google Console's authorized origins

---

## 4. Database Setup (MySQL)

### Option A: Install MySQL Locally
1. Download **MySQL Community Server** from https://dev.mysql.com/downloads/mysql/
2. Install it (default port: 3306)
3. Create database:
   ```sql
   CREATE DATABASE monika_g_cafe;
   ```

### Option B: Docker (Easiest)
```bash
docker run --name monika-mysql \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -p 3306:3306 \
  -d mysql:8
```
Then create database:
```bash
docker exec monika-mysql mysql -uroot -pyour_password -e "CREATE DATABASE monika_g_cafe;"
```

### Update .env
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=monika_g_cafe
```

---

## 5. Complete .env File Example

```env
# ============ DATABASE ============
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=monika_g_cafe

# ============ JWT ============
JWT_SECRET_KEY=your_long_random_string_here_at_least_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============ OTP ============
OTP_EXPIRE_MINUTES=5
OTP_LENGTH=6

# ============ GOOGLE OAUTH ============
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# ============ TWILIO (SMS OTP) ============
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+1234567890

# ============ SMTP (EMAIL OTP) ============
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdabcdabcdabcd
SMTP_FROM_NAME=Monika G Cafe

# ============ FRONTEND ============
FRONTEND_URL=http://localhost:5500
```

---

## 6. Running Everything

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate    # or venv\Scripts\activate on Windows
python seed.py              # Create admin account + sample data
uvicorn app.main:app --reload
```
Backend runs at: **http://localhost:8000**

### Terminal 2: Frontend
```bash
cd frontend
python -m http.server 5500
# or use VS Code Live Server
```
Frontend runs at: **http://localhost:5500**

### Test All Login Methods
1. **Email OTP**: Login page → Email tab → enter your email
2. **Mobile OTP**: Login page → Mobile tab → +919876543210
3. **Google**: Login page → Google Sign-In button

---

## 7. Troubleshooting

### Email OTP not arriving
- Check Gmail **Spam** folder
- Verify SMTP credentials in `.env` (no spaces in password)
- Check backend logs for SMTP errors
- Make sure Gmail **App Password** is used (not regular password)

### Mobile OTP not arriving
- Verify phone number format: `+countrycodephonenumber` (no spaces)
- Check Twilio Console → **Logs & History** for SMS status
- If trial account: verify your number in Twilio Settings first
- Check Twilio balance/credits

### Google Sign-In button not working
- Open browser DevTools (F12) → **Console** tab
- Look for JavaScript errors
- Verify Google Client ID is correct
- Make sure frontend URL is in Google Console's authorized origins

### Backend won't start
- Check `.env` file exists and is filled correctly
- Make sure all required packages are installed: `pip install -r requirements.txt`
- Check MySQL is running on port 3306
- Check port 8000 is not in use: `lsof -i :8000` (macOS/Linux)

### Database errors
- Make sure MySQL is running
- Make sure `monika_g_cafe` database exists
- Run `python seed.py` to create tables

---

## 8. Deploying to Production

### When Ready to Deploy Online

**Backend (Heroku, Railway, or AWS):**
1. Update `FRONTEND_URL` in `.env` to your frontend URL
2. Update `GOOGLE_REDIRECT_URI` to your backend domain
3. Deploy using: `git push heroku main` or platform's CLI

**Frontend (Vercel, Netlify, or GitHub Pages):**
1. Update `window.MONIKA_API_BASE_URL` in `js/api.js` to your backend URL
2. Update Google Console's authorized origins with your frontend domain
3. Deploy using: `vercel deploy` or platform's CLI

**Update Google Console:**
1. Add production URLs to authorized origins + redirect URIs
2. Add your domain to Twilio authorized URLs (if required)
3. Update SMTP if using production email service

---

## Summary

| Service | What It Does | Where to Configure |
|---------|-------------|-------------------|
| **Gmail SMTP** | Send OTP emails | `.env` + Gmail App Password |
| **Twilio** | Send OTP SMS | `.env` + Twilio Console |
| **Google OAuth** | "Sign in with Google" button | `.env` + Google Cloud Console + frontend |
| **MySQL** | Store all data | `.env` + local/Docker |

Once all 4 are configured, every login method works!
