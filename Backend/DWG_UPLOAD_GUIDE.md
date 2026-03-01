# DWG File Upload & Processing Guide

## ✅ Setup Complete

Your system is already configured to handle DWG files! Here's what's in place:

### Components:
1. **ODA File Converter** - Installed at: `C:\Program Files\ODA\ODAFileConverter 27.1.0\`
2. **DWG Converter** - `Backend/app/ai/dwg_converter.py`
3. **Upload Service** - Handles DWG files automatically
4. **Pipeline** - Converts DWG → DXF → Processing

## 🚀 How to Upload & Process DWG Files

### Method 1: Using Frontend (React)

1. **Start Backend:**
   ```bash
   cd Backend
   python main.py
   ```
   Backend runs on: `http://localhost:8000`

2. **Start Frontend:**
   ```bash
   cd Frontend
   npm start
   ```
   Frontend runs on: `http://localhost:3000`

3. **Upload DWG:**
   - Go to Upload page
   - Click "Choose File" or drag & drop
   - Select your `.dwg` file
   - Click "Upload"

### Method 2: Using API Directly (Postman/cURL)

**Upload DWG File:**
```bash
curl -X POST http://localhost:8000/api/upload/drawing \
  -F "file=@path/to/your/file.dwg"
```

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "id": "drawing_id_here",
    "filename": "unique_filename.dwg",
    "original_filename": "your_file.dwg",
    "file_type": "DWG",
    "file_size": 332456,
    "status": "processing",
    "uploaded_at": "2026-03-01T..."
  }
}
```

**Check Processing Status:**
```bash
curl http://localhost:8000/api/upload/drawing/{drawing_id}
```

**Get Layer 2 Results:**
```bash
curl http://localhost:8000/api/upload/drawing/{drawing_id}/layer2
```

### Method 3: Using Python Script

```python
import requests

# Upload DWG file
with open('path/to/your/file.dwg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/upload/drawing',
        files=files
    )
    
result = response.json()
print(f"Upload successful: {result['success']}")
print(f"Drawing ID: {result['data']['id']}")

# Get processing results
drawing_id = result['data']['id']
response = requests.get(f'http://localhost:8000/api/upload/drawing/{drawing_id}')
drawing_data = response.json()
print(f"Status: {drawing_data['data']['status']}")
print(f"Processed: {drawing_data['data']['processed']}")
```

## 📋 Processing Pipeline

When you upload a DWG file, here's what happens:

1. **Upload** → File saved to `uploads/` directory
2. **Validation** → Check file type and size
3. **Conversion** → DWG converted to DXF using ODA File Converter
4. **Layer 1** → Extract geometry, text, layers, blocks
5. **Layer 2** → Semantic analysis (title block, legend, schedule, boundaries)
6. **Layer 3** → Quantity takeoff (if Layer 2 succeeds)
7. **Storage** → Results saved to MongoDB

## 🔍 What Gets Extracted

### Layer 1 (Geometry):
- Lines, polylines, arcs, circles
- Text entities and positions
- Layers and blocks
- Bounding box
- Entity count
- Units and scale

### Layer 2 (Semantic):
- **Title Block** - Project info, drawing number, scale, date
- **Legend** - Symbol definitions
- **Schedule** - Tables and data
- **Boundaries** - Drawing regions
- **Text Clustering** - Grouped text elements

### Layer 3 (Quantities):
- Material quantities
- Dimensions
- Areas and volumes
- Cost estimates

## 📁 File Locations

**Uploaded Files:**
```
Backend/uploads/
└── {unique_id}.dwg
```

**Converted DXF:**
```
Backend/uploads/converted/
└── {filename}.dxf
```

**Intermediate JSON:**
```
Backend/uploads/
└── {filename}_normalized_drawing.json
```

## 🧪 Testing with Sample DWG

You already have a sample DWG file:
```
imputs/1.dwg
```

**Test it:**
```bash
cd Backend
python -c "
import requests

with open('../imputs/1.dwg', 'rb') as f:
    files = {'file': ('1.dwg', f, 'application/octet-stream')}
    response = requests.post('http://localhost:8000/api/upload/drawing', files=files)
    print(response.json())
"
```

## ⚙️ Configuration

**ODA Converter Path:**
Located in `Backend/app/ai/dwg_converter.py`:
```python
ODA_CONVERTER_PATH = r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe"
```

**Supported Formats:**
- Input: `.dwg` (all AutoCAD versions)
- Output: `.dxf` (ACAD2018 format)

**File Size Limit:**
- Default: 50 MB
- Configure in `.env`: `MAX_FILE_SIZE=52428800`

## 🐛 Troubleshooting

### Issue: "ODAFileConverter not found"
**Solution:** Verify installation path:
```bash
dir "C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe"
```

### Issue: "Conversion failed"
**Solution:** Check ODA converter logs and ensure DWG file is valid

### Issue: "File type not allowed"
**Solution:** Verify file has `.dwg` extension

### Issue: "File too large"
**Solution:** Increase `MAX_FILE_SIZE` in `.env` or compress DWG file

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/drawing` | Upload DWG/DXF/PDF file |
| GET | `/api/upload/drawings` | List all drawings |
| GET | `/api/upload/drawing/{id}` | Get drawing details |
| GET | `/api/upload/drawing/{id}/layer2` | Get Layer 2 results |
| GET | `/api/upload/drawing/{id}/layer3` | Get Layer 3 results |

## 🎯 Next Steps

1. **Start the backend server**
2. **Upload a DWG file** using any method above
3. **Check the results** via API or frontend
4. **Integrate with your workflow**

## 📝 Example Response

**Layer 2 Output:**
```json
{
  "success": true,
  "data": {
    "status": "success",
    "title_block": {
      "project_name": "RESIDENTIAL COMPLEX",
      "drawing_number": "A-101",
      "scale": "1:100",
      "date": "2024-01-15"
    },
    "legend": {
      "items": [
        {"symbol": "wall", "description": "Concrete Wall 300mm"},
        {"symbol": "door", "description": "Door Type A"}
      ]
    },
    "schedule": {
      "tables": [...]
    },
    "boundaries": {
      "regions": [...]
    }
  }
}
```

---

**Your system is ready to process DWG files!** 🎉

Just start the backend and upload your DWG files through the API or frontend.
