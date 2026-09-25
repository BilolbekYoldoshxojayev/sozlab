# Workflow & Lifecycle Commands: Vazir Chat

## Build & Run Commands

### 1. One-Click Launch (Recommended for Demo)
```powershell
.\start_dev.ps1
```

### 2. Backend Only
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Only
```powershell
cd frontend
npm install
npm run dev
```

## Testing & Verification Commands

### 1. Backend Automated Tests
```powershell
python -m pytest backend/tests/test_backend.py -v
```

### 2. Frontend Production Build & Typecheck
```powershell
cd frontend
npm run build
```

## URLs
- **Web Application:** `http://localhost:3000`
- **Call Simulator:** `http://localhost:3000/call`
- **Operator Dashboard:** `http://localhost:3000/operator`
- **Analytics:** `http://localhost:3000/analytics`
- **Call Archive:** `http://localhost:3000/history`
- **FastAPI OpenAPI Swagger:** `http://localhost:8000/docs`
