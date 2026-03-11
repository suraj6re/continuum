from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import re
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from cost_mapper import CostMapper

app = FastAPI(title="AI Cost Matcher API")

model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = joblib.load('ml_reranker/model.pkl')
df = pd.read_csv('cost_book_demo.csv')
cost_embeddings = model.encode(df['description'].tolist())
cost_mapper = CostMapper()

def extract_grade(text):
    if not text:
        return None
    match = re.search(r"\bm[1-9]\d\b", text.lower())
    return match.group() if match else None

def grade_match(qto, cost):
    q_grade = extract_grade(qto)
    c_grade = extract_grade(cost)
    
    if q_grade is None or c_grade is None:
        return 0
    
    return 1 if q_grade == c_grade else 0

def unit_match(qto_unit, cost_unit):
    return 1 if qto_unit == cost_unit else 0

components = ["slab", "column", "beam", "wall"]

def component_match(qto, cost):
    for comp in components:
        if comp in qto and comp in cost:
            return 1
    return 0

class QTORequest(BaseModel):
    description: str
    unit: str
    quantity: float = 1.0  # Added quantity for cost calculation
    top_k: int = 3

@app.post("/align_cost")
def align_cost(request: QTORequest):
    try:
        start = time.time()
        
        # Debug: Check grade extraction
        debug_grade = extract_grade(request.description)
        print(f"DEBUG GRADE for '{request.description}': {debug_grade}")
        
        query_embedding = model.encode([request.description])
        scores = cosine_similarity(query_embedding, cost_embeddings)[0]
        
        feature_data = []
        for idx, row in df.iterrows():
            feature_data.append({
                "semantic_score": scores[idx],
                "grade_match": grade_match(request.description, row["description"]),
                "unit_match": unit_match(request.unit, row["unit"]),
                "component_match": component_match(request.description.lower(), row["description"].lower())
            })
        
        features_df = pd.DataFrame(feature_data)
        ml_probs = reranker.predict_proba(features_df)[:, 1]
        
        df_temp = df.copy()
        df_temp['ml_probability'] = ml_probs
        df_temp['grade_match'] = [f['grade_match'] for f in feature_data]
        df_temp['unit_match'] = [f['unit_match'] for f in feature_data]
        df_temp['component_match'] = [f['component_match'] for f in feature_data]
        df_temp['semantic_score'] = [f['semantic_score'] for f in feature_data]
        df_sorted = df_temp.sort_values('ml_probability', ascending=False)
        
        results = []
        top_prob = float(df_sorted.iloc[0]['ml_probability'])
        
        for _, row in df_sorted.head(request.top_k).iterrows():
            prob = row['ml_probability']
            
            # Calculate cost mapping
            cost_mapping = cost_mapper.calculate_mapped_cost(
                request.quantity,
                request.unit,
                float(row['rate']),
                row['unit'],
                request.description,
                row['description']
            )
            
            # Get overall confidence
            mapping_confidence, adjusted_prob = cost_mapper.get_mapping_confidence(
                prob, row['unit_match'], cost_mapping['can_map']
            )
            
            result_item = {
                "cost_id": int(row['id']),
                "description": row['description'],
                "unit": row['unit'],
                "rate": float(row['rate']),
                "ml_probability": float(prob),
                "confidence": mapping_confidence,
                "match_details": {
                    "grade_matched": bool(row['grade_match']),
                    "unit_matched": bool(row['unit_match']),
                    "component_matched": bool(row['component_match']),
                    "semantic_score": float(row['semantic_score'])
                },
                "cost_mapping": cost_mapping
            }
            
            results.append(result_item)
        
        processing_time = (time.time() - start) * 1000
        
        # Determine best match (highest probability that can be mapped)
        best_match = None
        for result in results:
            if result['cost_mapping']['can_map']:
                best_match = result
                break
        
        return {
            "query": {
                "description": request.description,
                "quantity": request.quantity,
                "unit": request.unit
            },
            "best_match": best_match,
            "top_matches": results,
            "model_version": "v1.1-with-cost-mapping",
            "ranking_strategy": "Transformer embeddings + supervised re-ranking + intelligent cost mapping",
            "needs_review": bool(top_prob < 0.4 or (best_match and not best_match['match_details']['unit_matched'])),
            "processing_time_ms": round(processing_time, 2)
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/")
def root():
    return {"message": "AI Cost Matcher API", "endpoint": "/align_cost"}
