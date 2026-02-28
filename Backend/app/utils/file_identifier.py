import magic
from pathlib import Path

ALLOWED_EXTENSIONS = {'.pdf', '.dwg', '.dxf', '.png', '.jpg', '.jpeg', '.cad'}

FILE_TYPE_MAP = {
    'application/pdf': 'PDF',
    'image/png': 'PNG',
    'image/jpeg': 'JPG',
    'image/vnd.dwg': 'DWG',
    'image/vnd.dxf': 'DXF',
}

def identify_file_type(file_path: str) -> str:
    """Identify file type using magic numbers"""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    
    # Check by extension if mime detection fails
    ext = Path(file_path).suffix.lower()
    if ext == '.dwg':
        return 'DWG'
    elif ext == '.dxf':
        return 'DXF'
    elif ext == '.cad':
        return 'CAD'
    
    return FILE_TYPE_MAP.get(mime_type, ext.upper().replace('.', ''))

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
