import os
import sys
import uuid
import aiofiles
import json
import numpy as np
import importlib.util
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.models.drawing import Drawing
from app.utils.file_identifier import identify_file_type, is_allowed_file
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_pipeline import run_layer2_pipeline
from app.ai.layer3_pipeline import run_layer3_pipeline
from app.ai.layer4_pipeline import run_layer4_pipeline
from app.ai.layer5_pipeline import run_layer5_pipeline
from app.ai.layer_precision import run_layer6_pipeline

# Add layer 7-10 paths to sys.path
layer7_path = os.path.join(os.path.dirname(__file__), '..', '..', 'layer7_cost')
layer8_path = os.path.join(os.path.dirname(__file__), '..', '..', 'layer8_supplier')
layer9_path = os.path.join(os.path.dirname(__file__), '..', '..', 'layer9_procurement')
layer10_path = os.path.join(os.path.dirname(__file__), '..', '..', 'layer10_scheduler')

# Import layer 7-10 functions with specific imports to avoid conflicts
align_cost = None
QTORequest = None
run_supplier_discovery = None
generate_rfq_payload = None
create_tasks_from_layer8 = None
assign_dependencies = None
calculate_schedule = None
calculate_late_times = None
analyze_schedule = None
load_productivity_library = None

try:
    # Import Layer 7 functions (Cost & Risk Engine)
    sys.path.insert(0, layer7_path)
    from api import align_cost as _align_cost, QTORequest as _QTORequest
    align_cost = _align_cost
    QTORequest = _QTORequest
    sys.path.remove(layer7_path)
except ImportError as e:
    print(f"Warning: Could not import Layer 7 functions: {e}")

try:
    # Import Layer 8 functions (Supplier Discovery)
    sys.path.insert(0, layer8_path)
    spec = importlib.util.spec_from_file_location("layer8_main", os.path.join(layer8_path, "main.py"))
    layer8_main = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layer8_main)
    run_supplier_discovery = layer8_main.run_supplier_discovery
    sys.path.remove(layer8_path)
except Exception as e:
    print(f"Warning: Could not import Layer 8 functions: {e}")

try:
    # Import Layer 9 functions (Procurement)
    sys.path.insert(0, layer9_path)
    from rfq_generator import generate_rfq_payload as _generate_rfq_payload
    generate_rfq_payload = _generate_rfq_payload
    sys.path.remove(layer9_path)
except ImportError as e:
    print(f"Warning: Could not import Layer 9 functions: {e}")

try:
    # Import Layer 10 functions (Scheduling) using importlib to avoid conflicts
    sys.path.insert(0, layer10_path)
    
    # Load productivity_library
    spec = importlib.util.spec_from_file_location("layer10_productivity", os.path.join(layer10_path, "productivity_library.py"))
    productivity_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(productivity_mod)
    load_productivity_library = productivity_mod.load_productivity_library
    
    # Load task_generator
    spec = importlib.util.spec_from_file_location("layer10_task_gen", os.path.join(layer10_path, "task_generator.py"))
    task_gen_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(task_gen_mod)
    create_tasks_from_layer8 = task_gen_mod.create_tasks_from_layer8
    
    # Load dependency_engine
    spec = importlib.util.spec_from_file_location("layer10_dep", os.path.join(layer10_path, "dependency_engine.py"))
    dep_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dep_mod)
    assign_dependencies = dep_mod.assign_dependencies
    
    # Load cpm_engine
    spec = importlib.util.spec_from_file_location("layer10_cpm", os.path.join(layer10_path, "cpm_engine.py"))
    cpm_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cpm_mod)
    calculate_schedule = cpm_mod.calculate_schedule
    calculate_late_times = cpm_mod.calculate_late_times
    
    # Load critical_path
    spec = importlib.util.spec_from_file_location("layer10_critical", os.path.join(layer10_path, "critical_path.py"))
    critical_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(critical_mod)
    analyze_schedule = critical_mod.analyze_schedule
    
    sys.path.remove(layer10_path)
except Exception as e:
    print(f"Warning: Could not import Layer 10 functions: {e}")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))  # 50MB

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for MongoDB serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    return obj

