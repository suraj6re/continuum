import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

model = SentenceTransformer("all-MiniLM-L6-v2")
reranker = joblib.load('ml_reranker/model.pkl')

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

qto_item = "RCC slab M25 150mm thick"
qto_unit = "m3"

query_embedding = model.encode([qto_item])
scores = cosine_similarity(query_embedding, cost_embeddings)[0]

feature_data = []
for idx, row in df.iterrows():
    feature_data.append({
        "semantic_score": scores[idx],
        "grade_match": grade_match(qto_item, row["description"]),
        "unit_match": unit_match(qto_unit, row["unit"]),
        "component_match": component_match(qto_item.lower(), row["description"].lower())
    })

features_df = pd.DataFrame(feature_data)
ml_probs = reranker.predict_proba(features_df)[:, 1]
df['ml_probability'] = ml_probs
df['grade_match'] = [f['grade_match'] for f in feature_data]
df['unit_match'] = [f['unit_match'] for f in feature_data]
df['component_match'] = [f['component_match'] for f in feature_data]
df['semantic_score'] = [f['semantic_score'] for f in feature_data]
df_sorted = df.sort_values('ml_probability', ascending=False)

print(f"Query: '{qto_item}'\n")
print("Top 3 matches (ML reranked):\n")

for i, row in enumerate(df_sorted.head(3).itertuples(), 1):
    prob = row.ml_probability
    
    if prob > 0.6:
        confidence = "High"
    elif prob > 0.4:
        confidence = "Medium"
    else:
        confidence = "Low"
    
    bar_length = int(prob * 20)
    bar = "█" * bar_length
    
    print(f"{i}. {row.description}")
    print(f"   Unit: {row.unit} | Rate: Rs.{row.rate}")
    print(f"   {bar} {prob:.3f} ({confidence} Confidence)")
    print(f"   Matched: Grade={'✓' if row.grade_match else '✗'} | Unit={'✓' if row.unit_match else '✗'} | Component={'✓' if row.component_match else '✗'} | Semantic={row.semantic_score:.2f}")
    print()
