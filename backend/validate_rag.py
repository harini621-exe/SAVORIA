"""Quick RAG validation script."""
import sys
sys.path.insert(0, 'backend')
from app.rag.retriever import RecipeRAG

rag = RecipeRAG(data_dir='backend/data')
rag.build_index()
results = rag.retrieve(['garlic', 'pasta', 'olive oil', 'tomato'], top_k=3)
print(f'RAG retrieval OK: {len(results)} results')
for r in results:
    print(f"  - {r['name']} (match: {r['_match_ratio']:.2f})")
print('PASS')
