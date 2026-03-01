from rfq_generator import generate_rfq, generate_rfq_payload
from whatsapp_template import generate_whatsapp, generate_whatsapp_payload
from communication_logger import log_communication, get_logs, get_log_summary
import json

def test_basic_rfq():
    """Test basic RFQ generation"""
    print("=" * 80)
    print("TEST 1: Basic RFQ Generation")
    print("=" * 80)
    
    rfq = generate_rfq(
        supplier_name="Iron Works",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        project_name="Residential Tower A"
    )
    
    print(rfq)
    print("\n[OK] Test 1 Complete\n")


def test_enhanced_rfq():
    """Test RFQ with all optional parameters"""
    print("=" * 80)
    print("TEST 2: Enhanced RFQ with Optional Parameters")
    print("=" * 80)
    
    rfq = generate_rfq(
        supplier_name="Iron Works",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        project_name="Residential Tower A",
        delivery_date="15-02-2025",
        supplier_location="Nagpur",
        expected_rate=64.0
    )
    
    print(rfq)
    print("\n[OK] Test 2 Complete\n")


def test_structured_payload():
    """Test structured JSON payload generation"""
    print("=" * 80)
    print("TEST 3: Structured JSON Payload")
    print("=" * 80)
    
    payload = generate_rfq_payload(
        supplier_name="Iron Works",
        supplier_id=8,
        supplier_location="Nagpur",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        project_name="Residential Tower A",
        delivery_date="15-02-2025",
        expected_rate=64.0,
        distance_km=8,
        lead_time_days=1
    )
    
    print(json.dumps(payload, indent=2))
    print("\n[OK] Test 3 Complete\n")


def test_layer8_layer9_integration():
    """Test integration with Layer 8 and Layer 9 outputs"""
    print("=" * 80)
    print("TEST 4: Layer 8 + Layer 9 Integration")
    print("=" * 80)
    
    # Simulated Layer 8 output
    layer8_output = {
        "description": "Steel reinforcement Fe500 bars",
        "quantity": 2500,
        "unit": "kg"
    }
    
    # Simulated Layer 9 output
    layer9_output = {
        "recommended_supplier": "Iron Works",
        "recommended_supplier_id": 8,
        "best_rate": 64.0,
        "best_distance": 8,
        "best_lead_time": 1,
        "comparison": [
            {
                "supplier_name": "Iron Works",
                "location": "nagpur"
            }
        ]
    }
    
    # Generate RFQ from combined data
    payload = generate_rfq_payload(
        supplier_name=layer9_output["recommended_supplier"],
        supplier_id=layer9_output["recommended_supplier_id"],
        supplier_location=layer9_output["comparison"][0]["location"],
        material=layer8_output["description"],
        quantity=layer8_output["quantity"],
        unit=layer8_output["unit"],
        project_name="Residential Tower A",
        expected_rate=layer9_output["best_rate"],
        distance_km=layer9_output["best_distance"],
        lead_time_days=layer9_output["best_lead_time"]
    )
    
    print("Layer 8 Input:")
    print(json.dumps(layer8_output, indent=2))
    
    print("\nLayer 9 Input:")
    print(json.dumps({
        "recommended_supplier": layer9_output["recommended_supplier"],
        "best_rate": layer9_output["best_rate"],
        "best_distance": layer9_output["best_distance"]
    }, indent=2))
    
    print("\nGenerated RFQ:")
    print(payload["rfq_text"])
    
    print("\n[OK] Test 4 Complete\n")


def test_concrete_rfq():
    """Test RFQ for concrete material"""
    print("=" * 80)
    print("TEST 5: Concrete M25 RFQ")
    print("=" * 80)
    
    rfq = generate_rfq(
        supplier_name="Concrete Plus",
        material="Reinforced Cement Concrete M25",
        quantity=50,
        unit="m3",
        project_name="Commercial Complex B",
        delivery_date="20-02-2025",
        supplier_location="Nagpur",
        expected_rate=7150.0
    )
    
    print(rfq)
    print("\n[OK] Test 5 Complete\n")


def test_whatsapp_basic():
    """Test basic WhatsApp message generation"""
    print("=" * 80)
    print("TEST 6: WhatsApp Message Generation")
    print("=" * 80)
    
    message = generate_whatsapp(
        supplier_name="Iron Works",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        project_name="Residential Tower A",
        expected_rate=64.0
    )
    
    print(message)
    print(f"\nCharacter count: {len(message)}")
    print("\n[OK] Test 6 Complete\n")


def test_whatsapp_payload():
    """Test WhatsApp structured payload"""
    print("=" * 80)
    print("TEST 7: WhatsApp Structured Payload")
    print("=" * 80)
    
    payload = generate_whatsapp_payload(
        supplier_name="Iron Works",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        project_name="Residential Tower A",
        expected_rate=64.0,
        supplier_phone="+91-9876543210"
    )
    
    print(json.dumps(payload, indent=2))
    print("\n[OK] Test 7 Complete\n")


