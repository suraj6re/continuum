# StructIQ Backend

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file and replace MongoDB URL:
```
MONGODB_URL=your-actual-mongodb-url
```

### 3. Run Server
```bash
uvicorn main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`

## API Endpoints

### Upload Drawing
```
POST /api/upload/drawing
Content-Type: multipart/form-data
Body: file (PDF, CAD, DWG, DXF, PNG, JPG)
```

### Get All Drawings
```
GET /api/upload/drawings
```

### Get Specific Drawing
```
GET /api/upload/drawing/{drawing_id}
```

## File Types Supported
- PDF
- CAD
- DWG
- DXF
- PNG
- JPG/JPEG

## Database Collections
- `drawings` - Uploaded file metadata
- `projects` - Project information
