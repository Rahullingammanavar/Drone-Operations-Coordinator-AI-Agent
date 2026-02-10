# Decision Log - Drone Operations Coordinator AI Agent

**Author:** Rahul K Lingammanava  
**Date:** February 10, 2026  
**Assignment:** Skylark Drones Technical Assessment

---

## 1. Key Assumptions Made

### Data Assumptions
- **CSV Structure Completeness**: Assumed the provided 3 CSV files (pilot_roster, drone_fleet, missions) represent the complete data schema required for the assignment.
- **Date Format**: All dates follow ISO format (YYYY-MM-DD) for consistency and easy parsing.
- **Pilot Skills Format**: Skills and certifications are comma-separated within quoted strings, requiring proper parsing.
- **Status Values**: Pilot status limited to `Available`, `Assigned`, `On Leave`; Drone status limited to `Available`, `Maintenance`, `Assigned`.

### Business Logic Assumptions
- **Location Matching**: Exact string match required for location-based assignments (Bangalore vs Mumbai). No fuzzy matching or nearby location logic.
- **Assignment Priority**: When multiple conflicts exist, the system flags all of them rather than auto-resolving.
- **Maintenance Window**: Drones in maintenance are completely unavailable regardless of maintenance_due date.
- **Pilot Availability**: Pilots marked "On Leave" cannot be assigned even for urgent requests until their `available_from` date.

### "Urgent Reassignments" Interpretation
I interpreted "urgent reassignments" as:
1. **Quick Conflict Resolution**: When a project is marked "Urgent" priority, the agent proactively suggests available pilot-drone pairs that meet requirements.
2. **Backup Recommendations**: If the ideal match is unavailable, suggest next-best alternatives with clear trade-offs (e.g., missing Night Ops certification but available).
3. **Override Warnings**: For truly urgent cases, allow assignments with location mismatches but clearly flag the logistics challenge.

**Why this interpretation?** Real-world operations often require balancing ideal vs. feasible solutions under time pressure. The agent acts as a decision support tool, not a rigid blocker.

---

## 2. Trade-offs and Technical Decisions

### Technology Stack

| Choice | Rationale | Trade-off |
|--------|-----------|-----------|
| **LangChain + Gemini** | Fast conversational setup, good reasoning capabilities | Could use custom prompt engineering for more control |
| **Flask over FastAPI** | Simpler for quick deployment, familiar to most developers | Less async performance than FastAPI |
| **Google Sheets as DB** | Required by assignment; 2-way sync built-in | Not scalable for production; API rate limits |
| **gspread library** | Official Python library, reliable authentication | Some operations slower than direct API calls |

### Architecture Decisions

**1. Conflict Detection as Separate Module**
- **Decision**: Created `conflict_detector.py` as standalone module
- **Why**: Conflicts involve complex cross-referencing (pilots + drones + missions). Separating logic improves testability and maintainability.
- **Trade-off**: Slightly more code, but much easier to extend with new conflict types.

**2. Agent Tool Structure**
- **Decision**: Implemented 8 specialized tools for the agent:
  - `query_pilots`, `query_drones`, `query_missions`
  - `assign_pilot_to_project`, `update_pilot_status`
  - `check_conflicts`, `suggest_assignments`, `urgent_reassign`
- **Why**: Clear tool boundaries help Gemini understand capabilities and reduce hallucination.
- **Trade-off**: More boilerplate code vs. fewer but more complex tools.

**3. Synchronous Sheets Updates**
- **Decision**: Write operations to Google Sheets happen immediately (not batched)
- **Why**: Ensures data consistency and meets "2-way sync" requirement
- **Trade-off**: Slower if many updates needed, but acceptable for assignment scope (4 pilots, 4 drones)

**4. Frontend: Simple Chat UI vs. Dashboard**
- **Decision**: Built minimal chat interface (HTML/CSS/JS) instead of rich dashboard with charts
- **Why**: 5-hour time constraint; conversational interface is core requirement
- **Trade-off**: Less visual context, but faster development and meets spec

---

## 3. What I'd Do Differently With More Time

### Technical Improvements

