import subprocess
import os
from pathlib import Path

ODA_CONVERTER_PATH = r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe"

def convert_dwg_to_dxf(dwg_path: str) -> str:
    """Convert DWG to DXF using ODAFileConverter"""
    
    if not os.path.exists(ODA_CONVERTER_PATH):
        raise FileNotFoundError("ODAFileConverter not found")
    
    dwg_file = Path(dwg_path)
    output_dir = dwg_file.parent / "converted"
    output_dir.mkdir(exist_ok=True)
    
    # ODAFileConverter syntax: input_folder output_folder output_version file_type recurse audit
    cmd = [
        ODA_CONVERTER_PATH,
        str(dwg_file.parent),
        str(output_dir),
        "ACAD2018",
        "DXF",
        "0",
        "1"
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    dxf_path = output_dir / f"{dwg_file.stem}.dxf"
    if not dxf_path.exists():
        raise FileNotFoundError(f"Conversion failed: {dxf_path}")
    
    return str(dxf_path)
