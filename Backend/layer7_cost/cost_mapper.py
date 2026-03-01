"""
Cost Mapping Module
Handles intelligent unit conversion and cost mapping between QTO and Cost Book items
"""

class CostMapper:
    """
    Maps QTO items to Cost Book items with intelligent unit conversion
    """
    
    # Unit conversion factors and relationships
    UNIT_CONVERSIONS = {
        # Volume conversions
        ('m3', 'kg'): {
            'materials': {
                'steel': 7850,  # kg/m3 - density of steel
                'concrete': 2400,  # kg/m3 - density of RCC
                'cement': 1440,  # kg/m3 - density of cement
            }
        },
        ('kg', 'm3'): {
            'materials': {
                'steel': 1/7850,
                'concrete': 1/2400,
                'cement': 1/1440,
            }
        },
        # Area conversions
        ('m2', 'm3'): 'requires_thickness',
        ('m3', 'm2'): 'requires_thickness',
        # Direct conversions
        ('m', 'mm'): 1000,
        ('mm', 'm'): 0.001,
        ('m2', 'sqm'): 1,
        ('sqm', 'm2'): 1,
        ('m3', 'cum'): 1,
        ('cum', 'm3'): 1,
    }
    
    # Material keywords for intelligent detection
    MATERIAL_KEYWORDS = {
        'steel': ['steel', 'reinforcement', 'fe500', 'fe415', 'tmt', 'bars', 'rebar'],
        'concrete': ['concrete', 'rcc', 'm25', 'm20', 'm30', 'm15', 'm10'],
        'cement': ['cement', 'mortar'],
        'brick': ['brick', 'masonry'],
        'plaster': ['plaster'],
        'paint': ['paint', 'painting'],
        'tiles': ['tiles', 'flooring'],
    }
    
    def __init__(self):
        self.conversion_log = []
    
    def detect_material(self, description):
        """
        Detect material type from description
        """
        desc_lower = description.lower()
        for material, keywords in self.MATERIAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return material
        return None
    
    def can_convert(self, qto_unit, cost_unit, qto_desc, cost_desc):
        """
        Check if unit conversion is possible
        Returns: (can_convert: bool, conversion_factor: float, warning: str)
        """
        # Same unit - no conversion needed
        if qto_unit == cost_unit:
            return True, 1.0, None
        
        # Check if conversion exists
        conversion_key = (qto_unit, cost_unit)
        if conversion_key not in self.UNIT_CONVERSIONS:
            return False, None, f"No conversion available from {qto_unit} to {cost_unit}"
        
        conversion_data = self.UNIT_CONVERSIONS[conversion_key]
        
        # Handle material-based conversions (e.g., m3 to kg)
        if isinstance(conversion_data, dict) and 'materials' in conversion_data:
            qto_material = self.detect_material(qto_desc)
            cost_material = self.detect_material(cost_desc)
            
            if qto_material and qto_material in conversion_data['materials']:
                factor = conversion_data['materials'][qto_material]
                warning = f"Converting {qto_unit} to {cost_unit} using {qto_material} density"
                return True, factor, warning
            else:
                return False, None, f"Cannot determine material type for conversion"
        
        # Handle thickness-dependent conversions
        elif conversion_data == 'requires_thickness':
            return False, None, f"Conversion requires thickness information"
        
        # Handle direct conversions
        elif isinstance(conversion_data, (int, float)):
            return True, conversion_data, None
        
        return False, None, "Unknown conversion type"
    
    def calculate_mapped_cost(self, qto_quantity, qto_unit, cost_rate, cost_unit, 
                             qto_desc, cost_desc):
        """
        Calculate the mapped cost with unit conversion
        
        Returns: {
            'can_map': bool,
            'mapped_rate': float,
            'mapped_total': float,
            'conversion_factor': float,
            'warning': str,
            'explanation': str
        }
        """
        can_convert, factor, warning = self.can_convert(
            qto_unit, cost_unit, qto_desc, cost_desc
        )
        
        if not can_convert:
            return {
                'can_map': False,
                'mapped_rate': None,
                'mapped_total': None,
                'conversion_factor': None,
                'warning': warning,
                'explanation': f"Cannot map: {warning}"
            }
        
        # Calculate mapped values
        if factor == 1.0:
            # Direct mapping - same units
            mapped_rate = cost_rate
            mapped_total = qto_quantity * cost_rate
            explanation = f"Direct mapping: {qto_quantity} {qto_unit} x Rs.{cost_rate}/{cost_unit}"
        else:
            # Conversion required
            mapped_rate = cost_rate / factor if qto_unit != cost_unit else cost_rate
            mapped_total = qto_quantity * mapped_rate
            explanation = (
                f"Converted mapping: {qto_quantity} {qto_unit} x "
                f"Rs.{cost_rate}/{cost_unit} (factor: {factor:.2f}) = "
                f"Rs.{mapped_rate:.2f}/{qto_unit}"
            )
        
        return {
            'can_map': True,
            'mapped_rate': round(mapped_rate, 2),
            'mapped_total': round(mapped_total, 2),
            'conversion_factor': factor,
            'warning': warning,
            'explanation': explanation,
            'original_rate': cost_rate,
            'original_unit': cost_unit,
            'target_unit': qto_unit
        }
    
    def get_mapping_confidence(self, ml_probability, unit_match, can_map):
        """
        Determine overall mapping confidence considering ML probability and unit compatibility
        """
        if not can_map:
            return 'Not Mappable', 0.0
        
        if unit_match == 1:
            # Perfect unit match
            if ml_probability > 0.7:
                return 'Very High', ml_probability
            elif ml_probability > 0.5:
                return 'High', ml_probability
            elif ml_probability > 0.3:
                return 'Medium', ml_probability
            else:
                return 'Low', ml_probability
        else:
            # Unit conversion required - reduce confidence
            adjusted_prob = ml_probability * 0.8  # 20% penalty for conversion
            if adjusted_prob > 0.6:
                return 'High (with conversion)', adjusted_prob
            elif adjusted_prob > 0.4:
                return 'Medium (with conversion)', adjusted_prob
            else:
                return 'Low (with conversion)', adjusted_prob