async def save_upload_file(upload_file: UploadFile) -> Drawing:
    """Save uploaded file and create database record"""
    
    # Validate file extension
    if not is_allowed_file(upload_file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Generate unique filename
    file_ext = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_size = 0
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await upload_file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(status_code=413, detail="File too large")
            await f.write(chunk)
    
    # Identify file type
    file_type = identify_file_type(file_path)
    
    # Create database record
    drawing = Drawing(
        filename=unique_filename,
        original_filename=upload_file.filename,
        file_type=file_type,
        file_size=file_size,
        file_path=file_path,
        status="processing"
    )
    await drawing.insert()
    
    # Process with Layer 1 pipeline
    try:
        result = route_preprocessing(file_path, file_type)
        
        # Store Layer 1 results in database
        drawing.processed = True
        drawing.processed_at = datetime.utcnow()
        drawing.status = "processed"
        drawing.geometry = convert_numpy_types(result.get('geometry'))
        drawing.bounding_box = convert_numpy_types(result.get('bounding_box'))
        drawing.text = convert_numpy_types(result.get('text'))
        drawing.scale_candidates = convert_numpy_types(result.get('scale_candidates', []))
        drawing.units = convert_numpy_types(result.get('units'))
        drawing.layers = convert_numpy_types(result.get('layers'))
        drawing.blocks = convert_numpy_types(result.get('blocks'))
        drawing.pipeline_type = result.get('pipeline_type')
        drawing.entity_count = convert_numpy_types(result.get('entity_count'))
        drawing.intermediate_json = result.get('intermediate_json')
        
        # Run Layer 2 pipeline if vector
        if result.get('pipeline_type') == 'vector':
            try:
                layer2_result = run_layer2_pipeline(result)
                drawing.layer2_processed = True
                drawing.layer2_data = convert_numpy_types(layer2_result)
                
                # Run Layer 3 pipeline if Layer 2 succeeded
                if layer2_result.get('status') == 'success':
                    try:
                        layer3_result = run_layer3_pipeline(result, layer2_result)
                        drawing.layer3_processed = True
                        drawing.layer3_data = convert_numpy_types(layer3_result)
                        
                        # Run Layer 4 pipeline if Layer 3 succeeded
                        if not layer3_result.get('error'):
                            try:
                                layer4_result = run_layer4_pipeline(layer3_result)
                                drawing.layer4_processed = True
                                drawing.layer4_data = convert_numpy_types(layer4_result)
                                
                                # Run Layer 5 pipeline if Layer 4 succeeded
                                if layer4_result.get('success'):
                                    try:
                                        layer5_result = run_layer5_pipeline(result, layer2_result, layer3_result, layer4_result)
                                        drawing.layer5_processed = True
                                        drawing.layer5_data = convert_numpy_types(layer5_result)
                                        
                                        # Run Layer 6 pipeline if Layer 5 succeeded
                                        if layer5_result.get('success'):
                                            try:
                                                layer6_result = run_layer6_pipeline(layer4_result, layer3_result)
                                                drawing.layer6_processed = True
                                                drawing.layer6_data = convert_numpy_types(layer6_result)
                                                
                                                # Run Layer 7 pipeline if Layer 6 succeeded (Cost & Risk Engine)
                                                if layer6_result.get('success') and align_cost and QTORequest:
                                                    try:
                                                        layer7_results = []
                                                        # Process each QTO item from Layer 5
                                                        if layer5_result.get('qto_items'):
                                                            print(f"Processing {len(layer5_result['qto_items'])} QTO items for Layer 7")
                                                            for item in layer5_result['qto_items']:
                                                                print(f"Layer 7 processing item: {item.get('description', '')}")
                                                                request = QTORequest(
                                                                    description=item.get('description', ''),
                                                                    unit=item.get('unit', ''),
                                                                    quantity=item.get('quantity', 1.0),
                                                                    top_k=3
                                                                )
                                                                cost_result = align_cost(request)
                                                                print(f"Layer 7 result: {cost_result}")
                                                                layer7_results.append(cost_result)
                                                        else:
                                                            print("No QTO items found in Layer 5 result for Layer 7 processing")
                                                        
                                                        print(f"Layer 7 completed with {len(layer7_results)} results")
                                                        drawing.layer7_processed = True
                                                        drawing.layer7_data = convert_numpy_types({'results': layer7_results})
                                                        
                                                        # Run Layer 8 pipeline if Layer 7 succeeded (Supplier Discovery)
                                                        if layer7_results and run_supplier_discovery:
                                                            try:
                                                                layer8_results = []
                                                                for cost_item in layer7_results:
                                                                    if cost_item.get('best_match'):
                                                                        # Extract material info from description
                                                                        desc = cost_item['query']['description'].lower()
                                                                        material = 'steel' if 'steel' in desc else 'concrete' if 'concrete' in desc else 'cement'
                                                                        
                                                                        supplier_result = run_supplier_discovery(
                                                                            material=material,
                                                                            grade='',
                                                                            unit=cost_item['query']['unit'],
                                                                            max_distance_km=30
                                                                        )
                                                                        layer8_results.append(supplier_result)
                                                                
                                                                drawing.layer8_processed = True
                                                                drawing.layer8_data = convert_numpy_types({'results': layer8_results})
                                                                
                                                                # Run Layer 9 pipeline if Layer 8 succeeded (Procurement)
                                                                if layer8_results and generate_rfq_payload:
                                                                    try:
                                                                        layer9_results = []
                                                                        for idx, supplier_item in enumerate(layer8_results):
                                                                            if supplier_item.get('recommended_supplier') and idx < len(layer7_results):
                                                                                cost_item = layer7_results[idx]
                                                                                rfq = generate_rfq_payload(
                                                                                    supplier_name=supplier_item['recommended_supplier'],
                                                                                    supplier_id=supplier_item.get('recommended_supplier_id', 0),
                                                                                    supplier_location=supplier_item.get('comparison', [{}])[0].get('location', ''),
                                                                                    material=cost_item['query']['description'],
                                                                                    quantity=cost_item['query']['quantity'],
                                                                                    unit=cost_item['query']['unit'],
                                                                                    project_name='Project',
                                                                                    expected_rate=supplier_item.get('best_rate', 0),
                                                                                    distance_km=supplier_item.get('best_distance', 0),
                                                                                    lead_time_days=supplier_item.get('best_lead_time', 0)
                                                                                )
                                                                                layer9_results.append(rfq)
                                                                        
                                                                        drawing.layer9_processed = True
                                                                        drawing.layer9_data = convert_numpy_types({'results': layer9_results})
                                                                        
                                                                        # Run Layer 10 pipeline if Layer 9 succeeded (Scheduling)
                                                                        if layer9_results and create_tasks_from_layer8:
                                                                            try:
                                                                                # Prepare Layer 7 output format for Layer 10
                                                                                layer7_for_layer10 = []
                                                                                for cost_item in layer7_results:
                                                                                    if cost_item.get('best_match'):
                                                                                        layer7_for_layer10.append({
                                                                                            'description': cost_item['best_match']['description'],
                                                                                            'quantity': cost_item['query']['quantity'],
                                                                                            'unit': cost_item['query']['unit']
                                                                                        })
                                                                                
                                                                                # Load productivity library and create tasks
                                                                                library = load_productivity_library()
                                                                                crews_config = {}  # Default crews
                                                                                
                                                                                tasks = create_tasks_from_layer8(layer7_for_layer10, library, crews_config)
                                                                                tasks = assign_dependencies(tasks)
                                                                                tasks = calculate_schedule(tasks)
                                                                                tasks = calculate_late_times(tasks)
                                                                                
                                                                                schedule_analysis = analyze_schedule(tasks)
                                                                                
                                                                                drawing.layer10_processed = True
                                                                                drawing.layer10_data = convert_numpy_types(schedule_analysis)
                                                                            except Exception as e:
                                                                                print(f"Layer 10 processing failed: {e}")
                                                                                drawing.layer10_processed = False
                                                                    except Exception as e:
                                                                        print(f"Layer 9 processing failed: {e}")
                                                                        drawing.layer9_processed = False
                                                            except Exception as e:
                                                                print(f"Layer 8 processing failed: {e}")
                                                                drawing.layer8_processed = False
                                                    except Exception as e:
                                                        print(f"Layer 7 processing failed: {e}")
                                                        drawing.layer7_processed = False
                                            except Exception as e:
                                                print(f"Layer 6 processing failed: {e}")
                                                drawing.layer6_processed = False
                                    except Exception as e:
                                        print(f"Layer 5 processing failed: {e}")
                                        drawing.layer5_processed = False
                            except Exception as e:
                                print(f"Layer 4 processing failed: {e}")
                                drawing.layer4_processed = False
                    except Exception as e:
                        print(f"Layer 3 processing failed: {e}")
                        drawing.layer3_processed = False
            except Exception as e:
                print(f"Layer 2 processing failed: {e}")
                drawing.layer2_processed = False
        
        await drawing.save()
        
    except Exception as e:
        # Store error but don't fail upload
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Processing error: {error_detail}")
        drawing.processed = False
        drawing.processing_error = str(e)
        drawing.status = "error"
        await drawing.save()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    return drawing
