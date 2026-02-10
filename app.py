"""
Drone Operations Coordinator AI Agent
Main Streamlit Application
Version: 2.0 with Full CRUD Support
"""

import streamlit as st
import os
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Force reload of modules (for Streamlit Cloud)
import importlib
if 'src.sheets_manager' in sys.modules:
    importlib.reload(sys.modules['src.sheets_manager'])
if 'src.conflict_detector' in sys.modules:
    importlib.reload(sys.modules['src.conflict_detector'])

from src.sheets_manager import get_sheets_manager
from src.conflict_detector import ConflictDetector
import pandas as pd
import requests

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Drone Ops Coordinator AI",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, Simple UI
st.markdown("""
<style>
    .title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .stat-box {
        background: #f0f7ff;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .stat-number {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0066cc;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #666;
    }
    .btn-primary {
        background: #0066cc;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 0.85rem;
        cursor: pointer;
    }
    .btn-secondary {
        background: #e8f0fe;
        color: #0066cc;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.8rem;
        cursor: pointer;
    }
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        margin: 16px 0 8px 0;
    }
    .help-box {
        background: #f8f9fa;
        border-left: 3px solid #0066cc;
        padding: 12px;
        margin: 8px 0;
        font-size: 0.85rem;
    }
    .command-tag {
        background: #e8f0fe;
        color: #0066cc;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sheets_manager' not in st.session_state:
    st.session_state.sheets_manager = None


# Initialize Groq AI
@st.cache_resource
def init_groq():
    """Initialize Groq AI API"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        # Try to get from Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
                api_key = st.secrets['GROQ_API_KEY']
        except:
            pass
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment or secrets")
    
    return api_key


# Initialize Sheets Manager
@st.cache_resource
def init_sheets_manager():
    """Initialize Google Sheets connection"""
    return get_sheets_manager()


def get_pilot_summary(sheets_manager):
    """Get summary of pilot roster"""
    pilots = sheets_manager.get_pilots()
    
    # Normalize column names (lowercase and strip spaces)
    pilots.columns = pilots.columns.str.lower().str.strip()
    
    total = len(pilots)
    
    # Handle case where 'status' column might not exist
    if 'status' not in pilots.columns:
        return {'total': total, 'available': 0, 'assigned': 0, 'on_leave': 0}
    
    available = len(pilots[pilots['status'] == 'Available'])
    assigned = len(pilots[pilots['status'] == 'Assigned'])
    on_leave = len(pilots[pilots['status'] == 'On Leave'])
    
    return {
        'total': total,
        'available': available,
        'assigned': assigned,
        'on_leave': on_leave
    }


def get_drone_summary(sheets_manager):
    """Get summary of drone fleet"""
    drones = sheets_manager.get_drones()
    
    # Normalize column names (lowercase and strip spaces)
    drones.columns = drones.columns.str.lower().str.strip()
    
    total = len(drones)
    
    # Handle case where 'status' column might not exist
    if 'status' not in drones.columns:
        return {'total': total, 'available': 0, 'maintenance': 0, 'assigned': 0}
    
    available = len(drones[drones['status'] == 'Available'])
    maintenance = len(drones[drones['status'] == 'Maintenance'])
    assigned = len(drones[drones['status'] == 'Assigned'])
    
    return {
        'total': total,
        'available': available,
        'maintenance': maintenance,
        'assigned': assigned
    }


def format_pilot_info(pilot_row):
    """Format pilot information for display"""
    return f"""
**{pilot_row.get('name', 'N/A')}** (ID: {pilot_row.get('pilot_id', 'N/A')})
- **Skills**: {pilot_row.get('skills', 'N/A')}
- **Certifications**: {pilot_row.get('certifications', 'N/A')}
- **Location**: {pilot_row.get('location', 'N/A')}
- **Status**: {pilot_row.get('status', 'N/A')}
- **Current Assignment**: {pilot_row.get('current_assignment', 'N/A')}
- **Available From**: {pilot_row.get('available_from', 'N/A')}
"""


def format_drone_info(drone_row):
    """Format drone information for display"""
    return f"""
**{drone_row.get('model', 'N/A')}** (ID: {drone_row.get('drone_id', 'N/A')})
- **Capabilities**: {drone_row.get('capabilities', 'N/A')}
- **Location**: {drone_row.get('location', 'N/A')}
- **Status**: {drone_row.get('status', 'N/A')}
- **Current Assignment**: {drone_row.get('current_assignment', 'N/A')}
- **Maintenance Due**: {drone_row.get('maintenance_due', 'N/A')}
"""


def format_mission_info(mission_row):
    """Format mission information for display"""
    return f"""
**{mission_row.get('project_id', 'N/A')}** - {mission_row.get('client', 'N/A')}
- **Location**: {mission_row.get('location', 'N/A')}
- **Required Skills**: {mission_row.get('required_skills', 'N/A')}
- **Required Certifications**: {mission_row.get('required_certs', 'N/A')}
- **Duration**: {mission_row.get('start_date', 'N/A')} to {mission_row.get('end_date', 'N/A')}
- **Priority**: {mission_row.get('priority', 'N/A')}
"""


def process_query(query: str, sheets_manager) -> str:
    """Process user query and generate response"""
    
    query_lower = query.lower()
    
    # Query pilots
    if 'pilot' in query_lower and ('show' in query_lower or 'list' in query_lower or 'available' in query_lower):
        pilots = sheets_manager.get_pilots()
        
        if len(pilots) == 0:
            return "No pilot data available in the system."
        
        # Normalize column names
        pilots.columns = pilots.columns.str.lower().str.strip()
        
        # Check if required columns exist
        if 'status' not in pilots.columns:
            return f"Error: 'status' column not found in pilots data. Available columns: {list(pilots.columns)}"
        
        # Filter based on query
        if 'available' in query_lower:
            pilots = pilots[pilots['status'] == 'Available']
        
        if 'bangalore' in query_lower and 'location' in pilots.columns:
            pilots = pilots[pilots['location'].str.contains('Bangalore', case=False, na=False)]
        elif 'mumbai' in query_lower and 'location' in pilots.columns:
            pilots = pilots[pilots['location'].str.contains('Mumbai', case=False, na=False)]
        
        if len(pilots) == 0:
            return "No pilots found matching your criteria."
        
        response = f"Found **{len(pilots)}** pilot(s):\n\n"
        for idx, pilot in pilots.iterrows():
            response += format_pilot_info(pilot) + "\n---\n"
        
        return response
    
    # Query drones
    elif 'drone' in query_lower and ('show' in query_lower or 'list' in query_lower or 'available' in query_lower):
        drones = sheets_manager.get_drones()
        
        if len(drones) == 0:
            return "No drone data available in the system."
        
        # Normalize column names
        drones.columns = drones.columns.str.lower().str.strip()
        
        # Check if required columns exist
        if 'status' not in drones.columns:
            return f"Error: 'status' column not found in drones data. Available columns: {list(drones.columns)}"
        
        # Filter based on query
        if 'available' in query_lower:
            drones = drones[drones['status'] == 'Available']
        
        if 'thermal' in query_lower and 'capabilities' in drones.columns:
            drones = drones[drones['capabilities'].str.contains('Thermal', case=False, na=False)]
        
        if 'bangalore' in query_lower and 'location' in drones.columns:
            drones = drones[drones['location'].str.contains('Bangalore', case=False, na=False)]
        elif 'mumbai' in query_lower and 'location' in drones.columns:
            drones = drones[drones['location'].str.contains('Mumbai', case=False, na=False)]
        
        if len(drones) == 0:
            return "No drones found matching your criteria."
        
        response = f"Found **{len(drones)}** drone(s):\n\n"
        for idx, drone in drones.iterrows():
            response += format_drone_info(drone) + "\n---\n"
        
        return response
    
    # Query missions
    elif 'mission' in query_lower or 'project' in query_lower:
        missions = sheets_manager.get_missions()
        
        if len(missions) == 0:
            return "No mission data available in the system."
        
        # Normalize column names
        missions.columns = missions.columns.str.lower().str.strip()
        
        if 'urgent' in query_lower and 'priority' in missions.columns:
            missions = missions[missions['priority'].str.contains('Urgent', case=False, na=False)]
        
        response = f"Found **{len(missions)}** mission(s):\n\n"
        for idx, mission in missions.iterrows():
            response += format_mission_info(mission) + "\n---\n"
        
        return response
    
    # Check conflicts
    elif 'conflict' in query_lower:
        pilots = sheets_manager.get_pilots()
        drones = sheets_manager.get_drones()
        missions = sheets_manager.get_missions()
        # Normalize column names
        pilots.columns = pilots.columns.str.lower().str.strip()
        drones.columns = drones.columns.str.lower().str.strip()
        missions.columns = missions.columns.str.lower().str.strip()
        
        all_conflicts = []
        
        # Check assigned pilots and drones
        for idx, pilot in pilots.iterrows():
            pilot_status = pilot.get('status', '')
            if pilot_status == 'Assigned':
                pilot_name = pilot.get('name', 'Unknown')
                current_assignment = pilot.get('current_assignment', 'Unknown')
                all_conflicts.append(f"⚠️ Pilot {pilot_name} is assigned to {current_assignment}")
        
        for idx, drone in drones.iterrows():
            drone_status = drone.get('status', '')
            drone_id = drone.get('drone_id', 'Unknown')
            if drone_status == 'Maintenance':
                all_conflicts.append(f"🚨 Drone {drone_id} is in maintenance")
            elif drone_status == 'Assigned':
                current_assignment = drone.get('current_assignment', 'Unknown')
                all_conflicts.append(f"⚠️ Drone {drone_id} is assigned to {current_assignment}")
        
        if len(all_conflicts) == 0:
            return "✅ No conflicts detected! All systems operational."
        
        response = f"Found **{len(all_conflicts)}** conflict(s):\n\n"
        for conflict in all_conflicts:
            response += f"- {conflict}\n"
        
        return response
    
    # Suggest assignment
    elif 'suggest' in query_lower or 'recommend' in query_lower or 'assign' in query_lower:
        # Extract project ID if mentioned
        project_id = None
        for word in query.split():
            if word.startswith('PRJ'):
                project_id = word
                break
        
        if not project_id:
            return "Please specify a project ID (e.g., PRJ001) to get assignment suggestions."
        
        missions = sheets_manager.get_missions()
        # Normalize column names
        missions.columns = missions.columns.str.lower().str.strip()
        
        if 'project_id' not in missions.columns:
            return f"Error: 'project_id' column not found in missions data. Available columns: {list(missions.columns)}"
        
        mission = missions[missions['project_id'] == project_id]
        
        if len(mission) == 0:
            return f"Project {project_id} not found."
        
        mission = mission.iloc[0].to_dict()
        
        # Find suitable pilots and drones
        pilots = sheets_manager.get_pilots()
        drones = sheets_manager.get_drones()
        # Normalize column names
        pilots.columns = pilots.columns.str.lower().str.strip()
        drones.columns = drones.columns.str.lower().str.strip()
        
        # Check if required columns exist
        if 'status' not in pilots.columns:
            return f"Error: 'status' column not found in pilots data. Available columns: {list(pilots.columns)}"
        if 'status' not in drones.columns:
            return f"Error: 'status' column not found in drones data. Available columns: {list(drones.columns)}"
        
        available_pilots = pilots[pilots['status'] == 'Available']
        available_drones = drones[drones['status'] == 'Available']
        
        # Filter by location
        location_pilots = available_pilots[available_pilots['location'] == mission['location']]
        location_drones = available_drones[available_drones['location'] == mission['location']]
        
        if len(location_pilots) == 0 or len(location_drones) == 0:
            return f"⚠️ No available pilot-drone pairs found in {mission['location']} for {project_id}"
        
        # Check conflicts for first match
        pilot = location_pilots.iloc[0].to_dict()
        drone = location_drones.iloc[0].to_dict()
        
        conflict_check = ConflictDetector.full_assignment_check(pilot, drone, mission)
        
        response = f"## Assignment Suggestion for {project_id}\n\n"
        response += "### Recommended Pilot:\n"
        response += format_pilot_info(pilot)
        response += "\n### Recommended Drone:\n"
        response += format_drone_info(drone)
        
        if conflict_check['conflicts']:
            response += "\n### 🚨 Conflicts:\n"
            for conflict in conflict_check['conflicts']:
                response += f"- {conflict}\n"
        
        if conflict_check['warnings']:
            response += "\n### ⚠️ Warnings:\n"
            for warning in conflict_check['warnings']:
                response += f"- {warning}\n"
        
        if conflict_check['is_valid']:
            response += "\n✅ **This assignment is VALID and ready to proceed!**"
        else:
            response += "\n❌ **This assignment has conflicts that must be resolved first.**"
        
        return response
    
    # Update status
    elif 'update' in query_lower and 'status' in query_lower:
        # Parse update command: "update pilot P001 status to Available" or "update drone D001 status to Maintenance"
        import re
        
        # Try to match pilot update pattern
        pilot_match = re.search(r'update\s+pilot\s+(\w+)\s+status\s+to\s+(\w+)', query_lower)
        drone_match = re.search(r'update\s+drone\s+(\w+)\s+status\s+to\s+(\w+)', query_lower)
        
        if pilot_match:
            pilot_id = pilot_match.group(1).upper()
            new_status = pilot_match.group(2).capitalize()
            
            # Validate status
            valid_statuses = ['Available', 'Assigned', 'On Leave']
            if new_status not in valid_statuses:
                return f"❌ Invalid status '{new_status}'. Valid statuses: {', '.join(valid_statuses)}"
            
            # Update pilot status
            success = sheets_manager.update_pilot_status(pilot_id, new_status)
            if success:
                return f"✅ Successfully updated pilot {pilot_id} status to **{new_status}**"
            else:
                return f"❌ Failed to update pilot {pilot_id}. Pilot ID not found."
        
        elif drone_match:
            drone_id = drone_match.group(1).upper()
            new_status = drone_match.group(2).capitalize()
            
            valid_statuses = ['Available', 'Assigned', 'Maintenance']
            if new_status not in valid_statuses:
                return f"❌ Invalid status '{new_status}'. Valid statuses: {', '.join(valid_statuses)}"
            
            # Update drone status
            success = sheets_manager.update_drone_status(drone_id, new_status)
            if success:
                return f"✅ Successfully updated drone {drone_id} status to **{new_status}**"
            else:
                return f"❌ Failed to update drone {drone_id}. Drone ID not found."
        
        else:
            return """To update status, use these formats:

**Pilot Status:**
- "Update pilot P001 status to Available"
- "Update pilot P002 status to Assigned"  
- "Update pilot P003 status to On Leave"

**Drone Status:**
- "Update drone D001 status to Available"
- "Update drone D002 status to Maintenance"
- "Update drone D003 status to Assigned"

Valid pilot statuses: Available, Assigned, On Leave
Valid drone statuses: Available, Maintenance, Assigned"""
    
    # Add new drone
    elif 'add' in query_lower and 'drone' in query_lower:
        # Parse: "Add drone D005 model DJI M300 capabilities RGB, Thermal location Bangalore"
        import re
        
        # Extract drone details
        drone_id_match = re.search(r'drone\s+(\w+)', query_lower)
        model_match = re.search(r'model\s+([\w\s]+?)(?:\s+capabilities|\s+location|$)', query_lower)
        capabilities_match = re.search(r'capabilities\s+([\w,\s]+?)(?:\s+location|$)', query_lower)
        location_match = re.search(r'location\s+(\w+)', query_lower)
        
        if not all([drone_id_match, model_match, capabilities_match, location_match]):
            return """To add a drone, use this format:
"Add drone D005 model DJI M300 capabilities RGB, Thermal location Bangalore"

Required fields:
- drone_id (e.g., D005)
- model (e.g., DJI M300)
- capabilities (e.g., RGB, Thermal, LiDAR)
- location (e.g., Bangalore, Mumbai)"""
        
        drone_data = {
            'drone_id': drone_id_match.group(1).upper(),
            'model': model_match.group(1).strip().title(),
            'capabilities': capabilities_match.group(1).strip().title(),
            'location': location_match.group(1).strip().title(),
            'status': 'Available',
            'current_assignment': '–',
            'maintenance_due': '2026-12-31'
        }
        
        success = sheets_manager.add_drone(drone_data)
        if success:
            return f"✅ Successfully added drone **{drone_data['drone_id']}** ({drone_data['model']}) with {drone_data['capabilities']} capabilities in {drone_data['location']}"
        else:
            return f"❌ Failed to add drone. Drone ID {drone_data['drone_id']} may already exist."
    
    # Add new pilot
    elif 'add' in query_lower and 'pilot' in query_lower:
        # Parse: "Add pilot P005 name Rahul skills Mapping, Survey certifications DGCA location Bangalore"
        import re
        
        # Extract pilot details
        pilot_id_match = re.search(r'pilot\s+(\w+)', query_lower)
        name_match = re.search(r'name\s+([\w\s]+?)(?:\s+skills|\s+certifications|\s+location|$)', query_lower)
        skills_match = re.search(r'skills\s+([\w,\s]+?)(?:\s+certifications|\s+location|$)', query_lower)
        certs_match = re.search(r'certifications\s+([\w,\s]+?)(?:\s+location|$)', query_lower)
        location_match = re.search(r'location\s+(\w+)', query_lower)
        
        if not all([pilot_id_match, name_match, skills_match, certs_match, location_match]):
            return """To add a pilot, use this format:
"Add pilot P005 name Rahul skills Mapping, Survey certifications DGCA location Bangalore"

Required fields:
- pilot_id (e.g., P005)
- name (e.g., Rahul)
- skills (e.g., Mapping, Survey, Inspection, Thermal)
- certifications (e.g., DGCA, Night Ops)
- location (e.g., Bangalore, Mumbai)"""
        
        pilot_data = {
            'pilot_id': pilot_id_match.group(1).upper(),
            'name': name_match.group(1).strip().title(),
            'skills': skills_match.group(1).strip().title(),
            'certifications': certs_match.group(1).strip().upper(),
            'location': location_match.group(1).strip().title(),
            'status': 'Available',
            'current_assignment': '–',
            'available_from': '–'
        }
        
        success = sheets_manager.add_pilot(pilot_data)
        if success:
            return f"✅ Successfully added pilot **{pilot_data['name']}** ({pilot_data['pilot_id']}) with skills: {pilot_data['skills']} in {pilot_data['location']}"
        else:
            return f"❌ Failed to add pilot. Pilot ID {pilot_data['pilot_id']} may already exist."
    
    # Delete drone
    elif 'delete' in query_lower and 'drone' in query_lower:
        import re
        drone_id_match = re.search(r'drone\s+(\w+)', query_lower)
        
        if not drone_id_match:
            return "To delete a drone, use: 'Delete drone D001'"
        
        drone_id = drone_id_match.group(1).upper()
        success = sheets_manager.delete_drone(drone_id)
        if success:
            return f"✅ Successfully deleted drone **{drone_id}**"
        else:
            return f"❌ Failed to delete drone {drone_id}. Drone not found."
    
    # Delete pilot
    elif 'delete' in query_lower and 'pilot' in query_lower:
        import re
        pilot_id_match = re.search(r'pilot\s+(\w+)', query_lower)
        
        if not pilot_id_match:
            return "To delete a pilot, use: 'Delete pilot P001'"
        
        pilot_id = pilot_id_match.group(1).upper()
        success = sheets_manager.delete_pilot(pilot_id)
        if success:
            return f"✅ Successfully deleted pilot **{pilot_id}**"
        else:
            return f"❌ Failed to delete pilot {pilot_id}. Pilot not found."
    
    # Default: Use AI for general queries
    else:
        try:
            # Build context
            pilots = sheets_manager.get_pilots()
            drones = sheets_manager.get_drones()
            missions = sheets_manager.get_missions()
            
            # Normalize column names
            pilots.columns = pilots.columns.str.lower().str.strip()
            drones.columns = drones.columns.str.lower().str.strip()
            missions.columns = missions.columns.str.lower().str.strip()
            
            # Calculate available counts safely
            pilots_available = len(pilots[pilots['status']=='Available']) if 'status' in pilots.columns else 0
            drones_available = len(drones[drones['status']=='Available']) if 'status' in drones.columns else 0
            
            context = f"""
You are a Drone Operations Coordinator AI assistant for Skylark Drones.

Current Status:
- Pilots: {len(pilots)} total ({pilots_available} available)
- Drones: {len(drones)} total ({drones_available} available)
- Missions: {len(missions)} total

Pilot Data:
{pilots.to_string()}

Drone Data:
{drones.to_string()}

Mission Data:
{missions.to_string()}

User Query: {query}

Provide a helpful, concise response based on the available data.
"""
            
            # Call Groq API
            api_key = init_groq()
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a Drone Operations Coordinator AI assistant for Skylark Drones. Provide helpful, concise responses based on the data provided."},
                    {"role": "user", "content": context}
                ],
                "max_tokens": 500
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"I can help you with:\n- Viewing pilots/drones/missions\n- Checking conflicts\n- Suggesting assignments\n- Updating statuses\n\nTry: 'Show available pilots in Bangalore' or 'Suggest assignment for PRJ001'\n\n*(AI response unavailable: {response.status_code} - {response.text})*"
            
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_details = traceback.format_exc()
            print(f"Groq API Error: {str(e)}\n{error_details}")
            
            return f"I can help you with:\n- Viewing pilots/drones/missions\n- Checking conflicts\n- Suggesting assignments\n- Updating statuses\n\nTry: 'Show available pilots in Bangalore' or 'Suggest assignment for PRJ001'\n\n*(AI response unavailable: {str(e)})*"