def demonstrate_cost_mapping():
    """
    Demonstrate the cost mapping with examples
    """
    mapper = CostMapper()
    
    print("=" * 80)
    print("COST MAPPING DEMONSTRATION")
    print("=" * 80)
    
    # Example 1: Unit mismatch - Steel (m3 to kg)
    print("\n[Example 1] Steel Reinforcement (Unit Mismatch)")
    print("-" * 80)
    qto = {
        'description': 'Steel reinforcement Fe500 bars',
        'quantity': 2.5,
        'unit': 'm3'
    }
    cost = {
        'description': 'Steel reinforcement Fe500',
        'rate': 65,
        'unit': 'kg'
    }
    
    result = mapper.calculate_mapped_cost(
        qto['quantity'], qto['unit'],
        cost['rate'], cost['unit'],
        qto['description'], cost['description']
    )
    
    print(f"QTO: {qto['description']}")
    print(f"     Quantity: {qto['quantity']} {qto['unit']}")
    print(f"\nCost Item: {cost['description']}")
    print(f"           Rate: Rs.{cost['rate']}/{cost['unit']}")
    print(f"\n{'[CAN MAP]' if result['can_map'] else '[CANNOT MAP]'}")
    if result['can_map']:
        print(f"Mapped Rate: Rs.{result['mapped_rate']}/{qto['unit']}")
        print(f"Total Cost: Rs.{result['mapped_total']}")
        print(f"Conversion Factor: {result['conversion_factor']}")
        if result['warning']:
            print(f"WARNING: {result['warning']}")
        print(f"\nExplanation: {result['explanation']}")
    else:
        print(f"ERROR: {result['explanation']}")
    
    # Example 2: Perfect match - Concrete
    print("\n\n[Example 2] RCC Slab M25 (Perfect Match)")
    print("-" * 80)
    qto = {
        'description': 'RCC slab M25 150mm thick',
        'quantity': 50,
        'unit': 'm3'
    }
    cost = {
        'description': 'Reinforced Cement Concrete M25',
        'rate': 7200,
        'unit': 'm3'
    }
    
    result = mapper.calculate_mapped_cost(
        qto['quantity'], qto['unit'],
        cost['rate'], cost['unit'],
        qto['description'], cost['description']
    )
    
    print(f"QTO: {qto['description']}")
    print(f"     Quantity: {qto['quantity']} {qto['unit']}")
    print(f"\nCost Item: {cost['description']}")
    print(f"           Rate: Rs.{cost['rate']}/{cost['unit']}")
    print(f"\n{'[CAN MAP]' if result['can_map'] else '[CANNOT MAP]'}")
    if result['can_map']:
        print(f"Mapped Rate: Rs.{result['mapped_rate']}/{qto['unit']}")
        print(f"Total Cost: Rs.{result['mapped_total']}")
        print(f"\nExplanation: {result['explanation']}")
    
    # Example 3: Impossible conversion
    print("\n\n[Example 3] Impossible Conversion")
    print("-" * 80)
    qto = {
        'description': 'Brick masonry work',
        'quantity': 100,
        'unit': 'm3'
    }
    cost = {
        'description': 'Cement plaster 12mm thick',
        'rate': 280,
        'unit': 'm2'
    }
    
    result = mapper.calculate_mapped_cost(
        qto['quantity'], qto['unit'],
        cost['rate'], cost['unit'],
        qto['description'], cost['description']
    )
    
    print(f"QTO: {qto['description']}")
    print(f"     Quantity: {qto['quantity']} {qto['unit']}")
    print(f"\nCost Item: {cost['description']}")
    print(f"           Rate: Rs.{cost['rate']}/{cost['unit']}")
    print(f"\n{'[CAN MAP]' if result['can_map'] else '[CANNOT MAP]'}")
    if not result['can_map']:
        print(f"ERROR: {result['explanation']}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    demonstrate_cost_mapping()
