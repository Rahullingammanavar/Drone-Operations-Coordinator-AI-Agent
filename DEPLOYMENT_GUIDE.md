# 🚀 Deployment Guide - Streamlit Cloud

## Quick Deployment Steps

### Step 1: Push Code to GitHub ✅
Your code is already on GitHub at:
https://github.com/Rahullingammanavar/Drone-Operations-Coordinator-AI-Agent

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click **"Sign in"** (use your GitHub account)

2. **Create New App**
   - Click **"New app"** button
   - Repository: `Rahullingammanavar/Drone-Operations-Coordinator-AI-Agent`
   - Branch: `main`
   - Main file path: `app.py`
   - Click **"Advanced settings..."** (IMPORTANT!)

3. **Add Secrets** (Click "Advanced settings")
   Paste this into the Secrets box:

```toml
GEMINI_API_KEY = "AIzaSyDSs77MOe-Rp0EY0r2qNrd_WqrI5JWfgUM"
GOOGLE_SHEETS_ID = "1jCsmXP4PUQqCLV_A1XXxixqNhb4d0VK5cJyNivNvqn8"
GOOGLE_SERVICE_ACCOUNT_FILE = "credentials.json"

[gcp_service_account]
type = "service_account"
project_id = "drone-operations-agent-487006"
private_key_id = "b33a90d388312e506446fa26c8b9738ada4cf040"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCq5Yhcc0izh+pM\nOcoG8ph/MC0hNze/GvLEwew5nZ60Ju7v2XW6wbxuBQnBTW+ufYQmLi1aIPqYU3F8\n+TOfENuqPaPcwLUby4cVETPfzkx742qUBKeF6GFBS+1NyalTdMUiZgMeyR81uhq1\nQfQOR+HKfEA6Yf1SYoaKoTeb4i22mIYFf1o3wmZKeFVk5AO50XB0JcoXxoVAOQSr\n9kOJtR4T/H5GTe0NW+Uv3Jztor1FcoiDMUHXTlAO5bL/7u7Jui36E3F2/x/bs5s3\nPs+3/JGAU05S+REY5XHpi5Kw2k1+KBfu4M9R2y74qKIgb7NqtQ++GuUD6JN495rV\n5riOesCpAgMBAAECggEAAWtC0hhc9VdUETT2TKTNXQT+jZo38BzJAOw79LsuewAg\nbMUT+VcsJDJjgy427APRH0Cz513YZtUOigNHCUjqYgP9V9MRIz1x44a537UGpTgI\nBa7yNdDuTyH9GEUWjwGsX12Ueg12dmDottzo1LOGbZgm2l/qQA8JtJ35ExDHi2QT\nrX2s1sBUSKKeBQDdS2k8NBGN8Sk+qNDND6fh1Eq6HumdRPFOrhcWdyN+AEuBZ/EG\nz4Bj2fv3Nt6T6sm/rdz8fWI7BL2AdpyFYwkBEKXX4Ln/18lszCm6YsKBavUwF0dq\n2cT4CS6OBY8nNxGd3CG+1g+84XtXTnJ0Z+T6gnhYOQKBgQDaAmeOHL9BF94gVIbJ\nzKKYXvqYURBDvgrNjm+zvrMkJ2VTBJWpaLyQXkqU4ZF2CbSqHjVk1sQy/toiTbFu\n3OK7WpbD0pOC2WUfi3bEhhLKYeZzxixcrTDqlbdzAXBJQ0hY/ovN6Fadso/0Rc8p\nHKx1JSBgfXRc+om0voL8l0kEhQKBgQDIrWJxWCtaD5nSIrAKhGqxhSuAya6T9vKa\n8r3sn7NL32LJJHASX394x43jc+At2rR/giKqaPxWiM/XP1+zYthhHvO/JA7XDjta\nPjgefXZts50etUnhsuMUY1NzwVHYGiyaPBR9TaP90HtD0jz/F+IK46p9rcna22A/\nJ5iMKUlm1QKBgD0MT1NMWYIw3NLQ2K3Jz/47GpFsodFWdk/5gu4iiKenIIiO0BoQ\naj1DKj9mqwUS0rSQoQML4QUmuI7Ckt0onZU5WN6dKRGLLvYWZ7vAj6J8p7vj0qhh\nF0GZizV5QahCXxAMt7mBRkACsK0Gn2wzy1dCfj6G4v7maYljj+qLsrbBAoGBAKl6\nZM08nUAuNMZXLT10n3bU9OyLZ7jmsfVSVDvmk9HcEt20vEGIDWu/fIE/d3DCZ/XX\nvdcVWybp3D3486XYMM21Cj2/Ahl1l4KbUWHOq5nyOxuYF5FZNpYdXHlCJxDO6iRH\n4TYBwCG3VKLuhz0Yunpf07jYcMU4yIwNsLOOmsMRAoGAb37QHmAa+D1HBKb5a8nw\n1p4FZUQZnPqUyOBQJK56LSDkCyijb7Xp1kfAh0wtyZeMviFyMdt30frJK3Q3NFyv\nmKLIgO9sp2aLOWWcANWRLmPSPS1z+llocOna5HohDKasZmYZrR51rWdCiDzhBxr5\nTPYeppiLLcPp4NzCrwC3FnE=\n-----END PRIVATE KEY-----\n"
client_email = "drone-ops-agent@drone-operations-agent-487006.iam.gserviceaccount.com"
client_id = "113021234236475786822"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/drone-ops-agent%40drone-operations-agent-487006.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

4. **Deploy!**
   - Click **"Deploy!"**
   - Wait 2-3 minutes for deployment
   - You'll get a public URL like: `https://your-app-name.streamlit.app`

### Step 3: Test the Deployment

Once deployed, try these queries:
- ✅ "Show available pilots in Bangalore"
- ✅ "Which drones can handle thermal imaging?"
- ✅ "Suggest assignment for PRJ002"
- ✅ "Check all conflicts"

---

## Alternative: Deploy to Replit (Backup Option)

If Streamlit Cloud has issues:

1. Go to https://replit.com
2. Click "Create Repl"
3. Import from GitHub: `Rahullingammanavar/Drone-Operations-Coordinator-AI-Agent`
4. Add Secrets in Replit (same as above)
5. Click "Run"

---

## Troubleshooting

### Issue: "No module named streamlit"
- Replit/Streamlit Cloud will auto-install from `requirements.txt`
- Wait for installation to complete

### Issue: "Google Sheets connection failed"
- Check that secrets are pasted correctly in Streamlit Cloud
- Verify the Google Sheet is shared with service account

### Issue: "Gemini API error"
- Verify API key in secrets
- Check quota at https://aistudio.google.com

---

## 🎯 Final Checklist

- [x] Code pushed to GitHub
- [ ] Deployed to Streamlit Cloud
- [ ] Public URL obtained
- [ ] App tested with sample queries
- [ ] URL shared with evaluator

---

**Deployment Time: ~5 minutes**  
**Public URL Format**: `https://drone-ops-coordinator-XXXXX.streamlit.app`
