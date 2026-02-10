"""
Conflict Detector
Identifies scheduling conflicts, skill mismatches, and equipment issues
"""

from datetime import datetime
from typing import List, Dict, Any
import pandas as pd


class ConflictDetector:
    """Detects various types of conflicts in drone operations"""
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse date string to datetime object"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None
    
    @staticmethod
    def check_pilot_availability(pilot_data: Dict, mission_start: str, mission_end: str) -> List[str]:
        """
        Check if pilot is available for a mission
        
        Returns:
            List of conflict messages (empty if no conflicts)
        """
        conflicts = []
        
        # Check status
        if pilot_data['status'] == 'On Leave':
            available_from = pilot_data.get('available_from', '–')
            conflicts.append(
                f"⚠️ Pilot {pilot_data['name']} is on leave until {available_from}"
            )
        
        if pilot_data['status'] == 'Assigned':
            current_assignment = pilot_data.get('current_assignment', 'Unknown')
            available_from = pilot_data.get('available_from', '–')
            conflicts.append(
                f"⚠️ Pilot {pilot_data['name']} is already assigned to {current_assignment} "
                f"(available from: {available_from})"
            )
        
        # Check if available_from date is after mission start
        if pilot_data.get('available_from') and pilot_data['available_from'] != '–':
            available_date = ConflictDetector.parse_date(pilot_data['available_from'])
            mission_start_date = ConflictDetector.parse_date(mission_start)
            
            if available_date and mission_start_date and available_date > mission_start_date:
                conflicts.append(
                    f"⚠️ Pilot {pilot_data['name']} won't be available until {pilot_data['available_from']}, "
                    f"but mission starts on {mission_start}"
                )
        
        return conflicts
    
    @staticmethod
    def check_skill_match(pilot_skills: str, required_skills: str) -> List[str]:
        """
        Check if pilot has required skills
        
        Args:
            pilot_skills: Comma-separated skills (e.g., "Mapping, Survey")
            required_skills: Required skills for mission
        
        Returns:
            List of warnings (empty if all skills match)
        """
        warnings = []
        
        # Parse skills (handle quoted strings)
        pilot_skills_list = [s.strip() for s in pilot_skills.split(',')]
        required_skills_list = [s.strip() for s in required_skills.split(',')]
        
        # Check if pilot has all required skills
        missing_skills = []
        for req_skill in required_skills_list:
            if req_skill not in pilot_skills_list:
                missing_skills.append(req_skill)
        
        if missing_skills:
            warnings.append(
                f"⚠️ Pilot is missing required skills: {', '.join(missing_skills)}"
            )
        
        return warnings
    
    @staticmethod
    def check_certification_match(pilot_certs: str, required_certs: str) -> List[str]:
        """
        Check if pilot has required certifications
        
        Returns:
            List of warnings (empty if all certs match)
        """
        warnings = []
        
        # Parse certifications
        pilot_certs_list = [c.strip() for c in pilot_certs.split(',')]
        required_certs_list = [c.strip() for c in required_certs.split(',')]
        
        # Check for missing certifications
        missing_certs = []
        for req_cert in required_certs_list:
            if req_cert not in pilot_certs_list:
                missing_certs.append(req_cert)
        
        if missing_certs:
            warnings.append(
                f"🚨 CRITICAL: Pilot lacks required certifications: {', '.join(missing_certs)}"
            )
        
        return warnings
    
    @staticmethod
    def check_location_match(pilot_location: str, mission_location: str) -> List[str]:
        """Check if pilot and mission are in same location"""
        warnings = []
        
        if pilot_location.strip() != mission_location.strip():
            warnings.append(
                f"⚠️ Location mismatch: Pilot is in {pilot_location}, "
                f"but mission is in {mission_location}. Travel arrangements needed."
            )
        
        return warnings
    
    @staticmethod
    def check_drone_availability(drone_data: Dict) -> List[str]:
        """Check if drone is available"""
        conflicts = []
        
        if drone_data['status'] == 'Maintenance':
            conflicts.append(
                f"🚨 CRITICAL: Drone {drone_data['drone_id']} ({drone_data['model']}) "
                f"is currently in maintenance"
            )
        
        if drone_data['status'] == 'Assigned':
            assignment = drone_data.get('current_assignment', 'Unknown')
            conflicts.append(
                f"⚠️ Drone {drone_data['drone_id']} is already assigned to {assignment}"
            )
        
        return conflicts
    
    @staticmethod
    def check_drone_capability(drone_capabilities: str, required_skills: str) -> List[str]:
        """Check if drone has required capabilities"""
        warnings = []
        
        # For simplicity, map skills to drone capabilities
        # e.g., "Thermal" skill needs "Thermal" capability
        drone_caps = [c.strip() for c in drone_capabilities.split(',')]
        required_skills_list = [s.strip() for s in required_skills.split(',')]
        
        # Mapping of skills to required capabilities
        skill_to_capability = {
            'Thermal': 'Thermal',
            'Mapping': 'LiDAR',
            'Survey': 'RGB',
            'Inspection': 'RGB'
        }
        
        missing_caps = []
        for skill in required_skills_list:
            required_cap = skill_to_capability.get(skill)
            if required_cap and required_cap not in drone_caps:
                missing_caps.append(required_cap)
        
        if missing_caps:
            warnings.append(
                f"⚠️ Drone may lack required capabilities: {', '.join(set(missing_caps))}"
            )
        
        return warnings
    
    @staticmethod
    def check_drone_location(drone_location: str, mission_location: str) -> List[str]:
        """Check if drone and mission are in same location"""
        warnings = []
        
        if drone_location.strip() != mission_location.strip():
            warnings.append(
                f"⚠️ Drone is in {drone_location}, but mission is in {mission_location}. "
                f"Logistics required."
            )
        
        return warnings
    
    @staticmethod
    def full_assignment_check(
        pilot_data: Dict,
        drone_data: Dict,
        mission_data: Dict
    ) -> Dict[str, Any]:
        """
        Run all conflict checks for a pilot-drone-mission assignment
        
        Returns:
            Dict with 'conflicts', 'warnings', and 'is_valid' keys
        """
        all_conflicts = []
        all_warnings = []
        
        # Pilot checks
        all_conflicts.extend(
            ConflictDetector.check_pilot_availability(
                pilot_data,
                mission_data['start_date'],
                mission_data['end_date']
            )
        )
        
        all_warnings.extend(
            ConflictDetector.check_skill_match(
                pilot_data['skills'],
                mission_data['required_skills']
            )
        )
        
        all_conflicts.extend(
            ConflictDetector.check_certification_match(
                pilot_data['certifications'],
                mission_data['required_certs']
            )
        )
        
        all_warnings.extend(
            ConflictDetector.check_location_match(
                pilot_data['location'],
                mission_data['location']
            )
        )
        
        # Drone checks
        all_conflicts.extend(
            ConflictDetector.check_drone_availability(drone_data)
        )
        
        all_warnings.extend(
            ConflictDetector.check_drone_capability(
                drone_data['capabilities'],
                mission_data['required_skills']
            )
        )
        
        all_warnings.extend(
            ConflictDetector.check_drone_location(
                drone_data['location'],
                mission_data['location']
            )
        )
        
        return {
            'conflicts': all_conflicts,
            'warnings': all_warnings,
            'is_valid': len(all_conflicts) == 0,
            'has_warnings': len(all_warnings) > 0
        }
