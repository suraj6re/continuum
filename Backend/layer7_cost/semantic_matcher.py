import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model
print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Model loaded\n")

# Load CSV
df = pd.read_csv('cost_book_demo.csv')
print(f"✅ Loaded {len(df)} items from cost book\n")

# Encode all descriptions once
print("Encoding descriptions...")
desc_embeddings = model.encode(df['description'].tolist())
print("✅ Descriptions encoded\n")

# Test with mock QTO
qto_item = "RCC slab M25 150mm thick"
print(f"🔍 Testing with: '{qto_item}'\n")

# Encode query and calculate similarity
query_embedding = model.encode([qto_item])
scores = cosine_similarity(query_embedding, desc_embeddings)[0]
df['score'] = scores
df_sorted = df.sort_values('score', ascending=False)

print("📊 Top 3 matches:\n")
for i, row in enumerate(df_sorted.head(3).itertuples(), 1):
    print(f"{i}. {row.description}")
    print(f"   Unit: {row.unit} | Rate: ₹{row.rate}")
    print(f"   Score: {row.score:.2f}\n")
