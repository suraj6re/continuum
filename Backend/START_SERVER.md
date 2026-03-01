# How to Start the Backend Server

## Prerequisites

### 1. Install MongoDB

**Option A: MongoDB Community Server (Recommended)**
1. Download from: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB will run as a Windows service automatically

**Option B: MongoDB Compass (GUI + Server)**
1. Download from: https://www.mongodb.com/try/download/compass
2. Install and it includes MongoDB server

**Option C: Check if MongoDB is already installed:**
```powershell
mongod --version
```

### 2. Start MongoDB Service

**If installed as Windows Service:**
```powershell
# Check if running
Get-Service MongoDB

# Start if stopped
Start-Service MongoDB
```

**If not a service, start manually:**
```powershell
# Create data directory
mkdir C:\data\db

# Start MongoDB
mongod --dbpath C:\data\db
```

## Starting the Backend

### Step 1: Ensure MongoDB is Running

```powershell
# Test MongoDB connection
mongo --eval "db.version()"
```

Or check if port 27017 is listening:
```powershell
netstat -an | findstr "27017"
```

### Step 2: Start Backend Server

```powershell
cd Backend
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test the Server

Open browser: http://localhost:8000

Or use curl:
```powershell
curl http://localhost:8000
```

**Expected Response:**
```json
{"message": "StructIQ API is running"}
```

## Alternative: Run Without MongoDB (Development Mode)

If you don't want to install MongoDB right now, you can modify the code to skip database connection:

**Edit `Backend/main.py`:**

Comment out the database connection:
```python
# @app.on_event("startup")
# async def startup_event():
#     await connect_db()
#     upload_dir = os.getenv("UPLOAD_DIR", "../uploads")
#     if not os.path.exists(upload_dir):
#         os.makedirs(upload_dir)

# @app.on_event("shutdown")
# async def shutdown_event():
#     await close_db()
```

**Note:** Without MongoDB, file uploads won't be saved to database, but processing will still work.

## Troubleshooting

### Error: "Connection refused" or "MongoDB not found"

**Solution:** MongoDB is not running. Start it using one of the methods above.

### Error: "Port 8000 already in use"

**Solution:** Another process is using port 8000.

Find and kill it:
```powershell
# Find process using port 8000
netstat -ano | findstr ":8000"

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

Or change the port in `.env`:
```
API_PORT=8001
```

### Error: "Module not found"

**Solution:** Install dependencies:
```powershell
pip install -r requirements.txt
```

### Deprecation Warnings

The warnings about `on_event` are normal and don't affect functionality. They're just informing you about future FastAPI changes.

## Quick Start Commands

```powershell
# 1. Start MongoDB (if not running as service)
Start-Service MongoDB

# 2. Navigate to Backend
cd Backend

# 3. Start server
python main.py

# 4. In another terminal, test upload
curl -X POST http://localhost:8000/api/upload/drawing -F "file=@../imputs/1.dwg"
```

## API Documentation

Once server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Next Steps

1. ✅ Start MongoDB
2. ✅ Start Backend (`python main.py`)
3. ✅ Upload DWG file
4. ✅ Check results at `/api/upload/drawings`

---

**Need help?** Check the logs in the terminal where you ran `python main.py`
