# 📊 Google Sheets Setup Guide - Step by Step

## Overview
We need to:
1. Create a Google Sheet with your CSV data
2. Set up Google Sheets API access
3. Get credentials for the Python app to read/write data

**Estimated Time:** 15 minutes

---

## Part 1: Create Google Sheet (5 minutes)

### Step 1.1: Create New Spreadsheet
1. Go to: **https://sheets.google.com**
2. Click **"+ Blank"** to create a new spreadsheet
3. Rename it: **"Drone Operations Data"**

### Step 1.2: Create Three Sheets
Your spreadsheet needs 3 tabs (sheets):
- `pilot_roster`
- `drone_fleet`
- `missions`

**How to add sheets:**
1. Click the **"+"** button at the bottom left (next to "Sheet1")
2. Rename each sheet by right-clicking → "Rename"

### Step 1.3: Copy Data from CSV Files

**For Pilot Roster:**
1. Click on the `pilot_roster` sheet tab
2. Open your local file: `data/pilot_roster.csv`
3. Copy ALL the content (Ctrl+A, Ctrl+C)
4. Paste into cell A1 of the Google Sheet (Ctrl+V)
5. Click **File → Convert to Google Sheets** if prompted

**Repeat for:**
- `drone_fleet` sheet ← Copy from `data/drone_fleet.csv`
- `missions` sheet ← Copy from `data/missions.csv`

### Step 1.4: Get Spreadsheet ID
1. Look at the URL in your browser. It looks like:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
2. Copy the **SPREADSHEET_ID** (the long string between `/d/` and `/edit`)
3. **Save this ID** - you'll need it later!

**Example:**
```
https://docs.google.com/spreadsheets/d/1A2B3C4D5E6F7G8H9I0J/edit
                                    ^^^^^^^^^^^^^^^^^^^^
                                    This is your ID!
```

---

## Part 2: Set Up Google Sheets API (10 minutes)

### Step 2.1: Create Google Cloud Project
1. Go to: **https://console.cloud.google.com/**
2. Click **"Select a Project"** dropdown at the top
3. Click **"New Project"**
4. Project name: **"Drone Operations Agent"**
5. Click **"Create"**
6. Wait for the project to be created (notification will appear)
7. **Select your new project** from the dropdown

### Step 2.2: Enable Google Sheets API
1. In the search bar at the top, type: **"Google Sheets API"**
2. Click on **"Google Sheets API"** from results
3. Click the blue **"Enable"** button
4. Wait for it to enable (takes ~10 seconds)

### Step 2.3: Create Service Account
1. In the left sidebar, click **"Credentials"**
2. Click **"+ Create Credentials"** at the top
3. Select **"Service Account"**

**Fill in the form:**
- Service account name: `drone-ops-agent`
- Service account ID: (auto-filled, leave it)
- Description: `Service account for drone operations coordinator agent`
- Click **"Create and Continue"**

**Grant permissions:**
- Role: Select **"Editor"** (use the search box)
- Click **"Continue"**
- Click **"Done"**

### Step 2.4: Create Service Account Key (JSON)
1. You'll see your service accounts listed
2. Click on the **email address** of your new service account (looks like: `drone-ops-agent@...`)
3. Go to the **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Choose **JSON** format
6. Click **"Create"**
7. A JSON file will download automatically (e.g., `drone-ops-agent-xxx.json`)

**Important:** 
- **Rename this file to:** `credentials.json`
- **Move it to your project folder:** `Drone Operations Coordinator AI Agent/credentials.json`
- This file contains secrets - **never commit it to GitHub!** (it's already in .gitignore)

### Step 2.5: Share Google Sheet with Service Account
1. Open the downloaded `credentials.json` file
2. Find the line with `"client_email"` - it looks like:
   ```json
   "client_email": "drone-ops-agent@drone-ops-agent-xxxxx.iam.gserviceaccount.com"
   ```
3. **Copy that email address**
4. Go back to your **Google Sheet** (Drone Operations Data)
5. Click the **"Share"** button (top right)
6. **Paste the service account email**
7. Make sure it has **"Editor"** access
8. **Uncheck** "Notify people" (it's a robot, not a person!)
9. Click **"Share"** or **"Send"**

---

## Part 3: Create .env File (2 minutes)

### Step 3.1: Get Gemini API Key
1. Go to: **https://aistudio.google.com/app/apikey**
2. Click **"Create API Key"**
3. Select your project or create a new one
4. Copy the API key

### Step 3.2: Create .env File
1. In your project folder, create a file named `.env` (no extension!)
2. Copy the content from `.env.example`
3. Fill in your actual values:

```env
# Google Gemini API Key
GEMINI_API_KEY=AIza...your_actual_api_key_here

# Google Sheets Spreadsheet ID (from Part 1.4)
GOOGLE_SHEETS_ID=1A2B3C4D5E6F7G8H9I0J

# Google Service Account Credentials
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

**Save the file!**

---

## ✅ Verification Checklist

Before moving on, verify you have:

- [ ] Google Sheet created with 3 tabs: `pilot_roster`, `drone_fleet`, `missions`
- [ ] CSV data copied into each sheet
- [ ] Spreadsheet ID saved
- [ ] Google Sheets API enabled in Google Cloud
- [ ] Service account created
- [ ] `credentials.json` file downloaded and in project folder
- [ ] Google Sheet shared with service account email
- [ ] Gemini API key obtained
- [ ] `.env` file created with all values filled in

---

## 🚨 Common Issues & Solutions

### Issue 1: "Permission denied" when running the app
**Solution:** Make sure you shared the Google Sheet with the service account email (from credentials.json)

### Issue 2: "File not found: credentials.json"
**Solution:** 
- Check the file is in the project root folder
- Check it's named exactly `credentials.json` (not `credentials.json.txt`)

### Issue 3: "Invalid API key"
**Solution:** 
- Check you copied the full API key from Google AI Studio
- Check there are no extra spaces in the `.env` file

### Issue 4: "Spreadsheet not found"
**Solution:** 
- Verify the GOOGLE_SHEETS_ID in .env matches your sheet URL
- Make sure the sheet is shared with the service account

---

## 🎯 Next Steps

Once you've completed this setup:
1. Test the connection (I'll help you with this)
2. Start building the AI agent
3. Implement the core features

---

**Need help with any step? Let me know!**
