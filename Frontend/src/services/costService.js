const API_BASE_URL = 'http://localhost:8000';

export const fetchCostData = async (drawingId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/upload/drawing/${drawingId}/layer7`);
    if (!response.ok) throw new Error('Backend not available');
    const result = await response.json();
    if (result.success && result.data) {
      return result.data;
    }
    throw new Error('Invalid response');
  } catch (error) {
    console.error('Failed to fetch cost data:', error);
    return generateMockCostData(drawingId);
  }
};

const generateMockCostData = (projectId) => {
  return {
    project_id: projectId,
    cost_summary: {
      material_cost: 12500000,
      labor_cost: 4500000,
      equipment_cost: 1500000,
      total_cost: 18500000
    },
    cost_items: [
      {
        element_id: 'E1',
        element_name: 'Concrete Slab',
        quantity: 245.5,
        unit: 'm³',
        unit_rate: 7500,
        material_cost: 1841250,
        labor_cost: 320000,
        equipment_cost: 120000,
        total_cost: 2281250,
        confidence: 0.96
      },
      {
        element_id: 'E2',
        element_name: 'Steel Reinforcement',
        quantity: 12450,
        unit: 'kg',
        unit_rate: 85,
        material_cost: 1058250,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 1058250,
        confidence: 0.94
      },
      {
        element_id: 'E3',
        element_name: 'Brick Masonry',
        quantity: 1850,
        unit: 'm²',
        unit_rate: 450,
        material_cost: 832500,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 832500,
        confidence: 0.92
      },
      {
        element_id: 'E4',
        element_name: 'Plaster Work',
        quantity: 3200,
        unit: 'm²',
        unit_rate: 180,
        material_cost: 576000,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 576000,
        confidence: 0.89
      },
      {
        element_id: 'E5',
        element_name: 'Floor Tiles',
        quantity: 1450,
        unit: 'm²',
        unit_rate: 650,
        material_cost: 942500,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 942500,
        confidence: 0.97
      },
      {
        element_id: 'E6',
        element_name: 'Column Concrete',
        quantity: 42.7,
        unit: 'm³',
        unit_rate: 8500,
        material_cost: 362950,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 362950,
        confidence: 0.95
      },
      {
        element_id: 'E7',
        element_name: 'Beam Concrete',
        quantity: 38.2,
        unit: 'm³',
        unit_rate: 8200,
        material_cost: 313240,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 313240,
        confidence: 0.93
      },
      {
        element_id: 'E8',
        element_name: 'Formwork',
        quantity: 2800,
        unit: 'm²',
        unit_rate: 320,
        material_cost: 0,
        labor_cost: 896000,
        equipment_cost: 0,
        total_cost: 896000,
        confidence: 0.91
      },
      {
        element_id: 'E9',
        element_name: 'Excavation',
        quantity: 450,
        unit: 'm³',
        unit_rate: 280,
        material_cost: 0,
        labor_cost: 0,
        equipment_cost: 126000,
        total_cost: 126000,
        confidence: 0.98
      },
      {
        element_id: 'E10',
        element_name: 'Painting',
        quantity: 4200,
        unit: 'm²',
        unit_rate: 95,
        material_cost: 399000,
        labor_cost: 0,
        equipment_cost: 0,
        total_cost: 399000,
        confidence: 0.88
      }
    ]
  };
};

export const exportCostToCSV = (costItems, costSummary, adjustmentFactor) => {
  const headers = ['Element', 'Quantity', 'Unit', 'Unit Rate', 'Material Cost', 'Labor Cost', 'Equipment Cost', 'Total Cost', 'Confidence'];
  const rows = costItems.map(item => [
    item.element_name,
    item.quantity,
    item.unit,
    item.unit_rate,
    item.material_cost,
    item.labor_cost,
    item.equipment_cost,
    item.total_cost,
    (item.confidence * 100).toFixed(1) + '%'
  ]);
  
  const summaryRows = [
    [],
    ['Summary'],
    ['Material Cost', costSummary.material_cost],
    ['Labor Cost', costSummary.labor_cost],
    ['Equipment Cost', costSummary.equipment_cost],
    ['Total Cost', costSummary.total_cost],
    ['Adjustment Factor', adjustmentFactor]
  ];

  const csv = [headers, ...rows, ...summaryRows]
    .map(row => row.join(','))
    .join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `cost-report-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
};

export const exportCostToJSON = (costItems, costSummary, adjustmentFactor) => {
  const data = {
    cost_summary: costSummary,
    cost_items: costItems,
    adjustment_factor: adjustmentFactor,
    exported_at: new Date().toISOString()
  };

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `cost-report-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
};
