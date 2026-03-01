import cv2
import numpy as np
import fitz
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Configurable parameters
CONFIG = {
    'pdf_dpi': 300,
    'bilateral_d': 9,
    'bilateral_sigma_color': 75,
    'bilateral_sigma_space': 75,
    'adaptive_block_size': 11,
    'adaptive_c': 2,
    'morph_kernel_size': (2, 2),
    'min_component_area': 50,
    'enable_deskew': True
}

def pdf_to_image(file_path: str, dpi: int = 300) -> np.ndarray:
    """STEP 1: Convert PDF to image at specified DPI"""
    doc = fitz.open(file_path)
    page = doc[0]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    doc.close()
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img

def to_grayscale(image: np.ndarray) -> np.ndarray:
    """STEP 2: Convert to grayscale"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    return gray.astype(np.uint8)

def remove_noise(gray: np.ndarray, d: int = 9, sigma_color: int = 75, sigma_space: int = 75) -> np.ndarray:
    """STEP 3: Noise removal with bilateral filter"""
    return cv2.bilateralFilter(gray, d, sigma_color, sigma_space)

def adaptive_threshold(gray: np.ndarray, block_size: int = 11, c: int = 2) -> np.ndarray:
    """STEP 4: Adaptive thresholding"""
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, block_size, c
    )

def detect_skew_angle(binary: np.ndarray) -> float:
    """STEP 5: Detect skew angle using Hough Transform"""
    edges = cv2.Canny(binary, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=200)
    
    if lines is None:
        return 0.0
    
    angles = []
    for rho, theta in lines[:, 0]:
        angle = np.degrees(theta) - 90
        if -45 < angle < 45:
            angles.append(angle)
    
    return np.median(angles) if angles else 0.0

def deskew_image(image: np.ndarray, angle: float) -> np.ndarray:
    """STEP 5: Rotate image to correct skew"""
    if abs(angle) < 0.5:
        return image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def morphological_cleanup(binary: np.ndarray, kernel_size: Tuple[int, int] = (2, 2)) -> np.ndarray:
    """STEP 6: Morphological closing to connect lines"""
    kernel = np.ones(kernel_size, np.uint8)
    return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

def remove_small_components(binary: np.ndarray, min_area: int = 50) -> np.ndarray:
    """STEP 7: Remove small noise components"""
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    cleaned = np.zeros_like(binary)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            cleaned[labels == i] = 255
    return cleaned

def detect_scale(binary: np.ndarray) -> Optional[float]:
    """STEP 8: Detect scale factor (placeholder for OCR)"""
    return None

def preprocess_scanned_blueprint(file_path: str, config: Dict = None) -> Dict:
    """Main preprocessing pipeline for scanned blueprints"""
    cfg = {**CONFIG, **(config or {})}
    
    try:
        # Load image
        file_ext = Path(file_path).suffix.lower()
        if file_ext == '.pdf':
            image = pdf_to_image(file_path, cfg['pdf_dpi'])
        else:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Cannot load image: {file_path}")
        
        # STEP 2: Grayscale
        gray = to_grayscale(image)
        
        # STEP 3: Noise removal
        denoised = remove_noise(gray, cfg['bilateral_d'], cfg['bilateral_sigma_color'], cfg['bilateral_sigma_space'])
        
        # STEP 4: Adaptive thresholding
        binary = adaptive_threshold(denoised, cfg['adaptive_block_size'], cfg['adaptive_c'])
        
        # STEP 5: Deskew
        deskew_angle = 0.0
        if cfg['enable_deskew']:
            deskew_angle = detect_skew_angle(binary)
            binary = deskew_image(binary, deskew_angle)
        
        # STEP 6: Morphological cleanup
        binary = morphological_cleanup(binary, cfg['morph_kernel_size'])
        
        # STEP 7: Remove small components
        binary = remove_small_components(binary, cfg['min_component_area'])
        
        # STEP 8: Scale detection
        scale_factor = detect_scale(binary)
        
        # STEP 9: Return structured output
        return {
            'clean_image': denoised,
            'binary_image': binary,
            'deskew_angle': float(deskew_angle),
            'scale_factor': scale_factor
        }
    
    except Exception as e:
        raise ValueError(f"Preprocessing failed: {str(e)}")

def run_raster_pipeline(file_path: str) -> Dict:
    """Process raster images (PNG, JPG, JPEG, scanned PDF)"""
    
    # Run Layer 1 preprocessing
    preprocessed = preprocess_scanned_blueprint(file_path)
    binary = preprocessed['binary_image']
    
    (h, w) = binary.shape[:2]
    
    # Edge detection
    edges = cv2.Canny(binary, 50, 150)
    
    # Hough line detection
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    detected_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            detected_lines.append({
                'start': [int(x1), int(y1)],
                'end': [int(x2), int(y2)],
                'length': float(np.sqrt((x2-x1)**2 + (y2-y1)**2))
            })
    
    # Contour detection
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detected_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            detected_contours.append({
                'area': float(area),
                'perimeter': float(perimeter),
                'vertices': len(approx)
            })
    
    # OCR placeholder
    ocr_results = []
    
    return {
        'geometry': {
            'lines': detected_lines,
            'contours': detected_contours,
            'image_dimensions': {'width': w, 'height': h}
        },
        'parsed_text': ocr_results,
        'scale': {'scale_factor': preprocessed['scale_factor'], 'deskew_angle': preprocessed['deskew_angle']},
        'pipeline_type': 'raster',
        'preprocessed': preprocessed
    }

