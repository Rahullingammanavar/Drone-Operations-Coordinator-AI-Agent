"""
Google Sheets Manager
Handles all read/write operations with Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()


class SheetsManager:
    """Manages Google Sheets data operations"""
    
    def __init__(self):
        """Initialize Google Sheets connection"""
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Try to load from Streamlit secrets first (for cloud deployment)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                # Use Streamlit secrets
                self.creds = Credentials.from_service_account_info(
                    st.secrets['gcp_service_account'],
                    scopes=self.scopes
                )
            else:
                # Fall back to local file
                credentials_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials.json')
                self.creds = Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.scopes
                )
        except ImportError:
            # Running without Streamlit, use local file
            credentials_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials.json')
            self.creds = Credentials.from_service_account_file(
                credentials_file,
                scopes=self.scopes
            )
        
        self.client = gspread.authorize(self.creds)
        
        # Get Sheets ID from Streamlit secrets or environment variable
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GOOGLE_SHEETS_ID' in st.secrets:
                self.spreadsheet_id = st.secrets['GOOGLE_SHEETS_ID']
            else:
                self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        except ImportError:
            self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
            
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        
        # Cache for sheets
        self.pilot_sheet = self.spreadsheet.worksheet('pilot_roster')
        self.drone_sheet = self.spreadsheet.worksheet('drone_fleet')
        self.missions_sheet = self.spreadsheet.worksheet('missions')
    
    def _fix_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix column names if they were read as a single comma-separated string"""
        if len(df.columns) == 1 and ',' in str(df.columns[0]):
            # The header was read as a single string, split it
            col_names = str(df.columns[0]).split(',')
            # Re-read the data properly
            df.columns = col_names
        return df
    
    def get_pilots(self) -> pd.DataFrame:
        """Get all pilots data as DataFrame"""
        data = self.pilot_sheet.get_all_records()
        df = pd.DataFrame(data)
        return self._fix_dataframe_columns(df)
    
    def get_drones(self) -> pd.DataFrame:
        """Get all drones data as DataFrame"""
        data = self.drone_sheet.get_all_records()
        df = pd.DataFrame(data)
        return self._fix_dataframe_columns(df)
    
    def get_missions(self) -> pd.DataFrame:
        """Get all missions data as DataFrame"""
        data = self.missions_sheet.get_all_records()
        df = pd.DataFrame(data)
        return self._fix_dataframe_columns(df)
    
    def update_pilot_status(self, pilot_id: str, new_status: str) -> bool:
        """
        Update pilot status in Google Sheet
        
        Args:
            pilot_id: Pilot ID (e.g., 'P001')
            new_status: New status ('Available', 'Assigned', 'On Leave')
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all pilot data
            pilots = self.pilot_sheet.get_all_records()
            
            # Find the pilot row (add 2: 1 for header, 1 for 0-indexing)
            for idx, pilot in enumerate(pilots):
                if pilot['pilot_id'] == pilot_id:
                    row_number = idx + 2  # +2 because of header and 1-indexing
                    # Update status column (column 6)
                    self.pilot_sheet.update_cell(row_number, 6, new_status)
                    return True
            
            return False
        except Exception as e:
            print(f"Error updating pilot status: {e}")
            return False
    
    def update_pilot_assignment(self, pilot_id: str, assignment: str, available_from: str = '–') -> bool:
        """
        Update pilot assignment in Google Sheet
        
        Args:
            pilot_id: Pilot ID
            assignment: Project ID or '–' for no assignment
            available_from: Date when pilot becomes available
        
        Returns:
            bool: True if successful
        """
        try:
            pilots = self.pilot_sheet.get_all_records()
            
            for idx, pilot in enumerate(pilots):
                if pilot['pilot_id'] == pilot_id:
                    row_number = idx + 2
                    # Update current_assignment (column 7) and available_from (column 8)
                    self.pilot_sheet.update_cell(row_number, 7, assignment)
                    if available_from != '–':
                        self.pilot_sheet.update_cell(row_number, 8, available_from)
                    return True
            
            return False
        except Exception as e:
            print(f"Error updating pilot assignment: {e}")
            return False
    
    def update_drone_assignment(self, drone_id: str, assignment: str) -> bool:
        """
        Update drone assignment in Google Sheet
        
        Args:
            drone_id: Drone ID (e.g., 'D001')
            assignment: Project ID or '–' for no assignment
        
        Returns:
            bool: True if successful
        """
        try:
            drones = self.drone_sheet.get_all_records()
            
            for idx, drone in enumerate(drones):
                if drone['drone_id'] == drone_id:
                    row_number = idx + 2
                    # Update current_assignment (column 6)
                    self.drone_sheet.update_cell(row_number, 6, assignment)
                    return True
            
            return False
        except Exception as e:
            print(f"Error updating drone assignment: {e}")
            return False
    
    def refresh_data(self):
        """Refresh cached data from Google Sheets"""
        # Re-fetch worksheets to get latest data
        self.pilot_sheet = self.spreadsheet.worksheet('pilot_roster')
        self.drone_sheet = self.spreadsheet.worksheet('drone_fleet')
        self.missions_sheet = self.spreadsheet.worksheet('missions')


# Singleton instance
_sheets_manager_instance = None


def get_sheets_manager() -> SheetsManager:
    """Get or create SheetsManager singleton instance"""
    global _sheets_manager_instance
    if _sheets_manager_instance is None:
        _sheets_manager_instance = SheetsManager()
    return _sheets_manager_instance
