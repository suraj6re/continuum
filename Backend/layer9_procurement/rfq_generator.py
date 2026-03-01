from datetime import datetime

def generate_rfq(
    supplier_name,
    material,
    quantity,
    unit,
    project_name,
    delivery_date=None,
    supplier_location=None,
    expected_rate=None
):
    """
    Generate a formatted RFQ (Request for Quotation) text
    
    Args:
        supplier_name: Name of the supplier
        material: Material description
        quantity: Quantity required
        unit: Unit of measurement
        project_name: Project name
        delivery_date: Expected delivery date (optional)
        supplier_location: Supplier location (optional)
        expected_rate: Expected rate from Layer 9 (optional)
    
    Returns:
        Formatted RFQ text string
    """
    if delivery_date is None:
        delivery_date = "To be confirmed"
    
    today = datetime.today().strftime("%d-%m-%Y")
    
    rfq_text = f"""
----------------------------------------------------
REQUEST FOR QUOTATION (RFQ)
----------------------------------------------------

Date: {today}

To: {supplier_name}"""
    
    if supplier_location:
        rfq_text += f"\nLocation: {supplier_location}"
    
    rfq_text += f"""

Project: {project_name}

Material Details:
- Description : {material}
- Quantity    : {quantity} {unit}"""
    
    if expected_rate:
        rfq_text += f"\n- Reference Rate : Rs.{expected_rate}/{unit}"
    
    rfq_text += f"""

Requested Delivery Date: {delivery_date}

Kindly provide:
1. Best unit rate (Rs/{unit})
2. Availability confirmation
3. Expected dispatch timeline
4. Applicable taxes & transport charges

Regards,
Procurement Team
----------------------------------------------------
"""
    
    return rfq_text.strip()


def generate_rfq_payload(
    supplier_name,
    material,
    quantity,
    unit,
    project_name,
    delivery_date=None,
    supplier_id=None,
    supplier_location=None,
    expected_rate=None,
    distance_km=None,
    lead_time_days=None
):
    """
    Generate structured RFQ payload for API/frontend consumption
    
    Returns:
        Dictionary with RFQ details and formatted text
    """
    rfq_text = generate_rfq(
        supplier_name=supplier_name,
        material=material,
        quantity=quantity,
        unit=unit,
        project_name=project_name,
        delivery_date=delivery_date,
        supplier_location=supplier_location,
        expected_rate=expected_rate
    )
    
    payload = {
        "rfq_id": f"RFQ-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "date": datetime.today().strftime("%d-%m-%Y"),
        "supplier": {
            "name": supplier_name,
            "id": supplier_id,
            "location": supplier_location
        },
        "project": {
            "name": project_name
        },
        "material": {
            "description": material,
            "quantity": quantity,
            "unit": unit,
            "expected_rate": expected_rate
        },
        "logistics": {
            "delivery_date": delivery_date,
            "distance_km": distance_km,
            "lead_time_days": lead_time_days
        },
        "rfq_text": rfq_text,
        "status": "draft"
    }
    
    return payload
