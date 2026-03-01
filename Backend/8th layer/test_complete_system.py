# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from cost_mapper import CostMapper

print("[*] Initializing components...")
model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = joblib.load('ml_reranker/model.pkl')
cost_mapper = CostMapper()

df = pd.read_csv('cost_book_demo.csv')
cost_embeddings = model.encode(df['description'].tolist())

def extract_grade(text):
    if not text:
        return None
    match = re.search(r"\bm[1-9]\d\b", text.lower())
    return match.group() if match else None

def grade_match(qto, cost):
    return 1 if extract_grade(qto) == extract_grade(cost) else 0

def unit_match(qto_unit, cost_unit):
    return 1 if qto_unit == cost_unit else 0

components = ["slab", "column", "beam", "wall"]

def component_match(qto, cost):
    for comp in components:
        if comp in qto and comp in cost:
            return 1
    return 0

def process_qto_item(qto_item, qto_unit, qto_quantity):
    print("\n" + "="*100)
    print(f"[PROCESSING QTO ITEM]")
    print("="*100)
    print(f"Description: {qto_item}")
    print(f"Quantity: {qto_quantity} {qto_unit}")
    print()
    
    print("[STEP 1: SEMANTIC SIMILARITY]")
    print("-"*100)
    query_embedding = model.encode([qto_item])
    semantic_scores = cosine_similarity(query_embedding, cost_embeddings)[0]
    print(f"[OK] Computed semantic similarity for {len(df)} cost items")
    print()
    
    print("[STEP 2: FEATURE ENGINEERING]")
    print("-"*100)
    feature_data = []
    for idx, row in df.iterrows():
        features = {
            "semantic_score": semantic_scores[idx],
            "grade_match": grade_match(qto_item, row["description"]),
            "unit_match": unit_match(qto_unit, row["unit"]),
            "component_match": component_match(qto_item.lower(), row["description"].lower())
        }
        feature_data.append(features)
    
    print(f"[OK] Extracted 4 features for each cost item")
    print()
    
    print("[STEP 3: ML RANKING]")
    print("-"*100)
    features_df = pd.DataFrame(feature_data)
    ml_probs = reranker.predict_proba(features_df)[:, 1]
    
    coefficients = reranker.coef_[0]
    bias = reranker.intercept_[0]
    
    print(f"[OK] Model weights:")
    print(f"  semantic_score: {coefficients[0]:.3f}")
    print(f"  grade_match: {coefficients[1]:.3f}")
    print(f"  unit_match: {coefficients[2]:.3f}")
    print(f"  component_match: {coefficients[3]:.3f}")
    print(f"  bias: {bias:.3f}")
    print()
    
    df_temp = df.copy()
    df_temp['ml_probability'] = ml_probs
    df_temp['grade_match'] = [f['grade_match'] for f in feature_data]
    df_temp['unit_match'] = [f['unit_match'] for f in feature_data]
    df_temp['component_match'] = [f['component_match'] for f in feature_data]
    df_temp['semantic_score'] = [f['semantic_score'] for f in feature_data]
    df_sorted = df_temp.sort_values('ml_probability', ascending=False)
    
    print("[STEP 4: COST MAPPING]")
    print("-"*100)
    print("[OK] Analyzing top matches for cost mapping")
    print()
    
    print("[TOP 3 MATCHES]")
    print("="*100)
    
    for rank, row in enumerate(df_sorted.head(3).itertuples(), 1):
        prob = row.ml_probability
        
        cost_mapping = cost_mapper.calculate_mapped_cost(
            qto_quantity, qto_unit,
            row.rate, row.unit,
            qto_item, row.description
        )
        
        mapping_confidence, adjusted_prob = cost_mapper.get_mapping_confidence(
            prob, row.unit_match, cost_mapping['can_map']
        )
        
        print(f"\n[RANK {rank}]")
        print("-"*100)
        print(f"Cost Item: {row.description}")
        print(f"Rate: Rs.{row.rate}/{row.unit}")
        print()
        
        print(f"Feature Values:")
        print(f"   semantic_score = {row.semantic_score:.3f}")
        print(f"   grade_match = {row.grade_match}")
        print(f"   unit_match = {row.unit_match}")
        print(f"   component_match = {row.component_match}")
        print()
        
        z = (coefficients[0] * row.semantic_score + 
             coefficients[1] * row.grade_match + 
             coefficients[2] * row.unit_match + 
             coefficients[3] * row.component_match + 
             bias)
        
        print(f"ML Calculation:")
        print(f"   z = ({coefficients[0]:.2f} x {row.semantic_score:.3f}) + "
              f"({coefficients[1]:.2f} x {row.grade_match}) + "
              f"({coefficients[2]:.2f} x {row.unit_match}) + "
              f"({coefficients[3]:.2f} x {row.component_match}) + {bias:.2f}")
        print(f"   z = {z:.3f}")
        print(f"   probability = sigmoid({z:.3f}) = {prob:.3f}")
        print()
        
        print(f"Match Indicators:")
        print(f"   Grade: {'[YES]' if row.grade_match else '[NO]'} | "
              f"Unit: {'[YES]' if row.unit_match else '[NO]'} | "
              f"Component: {'[YES]' if row.component_match else '[NO]'}")
        print()
        
        print(f"Cost Mapping:")
        if cost_mapping['can_map']:
            print(f"   Status: [CAN MAP]")
            print(f"   Mapped Rate: Rs.{cost_mapping['mapped_rate']}/{qto_unit}")
            print(f"   Total Cost: Rs.{cost_mapping['mapped_total']:,.2f}")
            if cost_mapping['conversion_factor'] != 1.0:
                print(f"   Conversion Factor: {cost_mapping['conversion_factor']}")
            if cost_mapping['warning']:
                print(f"   WARNING: {cost_mapping['warning']}")
            print(f"   {cost_mapping['explanation']}")
        else:
            print(f"   Status: [CANNOT MAP]")
            print(f"   Reason: {cost_mapping['explanation']}")
        print()
        
        print(f"Confidence: {mapping_confidence}")
        bar_length = int(prob * 40)
        bar = "=" * bar_length
        print(f"   {bar} {prob:.3f}")
        print()
    
    print("="*100)
    print()


def main():
    print("\n")
    print("="*100)
    print("8TH LAYER: ML RANKING + COST MAPPING SYSTEM")
    print("="*100)
    print()
    
    print("\n[TEST CASE 1: UNIT MISMATCH - Steel Reinforcement]")
    process_qto_item(
        qto_item="Steel reinforcement Fe500 bars",
        qto_unit="m3",
        qto_quantity=2.5
    )
    
    print("\n[TEST CASE 2: PERFECT MATCH - RCC Slab]")
    process_qto_item(
        qto_item="RCC slab M25 150mm thick",
        qto_unit="m3",
        qto_quantity=50.0
    )
    
    print("\n" + "="*100)
    print("[ALL TEST CASES COMPLETED]")
    print("="*100)
    print()


if __name__ == "__main__":
    main()