# Main UI
def main():
    # Simple Header
    st.markdown('<div class="title">🚁 Skylark Drone Ops</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Manage your fleet and pilots easily</div>', unsafe_allow_html=True)
    
    # Initialize
    try:
        sheets_manager = init_sheets_manager()
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
        return
    
    # Sidebar - Simple Stats
    with st.sidebar:
        st.markdown('<div class="section-title">Fleet Status</div>', unsafe_allow_html=True)
        
        pilot_summary = get_pilot_summary(sheets_manager)
        drone_summary = get_drone_summary(sheets_manager)
        
        # Pilots
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{pilot_summary['available']}/{pilot_summary['total']}</div>
            <div class="stat-label">Pilots Available</div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Drones
        st.markdown(f'''
        <div class="stat-box">
            <div class="stat-number">{drone_summary['available']}/{drone_summary['total']}</div>
            <div class="stat-label">Drones Available</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("📋 All Pilots", use_container_width=True):
            with st.chat_message("assistant"):
                result = process_query("show all pilots", sheets_manager)
                st.markdown(result)
        
        if st.button("🚁 All Drones", use_container_width=True):
            with st.chat_message("assistant"):
                result = process_query("show all drones", sheets_manager)
                st.markdown(result)
        
        if st.button("⚠️ Check Conflicts", use_container_width=True):
            with st.chat_message("assistant"):
                result = process_query("check conflicts", sheets_manager)
                st.markdown(result)
    
    # Main Area - Simple Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "➕ Add New", "📖 Help"])
    
    with tab1:
        # Chat Interface
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Type your command here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    response = process_query(prompt, sheets_manager)
                    st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    with tab2:
        st.markdown('<div class="section-title">Add New Pilot</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            p_id = st.text_input("Pilot ID", "P005", key="p_id")
            p_name = st.text_input("Name", "", key="p_name")
            p_skills = st.text_input("Skills (comma separated)", "Mapping, Survey", key="p_skills")
        with col2:
            p_certs = st.text_input("Certifications", "DGCA", key="p_certs")
            p_loc = st.selectbox("Location", ["Bangalore", "Mumbai"], key="p_loc")
            p_status = st.selectbox("Status", ["Available", "Assigned", "On Leave"], key="p_status")
        
        if st.button("➕ Add Pilot", type="primary"):
            pilot_data = {
                'pilot_id': p_id.upper(),
                'name': p_name,
                'skills': p_skills,
                'certifications': p_certs.upper(),
                'location': p_loc,
                'status': p_status,
                'current_assignment': '–',
                'available_from': '–'
            }
            success = sheets_manager.add_pilot(pilot_data)
            if success:
                st.success(f"✅ Pilot {p_name} added successfully!")
            else:
                st.error("❌ Failed to add pilot. ID may already exist.")
        
        st.divider()
        
        st.markdown('<div class="section-title">Add New Drone</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            d_id = st.text_input("Drone ID", "D005", key="d_id")
            d_model = st.text_input("Model", "DJI M300", key="d_model")
            d_caps = st.text_input("Capabilities", "RGB, Thermal", key="d_caps")
        with col2:
            d_loc = st.selectbox("Location", ["Bangalore", "Mumbai"], key="d_loc")
            d_status = st.selectbox("Drone Status", ["Available", "Maintenance", "Assigned"], key="d_status")
        
        if st.button("➕ Add Drone", type="primary"):
            drone_data = {
                'drone_id': d_id.upper(),
                'model': d_model,
                'capabilities': d_caps,
                'location': d_loc,
                'status': d_status,
                'current_assignment': '–',
                'maintenance_due': '2026-12-31'
            }
            success = sheets_manager.add_drone(drone_data)
            if success:
                st.success(f"✅ Drone {d_id.upper()} added successfully!")
            else:
                st.error("❌ Failed to add drone. ID may already exist.")
    
    with tab3:
        st.markdown('<div class="section-title">Common Commands</div>', unsafe_allow_html=True)
        
        st.markdown('''
        <div class="help-box">
            <b>🔍 Search & Query</b><br>
            <span class="command-tag">show pilots in Bangalore</span><br>
            <span class="command-tag">show available drones</span><br>
            <span class="command-tag">check conflicts</span><br>
            <span class="command-tag">suggest assignment for PRJ001</span>
        </div>
        
        <div class="help-box">
            <b>✏️ Update Status</b><br>
            <span class="command-tag">update pilot P001 status to Assigned</span><br>
            <span class="command-tag">update drone D001 status to Maintenance</span>
        </div>
        
        <div class="help-box">
            <b>🗑️ Delete</b><br>
            <span class="command-tag">delete pilot P005</span><br>
            <span class="command-tag">delete drone D005</span>
        </div>
        ''', unsafe_allow_html=True)
        
        st.info("💡 Tip: You can also use the 'Add New' tab above to add pilots and drones with a simple form!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about pilots, drones, missions, or conflicts..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_query(prompt, sheets_manager)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
