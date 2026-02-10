# How to Run Locally

## Prerequisites
1. Python 3.9 or higher installed
2. All files in the project directory
3. `credentials.json` file in the root directory
4. `.env` file configured

## Steps

### 1. Create Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Verify Environment Variables
Make sure your `.env` file exists with:
```
GEMINI_API_KEY=your_key_here
GOOGLE_SHEETS_ID=your_sheet_id_here
GOOGLE_SERVICE_ACCOUNT_FILE=credentials.json
```

### 4. Run the Application
```powershell
streamlit run app.py
```

### 5. Open in Browser
The app will automatically open at: `http://localhost:8501`

If it doesn't open automatically, copy the URL from the terminal.

## Troubleshooting

### Error: "ModuleNotFoundError"
```powershell
pip install -r requirements.txt --upgrade
```

### Error: "Google Sheets connection failed"
1. Check that `credentials.json` is in the project root
2. Verify the Google Sheet is shared with the service account email
3. Check that GOOGLE_SHEETS_ID in `.env` matches your sheet

### Error: "Gemini API error"
1. Verify your API key in `.env`
2. Check API quota at: https://aistudio.google.com

## Testing the Agent

Try these example queries:
- "Show available pilots in Bangalore"
- "Which drones can handle thermal imaging?"
- "Suggest assignment for PRJ002"
- "Check all conflicts"
- "Show urgent missions"

## Stopping the App
Press `Ctrl + C` in the terminal

## Deactivating Virtual Environment
```powershell
deactivate
```
