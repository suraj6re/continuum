# StructIQ - Full Stack Setup

## Backend Setup

### 1. Navigate to Backend
```bash
cd Backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure MongoDB
Edit `Backend/.env` and replace with your MongoDB URL:
```
MONGODB_URL=mongodb+srv://your-username:your-password@cluster.mongodb.net/structiq
```

### 4. Run Backend Server
```bash
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`

---

## Frontend Setup

### 1. Navigate to Frontend
```bash
cd Frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Run Frontend
```bash
npm start
```

Frontend runs at: `http://localhost:3000`

---

## Features Implemented

✅ **File Upload** - PDF, CAD, DWG, DXF, PNG, JPG
✅ **File Identification** - Automatic file type detection
✅ **MongoDB Storage** - File metadata stored in database
✅ **API Integration** - Frontend connected to backend
✅ **Error Handling** - Upload validation and error messages

---

## API Endpoints

### Upload Drawing
```
POST http://localhost:8000/api/upload/drawing
Content-Type: multipart/form-data
Body: file
```

### Get All Drawings
```
GET http://localhost:8000/api/upload/drawings
```

### Get Drawing by ID
```
GET http://localhost:8000/api/upload/drawing/{id}
```

---

## Database Structure

### Collection: drawings
```json
{
  "_id": "ObjectId",
  "filename": "uuid.pdf",
  "original_filename": "floor_plan.pdf",
  "file_type": "PDF",
  "file_size": 2048576,
  "file_path": "uploads/uuid.pdf",
  "status": "uploaded",
  "uploaded_at": "2024-01-15T10:30:00"
}
```

---

## Testing Upload

1. Start backend: `uvicorn main:app --reload --port 8000`
2. Start frontend: `npm start`
3. Login to app
4. Go to Upload Drawing page
5. Drag & drop or select a file
6. File uploads to backend and stores in MongoDB
7. View success message with file details
