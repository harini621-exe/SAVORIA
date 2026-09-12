"""Test full recipe generation pipeline via API."""
import sys
sys.path.insert(0, '.')
import asyncio

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
errors = []

# Test full recipe generation
try:
    print('Testing recipe generation (this will call watsonx.ai or use RAG fallback)...')
    r = client.post('/api/recipes/generate', json={
        'available_ingredients': ['garlic', 'pasta', 'olive oil', 'tomato', 'basil'],
        'servings': 2,
        'meal_type': 'dinner',
    }, timeout=90)
    assert r.status_code == 200, f"Status {r.status_code}: {r.text[:200]}"
    data = r.json()
    assert len(data['recipes']) > 0
    recipe = data['recipes'][0]
    print(f'Recipe generation: PASS')
    print(f'  - Query: {data["query_summary"]}')
    print(f'  - Got {len(data["recipes"])} recipes, first: {recipe["name"]}')
    print(f'  - RAG context: {data["retrieved_context_count"]} recipes retrieved')
    first_recipe_id = recipe['id']
except Exception as e:
    errors.append(f'Recipe generation: FAIL - {e}')
    first_recipe_id = 'r001'

# Test list recipes
try:
    r = client.get('/api/recipes?limit=5')
    assert r.status_code == 200
    data = r.json()
    assert len(data['recipes']) > 0
    print(f'List recipes: PASS ({data["total"]} total)')
except Exception as e:
    errors.append(f'List recipes: FAIL - {e}')

# Test list recipes with filter
try:
    r = client.get('/api/recipes?meal_type=breakfast')
    assert r.status_code == 200
    data = r.json()
    for rec in data['recipes']:
        assert rec['meal_type'] == 'breakfast'
    print(f'List recipes (filtered): PASS ({len(data["recipes"])} breakfast recipes)')
except Exception as e:
    errors.append(f'List recipes filtered: FAIL - {e}')

# Test get recipe detail
try:
    r = client.get('/api/recipes/r001?ingredients=garlic,spaghetti,olive oil')
    assert r.status_code == 200
    data = r.json()
    assert data['recipe']['id'] == 'r001'
    assert len(data['recipe']['steps']) > 0
    avail = [i for i in data['recipe']['ingredients'] if i['available']]
    print(f'Recipe detail: PASS ({len(avail)} ingredients marked available)')
except Exception as e:
    errors.append(f'Recipe detail: FAIL - {e}')

# Test recipe with vegan preference
try:
    r = client.post('/api/recipes/generate', json={
        'available_ingredients': ['lentils', 'onion', 'garlic', 'tomato', 'cumin'],
        'dietary_preference': 'vegan',
        'meal_type': 'dinner',
        'servings': 3,
    }, timeout=90)
    assert r.status_code == 200
    data = r.json()
    assert len(data['recipes']) > 0
    print(f'Vegan recipe generation: PASS ({len(data["recipes"])} recipes)')
except Exception as e:
    errors.append(f'Vegan generation: FAIL - {e}')

# Test ingredient substitution with available ingredients
try:
    r = client.post('/api/substitutions', json={
        'ingredient': 'eggs',
        'available_ingredients': ['banana', 'flaxseed'],
    })
    assert r.status_code == 200
    data = r.json()
    print(f'Substitution (eggs): PASS ({len(data["substitutions"])} alternatives)')
except Exception as e:
    errors.append(f'Substitution: FAIL - {e}')

print()
if errors:
    for e in errors:
        print(f'  ERROR: {e}')
    sys.exit(1)
else:
    print('=== ALL FULL PIPELINE TESTS PASSED ===')
