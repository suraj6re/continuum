const getElementCategory = (elementName) => {
  const name = (elementName || '').toLowerCase();
  if (name.includes('excavation') || name.includes('foundation')) return 'Foundation';
  if (name.includes('concrete') || name.includes('steel') || name.includes('column') || name.includes('beam') || name.includes('slab') || name.includes('formwork')) return 'Structural';
  if (name.includes('brick') || name.includes('masonry') || name.includes('wall')) return 'Walls';
  return 'Finishing';
};

const getValidationStatus = (confidence) => {
  if (confidence >= 0.95) return 'Validated';
  if (confidence >= 0.90) return 'Review Recommended';
  return 'Attention Required';
};

const generateFlags = (element, allElements) => {
  const flags = [];
  
  // Low confidence flag
  if (element.confidence < 0.90) {
    flags.push('Low model certainty');
  }
  
  // Zero quantity check
  if (!element.quantity || element.quantity === 0) {
    flags.push('Zero quantity detected');
  }
  
  // Extreme quantity deviation
  const category = getElementCategory(element.element_name || element.name);
  const categoryElements = allElements.filter(e => 
    getElementCategory(e.element_name || e.name) === category
  );
  
  if (categoryElements.length > 1) {
    const quantities = categoryElements.map(e => e.quantity || 0);
    const avg = quantities.reduce((a, b) => a + b, 0) / quantities.length;
    const stdDev = Math.sqrt(
      quantities.reduce((sum, q) => sum + Math.pow(q - avg, 2), 0) / quantities.length
    );
    
    if (Math.abs(element.quantity - avg) > 3 * stdDev && stdDev > 0) {
      flags.push('Extreme quantity deviation');
    }
  }
  
  // Missing dimension reference
  if (element.confidence < 0.93 && element.confidence >= 0.90) {
    flags.push('Missing dimension reference');
  }
  
  // Irregular geometry
  if (element.confidence < 0.88) {
    flags.push('Irregular geometry detected');
  }
  
  return flags;
};

const performCrossValidation = (qtoElements) => {
  const checks = [];
  
  // Check for slab without reinforcement
  const hasSlabs = qtoElements.some(e => 
    (e.element_name || e.name || '').toLowerCase().includes('slab')
  );
  const hasSteel = qtoElements.some(e => 
    (e.element_name || e.name || '').toLowerCase().includes('steel') ||
    (e.element_name || e.name || '').toLowerCase().includes('reinforcement')
  );
  
  if (hasSlabs && !hasSteel) {
    checks.push({
      check: 'Slab-Reinforcement Consistency',
      status: 'Warning',
      message: 'Slab detected but no reinforcement found'
    });
  }
  
  // Check for concrete without formwork
  const hasConcrete = qtoElements.some(e => 
    (e.element_name || e.name || '').toLowerCase().includes('concrete')
  );
  const hasFormwork = qtoElements.some(e => 
    (e.element_name || e.name || '').toLowerCase().includes('formwork')
  );
  
  if (hasConcrete && !hasFormwork) {
    checks.push({
      check: 'Concrete-Formwork Consistency',
      status: 'Info',
      message: 'Concrete detected but no formwork found'
    });
  }
  
  return checks;
};

export const analyzeValidation = (qtoElements, costItems = []) => {
  if (!qtoElements || qtoElements.length === 0) {
    return {
      elements: [],
      summary: {
        total: 0,
        high_confidence: 0,
        medium_confidence: 0,
        low_confidence: 0,
        needs_review: 0,
        average_confidence: 0
      },
      metrics: {
        total_elements: 0,
        validated: 0,
        flagged: 0,
        user_corrections: 0,
        coverage_percent: 0
      },
      crossValidation: []
    };
  };

  const validatedElements = qtoElements.map(element => {
    const confidence = element.confidence || 0;
    const flags = generateFlags(element, qtoElements);
    
    return {
      ...element,
      category: getElementCategory(element.element_name || element.name),
      validation_status: getValidationStatus(confidence),
      flags,
      approval_status: confidence >= 0.95 ? 'approved' : 'pending',
      user_corrected: false,
      override_quantity: null,
      notes: ''
    };
  });

  const highConfidence = validatedElements.filter(e => e.confidence >= 0.95).length;
  const mediumConfidence = validatedElements.filter(e => e.confidence >= 0.90 && e.confidence < 0.95).length;
  const lowConfidence = validatedElements.filter(e => e.confidence < 0.90).length;
  const needsReview = validatedElements.filter(e => e.flags.length > 0).length;
  const avgConfidence = validatedElements.reduce((sum, e) => sum + e.confidence, 0) / validatedElements.length;

  const validated = validatedElements.filter(e => e.approval_status === 'approved').length;
  const flagged = validatedElements.filter(e => e.flags.length > 0).length;
  const userCorrected = validatedElements.filter(e => e.user_corrected).length;
  const coverage = ((validated + userCorrected) / validatedElements.length) * 100;

  const crossValidation = performCrossValidation(qtoElements);

  return {
    elements: validatedElements,
    summary: {
      total: validatedElements.length,
      high_confidence: highConfidence,
      medium_confidence: mediumConfidence,
      low_confidence: lowConfidence,
      needs_review: needsReview,
      average_confidence: avgConfidence
    },
    metrics: {
      total_elements: validatedElements.length,
      validated,
      flagged,
      user_corrections: userCorrected,
      coverage_percent: coverage
    },
    crossValidation
  };
};

export const exportValidationReport = (validationData, format = 'csv') => {
  if (format === 'csv') {
    const headers = ['Element', 'Category', 'Quantity', 'Unit', 'Confidence', 'Status', 'Flags', 'Approval', 'Override', 'Notes'];
    const rows = validationData.elements.map(e => [
      e.element_name || e.name,
      e.category,
      e.override_quantity || e.quantity,
      e.unit || '',
      (e.confidence * 100).toFixed(1) + '%',
      e.validation_status,
      e.flags.join('; '),
      e.approval_status,
      e.override_quantity ? 'Yes' : 'No',
      e.notes || ''
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `validation-report-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  } else {
    const data = {
      ...validationData,
      exported_at: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `validation-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
};
