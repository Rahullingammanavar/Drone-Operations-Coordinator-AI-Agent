"""
Drone Operations Coordinator AI Agent
Main Streamlit Application
"""

import streamlit as st
import os
from dotenv import load_dotenv
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.sheets_manager import get_sheets_manager
from src.conflict_detector import ConflictDetector
import google.generativeai as genai
import pandas as pd

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Drone Ops Coordinator AI",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sheets_manager' not in st.session_state:
    st.session_state.sheets_manager = None


# Initialize Gemini
@st.cache_resource
def init_gemini():
    """Initialize Gemini API"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        # Try to get from Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets['GEMINI_API_KEY']
        except:
            pass
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment or secrets")
    
    genai.configure(api_key=api_key)
    # Use the latest model name
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model


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
        # Simple status update handler
        return "To update status, please use the format: 'Update pilot P001 status to Available'"
    
    # Default: Use Gemini for general queries
    else:
        try:
            model = init_gemini()
            
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
            
            response = model.generate_content(context)
            return response.text
            
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_details = traceback.format_exc()
            print(f"Gemini API Error: {str(e)}\n{error_details}")
            
            return f"I can help you with:\n- Viewing pilots/drones/missions\n- Checking conflicts\n- Suggesting assignments\n- Updating statuses\n\nTry: 'Show available pilots in Bangalore' or 'Suggest assignment for PRJ001'\n\n*(AI response unavailable: {str(e)})*"


# Main UI
def main():
    st.markdown('<div class="main-header">🚁 Drone Operations Coordinator AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent coordination for Skylark Drones fleet & pilot management</div>', unsafe_allow_html=True)
    
    # Initialize managers
    try:
        sheets_manager = init_sheets_manager()
    except Exception as e:
        st.error(f"❌ Failed to connect to Google Sheets: {str(e)}")
        st.info("Please check your credentials.json file and Google Sheets permissions.")
        return
    
    # Sidebar with status
    with st.sidebar:
        st.header("📊 Fleet Status")
        
        pilot_summary = get_pilot_summary(sheets_manager)
        drone_summary = get_drone_summary(sheets_manager)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Pilots", pilot_summary['total'])
            st.metric("Available", pilot_summary['available'], delta=None)
        with col2:
            st.metric("Total Drones", drone_summary['total'])
            st.metric("Available", drone_summary['available'], delta=None)
        
        st.divider()
        
        st.subheader("🔄 Quick Actions")
        if st.button("🔍 Check All Conflicts"):
            with st.chat_message("assistant"):
                result = process_query("check conflicts", sheets_manager)
                st.markdown(result)
        
        if st.button("📋 Show All Pilots"):
            with st.chat_message("assistant"):
                result = process_query("show all pilots", sheets_manager)
                st.markdown(result)
        
        if st.button("🚁 Show All Drones"):
            with st.chat_message("assistant"):
                result = process_query("show all drones", sheets_manager)
                st.markdown(result)
        
        st.divider()
        st.caption(" Built for Skylark Drones Technical Assessment")
    
    # Main chat interface
    st.header("💬 Chat with the Coordinator")
    
    # Display example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - **"Show available pilots in Bangalore"**
        - **"Which drones can handle thermal imaging in Mumbai?"**
        - **"Suggest assignment for PRJ002"**
        - **"Check all conflicts"**
        - **"Show urgent missions"**
        - **"List all available drones"**
        """)
    
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
