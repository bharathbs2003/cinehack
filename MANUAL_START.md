# 🚀 Manual Start Guide - EduDub AI

## Quick Start (3 Simple Steps)

### Step 1: Start Backend

Open **PowerShell** or **Command Prompt** and run:

```powershell
cd D:\EduDubAI\backend
.\venv\Scripts\activate
python -m app.main_simple
```

**You should see:**
```
============================================
🚀 Starting EduDub AI - Local Version
============================================
📍 Backend API: http://0.0.0.0:8000
📖 API Docs: http://0.0.0.0:8000/docs
============================================
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this window open!**

---

### Step 2: Start Frontend

Open a **NEW** PowerShell/Command Prompt window and run:

```powershell
cd D:\EduDubAI\frontend
npm run dev
```

**You should see:**
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Leave this window open too!**

---

### Step 3: Open Browser

Open your browser and go to:

**http://localhost:5173**

---

## 🧪 Test the Application

### Test 1: Check Backend API
Open: http://localhost:8000

You should see:
```json
{
  "message": "EduDub AI - Local Version",
  "version": "2.0.0-local",
  "status": "ready"
}
```

### Test 2: Check API Documentation
Open: http://localhost:8000/docs

You'll see interactive API documentation (Swagger UI)

### Test 3: Verify API Keys
Open: http://localhost:8000/api/test

You should see all keys marked with ✅

### Test 4: Try the Frontend
1. Go to http://localhost:5173
2. Click "Get Started" or navigate to upload page
3. Upload a short video
4. Select target language
5. Click "Generate Dub"

---

## 🛑 Stop Services

Press `Ctrl+C` in both terminal windows to stop the services.

---

## ⚠️ Troubleshooting

### Problem: "Port already in use"

**Solution:**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
# Note the PID and run:
taskkill /PID <PID> /F

# Kill process on port 5173
netstat -ano | findstr :5173
# Note the PID and run:
taskkill /PID <PID> /F
```

### Problem: "Module not found"

**Solution:**
```powershell
cd D:\EduDubAI\backend
.\venv\Scripts\activate
pip install -r requirements_py313.txt
```

### Problem: "npm: command not found"

**Solution:**
Make sure Node.js is installed: https://nodejs.org/

---

## 📝 Summary

Your setup is complete:
- ✅ All dependencies installed
- ✅ API keys configured
- ✅ Backend ready
- ✅ Frontend ready

Just follow the 3 steps above to start using EduDub AI!

---

**Need help?** Check:
- `TEST_COMPLETE.md` for testing instructions
- `START_HERE.md` for overview
- `SETUP_GUIDE.md` for detailed documentation