**1. Database Layer (2-3 hours)**
- Add SQLite or PostgreSQL as caching layer
- Sync Google Sheets → DB on startup, DB → Sheets on updates
- **Benefit**: Faster queries, offline capability, complex joins

**2. Advanced Conflict Detection (1-2 hours)**
- Graph-based conflict visualization (which pilot blocks which drone on which dates)
- Conflict severity scoring (location mismatch vs. certification gap)
- Auto-suggest conflict resolution steps
- **Benefit**: More actionable insights for complex scenarios

**3. Robust Error Handling (1 hour)**
- Implement retry logic for Google Sheets API failures
- Handle malformed user queries more gracefully
- Add input validation for date ranges, pilot IDs, etc.
- **Benefit**: Production-ready reliability

**4. Testing Suite (2 hours)**
- Unit tests for conflict detection logic
- Integration tests for Sheets sync
- Mock data for edge cases
- **Benefit**: Confidence in edge case handling

**5. Enhanced UI (2 hours)**
- Add visual timeline of assignments
- Display pilot/drone cards with status badges
- Interactive conflict resolution wizard
- **Benefit**: Better user experience for non-technical coordinators

### Business Logic Enhancements

**1. Smart Assignment Scoring**
- Rank pilot-drone pairs by: skill exact match > location match > availability buffer
- Show "confidence score" for each suggested assignment
- **Benefit**: Data-driven decision making

**2. Predictive Maintenance**
- Flag drones approaching maintenance_due dates during assignment
- Suggest alternative drones if maintenance overlaps with project end_date
- **Benefit**: Proactive planning, reduced project disruptions

**3. Multi-Project Optimization**
- Batch assign across all pending projects to minimize total conflicts
- Suggest optimal pilot-project pairings considering entire portfolio
- **Benefit**: Global optimization vs. greedy one-by-one assignment

---

## 4. Edge Cases Handled

✅ **Double-Booking Detection**: Checks if pilot's `available_from` date overlaps with new assignment  
✅ **Certification Mismatch**: Validates pilot certifications against project `required_certs`  
✅ **Maintenance Conflict**: Blocks assignment of drones with `status='Maintenance'`  
✅ **Location Mismatch**: Flags when pilot and project locations differ  
✅ **Skill Gap Detection**: Warns if pilot's skills don't fully cover `required_skills`  
✅ **Drone-Location Mismatch**: Checks if assigned drone is in same city as project  

---

## 5. Deployment Strategy

**Platform**: Replit (chosen over Vercel)  
**Why Replit**:
- Zero-config Python environment
- Built-in secrets management for API keys
- Instant public URL
- No build step required

**Environment Variables Required**:
- `GEMINI_API_KEY`: Google Gemini API key
- `GOOGLE_SHEETS_ID`: Spreadsheet ID for data source
- `GOOGLE_SERVICE_ACCOUNT`: JSON credentials for Sheets API

**Deployment Steps**:
1. Upload code to Replit
2. Add secrets via Replit UI
3. Run `pip install -r requirements.txt`
4. Execute `python app.py`
5. Share public URL

---

## 6. Limitations & Future Work

### Current Limitations
- **No Authentication**: Anyone with link can access (acceptable for demo)
- **No Audit Log**: Can't track who made which assignment changes
- **Single-User**: No concurrent user support (Sheets as DB limitation)
- **Limited Scale**: Performance degrades beyond ~50 pilots/drones
- **No Notifications**: Doesn't alert stakeholders of assignments

### Recommended Next Steps for Production
1. Add user authentication (OAuth)
2. Migrate to proper database (PostgreSQL)
3. Implement role-based access control
4. Add email/SMS notifications for assignments
5. Create mobile app for field pilots
6. Integrate with drone telemetry for real-time status

---

**Total Development Time**: 4.5 hours  
**Lines of Code**: ~800  
**External APIs**: 2 (Google Sheets, Gemini)  
**Edge Cases Handled**: 6  

**Final Note**: This agent demonstrates core capabilities required for drone operations coordination. With more time, the focus would shift to UI/UX polish, advanced optimization algorithms, and production hardening.
