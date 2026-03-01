import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("../cost_book_demo.csv")
model = SentenceTransformer("all-MiniLM-L6-v2")

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

qto_samples = [
    # Concrete
    ("RCC slab M25 150mm thick", "m3", 1),
    ("RCC slab M20 120mm thick", "m3", 2),
    ("Concrete column M30 grade", "m3", 4),
    ("Lean concrete M10 leveling", "m3", 5),

    # Steel
    ("Steel reinforcement Fe500 bars", "kg", 6),
    ("Steel reinforcement Fe415 bars", "kg", 7),
    ("Structural steel sections fabrication", "kg", 8),
    ("TMT bars 12mm diameter", "kg", 9),
    ("MS plates and angles structural work", "kg", 10),

    # Masonry
    ("Brick masonry in cement mortar 1:6", "m3", 11),
    ("Brick masonry in cement mortar 1:4", "m3", 12),
    ("Hollow concrete block masonry", "m3", 13),
    ("Stone masonry work", "m3", 14),
    ("AAC block masonry wall", "m3", 15),

    # Finishing
    ("Cement plaster 12mm thick walls", "m2", 16),
    ("Gypsum plaster 12mm thick finish", "m2", 17),
    ("Ceramic floor tiles 600x600 flooring", "m2", 18),
    ("Vitrified tiles 600x600 flooring", "m2", 19),
    ("Painting on walls two coats", "m2", 20),

    # Earthwork
    ("Excavation in ordinary soil foundation", "m3", 21),
    ("Excavation in hard soil foundation", "m3", 22),
    ("Earth filling and compaction work", "m3", 23),

    # Formwork
    ("Centering and shuttering for slab", "m2", 24),
    ("Centering and shuttering for beam", "m2", 25),
]

training_rows = []
cost_embeddings = model.encode(df["description"].tolist())

for qto_text, qto_unit, correct_id in qto_samples:
    qto_embedding = model.encode([qto_text])
    similarities = cosine_similarity(qto_embedding, cost_embeddings)[0]

    for idx, row in df.iterrows():
        label = 1 if row["id"] == correct_id else 0
        
        training_rows.append({
            "semantic_score": similarities[idx],
            "grade_match": grade_match(qto_text, row["description"]),
            "unit_match": unit_match(qto_unit, row["unit"]),
            "component_match": component_match(qto_text.lower(), row["description"].lower()),
            "label": label
        })

train_df = pd.DataFrame(training_rows)
train_df.to_csv("training_data.csv", index=False)
print(f"Training data generated: {len(train_df)} samples")
