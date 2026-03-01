"""Statistical Outlier Detector"""
from typing import Dict, List
import statistics

def detect_outliers(measurements: List[Dict]) -> Dict:
    """Detect statistical anomalies using 3-sigma rule"""
    by_type = {}
    for m in measurements:
        elem_type = m.get("type")
        if elem_type not in by_type:
            by_type[elem_type] = []
        by_type[elem_type].append(m)
    
    anomalies = []
    
    for elem_type, elements in by_type.items():
        if len(elements) < 3:
            continue
        
        volumes = [e.get("measurements", {}).get("volume", 0) for e in elements if "volume" in e.get("measurements", {})]
        
        if len(volumes) >= 3:
            mean_vol = statistics.mean(volumes)
            stdev_vol = statistics.stdev(volumes) if len(volumes) > 1 else 0
            
            for i, vol in enumerate(volumes):
                if stdev_vol > 0:
                    z_score = abs((vol - mean_vol) / stdev_vol)
                    
                    if z_score > 3:
                        anomalies.append({
                            "element_id": elements[i].get("element_id"),
                            "type": elem_type,
                            "metric": "volume",
                            "value": vol,
                            "mean": mean_vol,
                            "z_score": round(z_score, 2),
                            "severity": "high" if z_score > 4 else "medium"
                        })
    
    return {
        "total_anomalies": len(anomalies),
        "anomalies": anomalies,
        "anomaly_rate": len(anomalies) / len(measurements) if measurements else 0
    }
