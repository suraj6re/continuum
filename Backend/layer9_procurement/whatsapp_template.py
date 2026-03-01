from datetime import datetime

def generate_whatsapp(
    supplier_name,
    material,
    quantity,
    unit,
    project_name,
    expected_rate=None
):
    """
    Generate WhatsApp-ready message for supplier inquiry
    
    Args:
        supplier_name: Name of the supplier
        material: Material description
        quantity: Quantity required
        unit: Unit of measurement
        project_name: Project name
        expected_rate: Expected rate (optional)
    
    Returns:
        WhatsApp-formatted message string
    """
    today = datetime.today().strftime("%d-%m-%Y")
    
    message = (
        f"Hello {supplier_name},\n\n"
        f"We require the following material for project '{project_name}':\n"
        f"- {material}\n"
        f"- Quantity: {quantity} {unit}\n"
    )
    
    if expected_rate:
        message += f"- Reference Rate: Rs.{expected_rate}/{unit}\n"
    
    message += (
        f"\nKindly confirm:\n"
        f"• Best unit rate\n"
        f"• Availability\n"
        f"• Delivery timeline\n\n"
        f"Date: {today}\n"
        f"Thank you."
    )
    
    return message


def generate_whatsapp_payload(
    supplier_name,
    material,
    quantity,
    unit,
    project_name,
    expected_rate=None,
    supplier_phone=None
):
    """
    Generate structured WhatsApp payload for API/frontend
    
    Returns:
        Dictionary with WhatsApp message details
    """
    message = generate_whatsapp(
        supplier_name=supplier_name,
        material=material,
        quantity=quantity,
        unit=unit,
        project_name=project_name,
        expected_rate=expected_rate
    )
    
    payload = {
        "message_id": f"WA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "channel": "whatsapp",
        "recipient": {
            "name": supplier_name,
            "phone": supplier_phone
        },
        "message": message,
        "character_count": len(message),
        "status": "draft",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return payload
