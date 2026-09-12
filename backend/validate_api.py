"""Test API endpoints using TestClient (no model download needed for non-RAG tests)."""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
errors = []

# Health check
try:
    r = client.get('/api/health')
    assert r.status_code == 200
    data = r.json()
    assert data['status'] == 'ok'
    print(f'Health check: PASS (watsonx_configured={data["watsonx_configured"]})')
except Exception as e:
    errors.append(f'Health: FAIL - {e}')

# Root
try:
    r = client.get('/')
    assert r.status_code == 200
    assert 'SAVORIA' in r.json()['name']
    print('Root: PASS')
except Exception as e:
    errors.append(f'Root: FAIL - {e}')

# Generate recipes — empty input
try:
    r = client.post('/api/recipes/generate', json={'available_ingredients': []})
    assert r.status_code in (400, 422)
    print(f'Generate (empty input): PASS (status={r.status_code})')
except Exception as e:
    errors.append(f'Generate empty: FAIL - {e}')

# Substitutions
try:
    r = client.post('/api/substitutions', json={'ingredient': 'butter'})
    assert r.status_code == 200
    data = r.json()
    assert data['ingredient'] == 'butter'
    assert len(data['substitutions']) > 0
    print(f'Substitutions: PASS ({len(data["substitutions"])} subs for butter)')
except Exception as e:
    errors.append(f'Substitutions: FAIL - {e}')

# Ingredient analysis
try:
    r = client.post('/api/ingredients/analyse', json=['garlic', 'onion', 'tomato'])
    assert r.status_code == 200
    data = r.json()
    assert 'normalised' in data
    print('Ingredient analysis: PASS')
except Exception as e:
    errors.append(f'Ingredient analysis: FAIL - {e}')

# Recipe not found
try:
    r = client.get('/api/recipes/nonexistent_xyz_999')
    assert r.status_code == 404
    print('Recipe not found: PASS (404 returned)')
except Exception as e:
    errors.append(f'Recipe not found: FAIL - {e}')

print()
if errors:
    for e in errors:
        print(f'  ERROR: {e}')
    sys.exit(1)
else:
    print('=== ALL API ENDPOINT TESTS PASSED ===')
