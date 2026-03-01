export default function Layer6Output({ data }) {
  if (!data) {
    return <div className="text-text-muted">No Layer 6 data available</div>;
  }

  const { flags, overall_confidence, uncertainty_band, quality_grade, validated_aggregation, validation_summary } = data;

  const getGradeColor = (grade) => {
    const colors = {
      'A': 'text-emerald-600',
      'B': 'text-blue-600',
      'C': 'text-yellow-600',
      'D': 'text-red-600'
    };
    return colors[grade] || 'text-text-secondary';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      'High': 'bg-red-100 text-red-800 border-red-300',
      'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'Low': 'bg-blue-100 text-blue-800 border-blue-300'
    };
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  return (
    <div className="space-y-6">
      {/* Overall Quality */}
      <div className="bg-bg-section p-6 rounded-lg border border-border-warm">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Overall Quality Assessment</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-text-muted">Quality Grade</p>
            <p className={`text-3xl font-bold ${getGradeColor(quality_grade)}`}>{quality_grade}</p>
          </div>
          <div>
            <p className="text-sm text-text-muted">Overall Confidence</p>
            <p className="text-3xl font-bold text-brand-orange">{(overall_confidence * 100).toFixed(1)}%</p>
          </div>
          <div>
            <p className="text-sm text-text-muted">Uncertainty Band</p>
            <p className="text-lg font-semibold text-text-primary">Cost: {uncertainty_band?.cost}</p>
            <p className="text-lg font-semibold text-text-primary">Duration: {uncertainty_band?.duration}</p>
          </div>
        </div>
      </div>

      {/* Flags */}
      {flags && flags.length > 0 && (
        <div className="bg-bg-section p-6 rounded-lg border border-border-warm">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Validation Flags ({flags.length})</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {flags.map((flag, idx) => (
              <div key={idx} className={`p-3 rounded border ${getSeverityColor(flag.severity)}`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-semibold">{flag.type}</p>
                    <p className="text-sm">Element: {flag.element}</p>
                    <p className="text-xs mt-1">{flag.details}</p>
                  </div>
                  <span className="text-xs font-bold">{flag.severity}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation Summary */}
      {validation_summary && (
        <div className="bg-bg-section p-6 rounded-lg border border-border-warm">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Validation Summary</h3>
          
          <div className="space-y-4">
            {/* Consistency Checks */}
            <div className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-medium text-text-primary">Internal Consistency</h4>
              <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
                <div>
                  <span className="text-text-muted">Total: </span>
                  <span className="text-text-primary font-medium">{validation_summary.consistency_checks.total_checks}</span>
                </div>
                <div>
                  <span className="text-text-muted">Passed: </span>
                  <span className="text-emerald-600 font-medium">{validation_summary.consistency_checks.passed}</span>
                </div>
                <div>
                  <span className="text-text-muted">Pass Rate: </span>
                  <span className="text-text-primary font-medium">{(validation_summary.consistency_checks.pass_rate * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Sanity Checks */}
            <div className="border-l-4 border-purple-500 pl-4">
              <h4 className="font-medium text-text-primary">Sanity Checks</h4>
              <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
                <div>
                  <span className="text-text-muted">Total: </span>
                  <span className="text-text-primary font-medium">{validation_summary.sanity_checks.total_checks}</span>
                </div>
                <div>
                  <span className="text-text-muted">Passed: </span>
                  <span className="text-emerald-600 font-medium">{validation_summary.sanity_checks.passed}</span>
                </div>
                <div>
                  <span className="text-text-muted">Pass Rate: </span>
                  <span className="text-text-primary font-medium">{(validation_summary.sanity_checks.pass_rate * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Anomaly Detection */}
            <div className="border-l-4 border-red-500 pl-4">
              <h4 className="font-medium text-text-primary">Anomaly Detection</h4>
              <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
                <div>
                  <span className="text-text-muted">Elements: </span>
                  <span className="text-text-primary font-medium">{validation_summary.anomaly_detection.total_anomalies}</span>
                </div>
                <div>
                  <span className="text-text-muted">Anomalies: </span>
                  <span className="text-red-600 font-medium">{validation_summary.anomaly_detection.anomalies?.length || 0}</span>
                </div>
                <div>
                  <span className="text-text-muted">Rate: </span>
                  <span className="text-text-primary font-medium">{(validation_summary.anomaly_detection.anomaly_rate * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* Redundancy Checks */}
            {validation_summary.redundancy_checks && (
              <div className="border-l-4 border-yellow-500 pl-4">
                <h4 className="font-medium text-text-primary">Redundant Measurement Comparison</h4>
                <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
                  <div>
                    <span className="text-text-muted">Total: </span>
                    <span className="text-text-primary font-medium">{validation_summary.redundancy_checks.total_checks}</span>
                  </div>
                  <div>
                    <span className="text-text-muted">Mismatches: </span>
                    <span className="text-yellow-600 font-medium">{validation_summary.redundancy_checks.issues?.length || 0}</span>
                  </div>
                  <div>
                    <span className="text-text-muted">Pass Rate: </span>
                    <span className="text-text-primary font-medium">{(validation_summary.redundancy_checks.pass_rate * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* Duplicate Detection */}
            {validation_summary.duplicate_detection && (
              <div className="border-l-4 border-orange-500 pl-4">
                <h4 className="font-medium text-text-primary">Duplicate Detection</h4>
                <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
                  <div>
                    <span className="text-text-muted">Checked: </span>
                    <span className="text-text-primary font-medium">{validation_summary.duplicate_detection.duplicates?.length || 0}</span>
                  </div>
                  <div>
                    <span className="text-text-muted">Duplicates: </span>
                    <span className="text-orange-600 font-medium">{validation_summary.duplicate_detection.duplicates?.length || 0}</span>
                  </div>
                  <div>
                    <span className="text-text-muted">Rate: </span>
                    <span className="text-text-primary font-medium">{(validation_summary.duplicate_detection.duplicate_rate * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footprint Validation */}
          {validation_summary.footprint_validation && !validation_summary.footprint_validation.valid && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-800">
                <span className="font-semibold">⚠ Footprint Warning:</span> {validation_summary.footprint_validation.flag}
              </p>
            </div>
          )}

          {/* Steel-Concrete Ratio Issues */}
          {validation_summary.steel_concrete_ratio?.issues?.length > 0 && (
            <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded">
              <p className="text-sm text-orange-800">
                <span className="font-semibold">⚠ Steel Ratio Issues:</span> {validation_summary.steel_concrete_ratio.issues.length} element type(s) with abnormal steel-to-concrete ratios
              </p>
            </div>
          )}
        </div>
      )}

      {/* Confidence Distribution */}
      {data.confidence_distribution && (
        <div className="bg-bg-section p-6 rounded-lg border border-border-warm">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Confidence Distribution</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-emerald-600">{data.confidence_distribution.High}</p>
              <p className="text-sm text-text-muted">High Confidence</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{data.confidence_distribution.Medium}</p>
              <p className="text-sm text-text-muted">Medium Confidence</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">{data.confidence_distribution.Low}</p>
              <p className="text-sm text-text-muted">Low Confidence</p>
            </div>
          </div>
        </div>
      )}

      {/* Validated Quantities with Uncertainty */}
      {validated_aggregation && Object.keys(validated_aggregation).length > 0 && (
        <div className="bg-bg-section p-6 rounded-lg border border-border-warm">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Validated Quantities with Uncertainty</h3>
          <div className="space-y-3">
            {Object.entries(validated_aggregation).map(([material, data]) => (
              <div key={material} className="border border-border-warm rounded p-4">
                <h4 className="font-medium text-text-primary mb-2">{material}</h4>
                
                {data.volume_with_uncertainty && (
                  <div className="mb-2">
                    <p className="text-sm text-text-muted">Volume</p>
                    <p className="text-lg font-semibold text-brand-orange">{data.volume_with_uncertainty}</p>
                    {data.volume_range && (
                      <p className="text-xs text-text-muted">
                        Range: {data.volume_range.min} - {data.volume_range.max} m³
                      </p>
                    )}
                  </div>
                )}
                
                {data.area_with_uncertainty && (
                  <div className="mb-2">
                    <p className="text-sm text-text-muted">Area</p>
                    <p className="text-lg font-semibold text-brand-orange">{data.area_with_uncertainty}</p>
                    {data.area_range && (
                      <p className="text-xs text-text-muted">
                        Range: {data.area_range.min} - {data.area_range.max} m²
                      </p>
                    )}
                  </div>
                )}
                
                <div className="flex justify-between items-center mt-2 text-sm">
                  <span className="text-text-muted">Confidence: <span className="font-medium text-text-primary">{(data.confidence * 100).toFixed(1)}%</span></span>
                  <span className="text-text-muted">Uncertainty: <span className="font-medium text-text-primary">±{data.uncertainty_pct}%</span></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
