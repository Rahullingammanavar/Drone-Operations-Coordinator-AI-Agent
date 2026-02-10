# 🚁 Drone Operations Coordinator AI Agent

An intelligent AI agent that automates drone operations coordination for Skylark Drones, handling pilot roster management, drone fleet tracking, assignment coordination, and conflict detection.

## 📋 Problem Statement

Skylark Drones operates a fleet of drones and pilots across multiple client projects simultaneously. This AI agent replaces manual coordination by:

- **Pilot Roster Management**: Tracking availability, skills, certifications, and assignments
- **Drone Fleet Tracking**: Monitoring status, capabilities, location, and maintenance
- **Smart Assignment Matching**: Pairing the right pilot with the right drone for each project
- **Conflict Detection**: Identifying scheduling conflicts, skill mismatches, and equipment issues
- **Urgent Reassignments**: Handling last-minute changes efficiently

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   User Query    │
│  (Chat Interface)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Agent      │
│  (LangChain +   │
│   Gemini API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Conflict        │◄─────┤ Google Sheets    │
│ Detector        │      │ Integration      │
└─────────────────┘      │ (2-way sync)     │
         │               └──────────────────┘
         ▼
┌─────────────────┐
│  Assignment     │
│  Matcher        │
└─────────────────┘
```

## 🚀 Features

### Core Functionality
✅ **Roster Management**
- Query pilot availability by skill, certification, location
- View current assignments
- Update pilot status (syncs back to Google Sheet)

✅ **Assignment Tracking**
- Match pilots to projects based on requirements
- Track active assignments
- Handle reassignments

✅ **Drone Inventory**
- Query fleet by capability, availability, location
- Track deployment status
- Flag maintenance issues

✅ **Conflict Detection**
- Double-booking detection (pilot or drone assigned to overlapping projects)
- Skill/certification mismatch warnings
- Equipment-pilot location mismatch alerts
- Maintenance status validation

### Edge Cases Handled
⚠️ Pilot assigned to overlapping project dates  
⚠️ Pilot assigned to job requiring certification they lack  
⚠️ Drone assigned but currently in maintenance  
⚠️ Pilot and assigned drone in different locations  

## 💻 Tech Stack

- **AI Framework**: LangChain + Google Gemini API
- **Backend**: Python + Flask
- **Frontend**: HTML/CSS/JavaScript (Chat Interface)
- **Data Integration**: Google Sheets API (`gspread`)
- **Deployment**: Replit / Vercel
- **Version Control**: Git + GitHub

## 📦 Installation

### Prerequisites
- Python 3.9+
- Google Cloud account (for Sheets API)
- Gemini API key

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/drone-ops-coordinator-agent.git
cd drone-ops-coordinator-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_SHEETS_CREDENTIALS=path_to_credentials.json
```

5. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000` to interact with the agent.

## 📊 Data Structure

### Pilot Roster
- `pilot_id`, `name`, `skills`, `certifications`, `location`, `status`, `current_assignment`, `available_from`

### Drone Fleet
- `drone_id`, `model`, `capabilities`, `status`, `location`, `current_assignment`, `maintenance_due`

### Missions
- `project_id`, `client`, `location`, `required_skills`, `required_certs`, `start_date`, `end_date`, `priority`

## 💬 Example Queries

```
"Show me all available pilots in Bangalore"
"Which drone can handle thermal imaging in Mumbai?"
"Assign a pilot to Project PRJ002"
"Are there any scheduling conflicts?"
"I need to reassign Project-A urgently"
```

## 📝 Decision Log

See [Decision_Log.md](./Decision_Log.md) for detailed technical decisions, trade-offs, and assumptions.

## 🎯 Project Status

- [x] Project setup
- [x] Google Sheets integration
- [x] AI agent implementation
- [x] Conflict detection
- [x] Assignment matching
- [x] Deployment
- [x] Documentation

## 👤 Author

**Rahul K Lingammanava**  
Built as a technical assignment for Skylark Drones

## 📄 License

This project is created for educational and assessment purposes.

---

**Last Updated**: February 10, 2026