def test_communication_logging():
    """Test communication logging"""
    print("=" * 80)
    print("TEST 8: Communication Logging")
    print("=" * 80)
    
    # Log RFQ
    log1 = log_communication(
        supplier="Iron Works",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        mode="RFQ",
        status="Drafted",
        project_name="Residential Tower A",
        expected_rate=64.0
    )
    print(f"Logged RFQ: {log1['log_id']}")
    
    # Log WhatsApp
    log2 = log_communication(
        supplier="Iron Works",
        material="Steel reinforcement Fe500 bars",
        quantity=2500,
        unit="kg",
        mode="WhatsApp",
        status="Drafted",
        project_name="Residential Tower A"
    )
    print(f"Logged WhatsApp: {log2['log_id']}")
    
    # Log Email
    log3 = log_communication(
        supplier="Concrete Plus",
        material="Reinforced Cement Concrete M25",
        quantity=50,
        unit="m3",
        mode="Email",
        status="Drafted",
        project_name="Commercial Complex B",
        expected_rate=7150.0
    )
    print(f"Logged Email: {log3['log_id']}")
    
    print("\n[OK] Test 8 Complete\n")


def test_log_retrieval():
    """Test log retrieval and filtering"""
    print("=" * 80)
    print("TEST 9: Log Retrieval & Filtering")
    print("=" * 80)
    
    # Get all logs
    all_logs = get_logs()
    print(f"Total logs: {len(all_logs)}")
    
    # Filter by supplier
    iron_logs = get_logs(supplier="Iron Works")
    print(f"Iron Works logs: {len(iron_logs)}")
    
    # Filter by mode
    whatsapp_logs = get_logs(mode="WhatsApp")
    print(f"WhatsApp logs: {len(whatsapp_logs)}")
    
    # Get summary
    summary = get_log_summary()
    print(f"\nLog Summary:")
    print(json.dumps(summary, indent=2))
    
    print("\n[OK] Test 9 Complete\n")


def test_complete_flow():
    """Test complete Layer 10 flow"""
    print("=" * 80)
    print("TEST 10: Complete Layer 10 Flow")
    print("=" * 80)
    
    # Simulated Layer 8 & 9 data
    layer8 = {
        "description": "Steel reinforcement Fe500 bars",
        "quantity": 2500,
        "unit": "kg"
    }
    
    layer9 = {
        "recommended_supplier": "Iron Works",
        "best_rate": 64.0
    }
    
    project = "Residential Tower A"
    
    print("Step 1: Generate RFQ")
    rfq = generate_rfq(
        supplier_name=layer9["recommended_supplier"],
        material=layer8["description"],
        quantity=layer8["quantity"],
        unit=layer8["unit"],
        project_name=project,
        expected_rate=layer9["best_rate"]
    )
    print("[OK] RFQ Generated")
    
    print("\nStep 2: Generate WhatsApp Message")
    whatsapp = generate_whatsapp(
        supplier_name=layer9["recommended_supplier"],
        material=layer8["description"],
        quantity=layer8["quantity"],
        unit=layer8["unit"],
        project_name=project,
        expected_rate=layer9["best_rate"]
    )
    print("[OK] WhatsApp Message Generated")
    
    print("\nStep 3: Log Communications")
    log_communication(
        supplier=layer9["recommended_supplier"],
        material=layer8["description"],
        quantity=layer8["quantity"],
        unit=layer8["unit"],
        mode="RFQ",
        status="Drafted",
        project_name=project,
        expected_rate=layer9["best_rate"]
    )
    log_communication(
        supplier=layer9["recommended_supplier"],
        material=layer8["description"],
        quantity=layer8["quantity"],
        unit=layer8["unit"],
        mode="WhatsApp",
        status="Drafted",
        project_name=project,
        expected_rate=layer9["best_rate"]
    )
    print("[OK] Communications Logged")
    
    print("\n[OK] Test 10 Complete\n")


def main():
    print("\n" + "=" * 80)
    print("LAYER 10 - PROCUREMENT AGENT (Steps 1, 2, 3)")
    print("=" * 80 + "\n")
    
    # Step 1 Tests
    print("STEP 1: RFQ Template Generator")
    print("-" * 80)
    test_basic_rfq()
    test_enhanced_rfq()
    test_structured_payload()
    test_layer8_layer9_integration()
    test_concrete_rfq()
    
    # Step 2 Tests
    print("\nSTEP 2: WhatsApp Draft Generator")
    print("-" * 80)
    test_whatsapp_basic()
    test_whatsapp_payload()
    
    # Step 3 Tests
    print("\nSTEP 3: Communication Logging")
    print("-" * 80)
    test_communication_logging()
    test_log_retrieval()
    
    # Complete Flow
    test_complete_flow()
    
    print("=" * 80)
    print("ALL TESTS COMPLETE - LAYER 10 READY (Steps 1, 2, 3)")
    print("=" * 80)


if __name__ == "__main__":
    main()
