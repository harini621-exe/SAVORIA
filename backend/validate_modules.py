"""Validate all backend modules."""
import sys
sys.path.insert(0, '.')
errors = []

# Ingredient analyzer
try:
    from app.agents.ingredient_analyzer import IngredientAnalyzer
    a = IngredientAnalyzer()
    r = a.process(['garlic', 'pasta', 'olive oil', 'tomato'])
    assert r['unique_count'] == 4
    valid, _ = a.validate(['garlic'])
    assert valid
    invalid, _ = a.validate([])
    assert not invalid
    print('IngredientAnalyzer: PASS')
except Exception as e:
    errors.append(f'IngredientAnalyzer: FAIL - {e}')

# Preference analyzer
try:
    from app.agents.preference_analyzer import PreferenceAnalyzer
    p = PreferenceAnalyzer()
    prefs = p.process('veg', 'italian', 'dinner', 30, 2, ['peanuts'])
    assert prefs['dietary_preference'] == 'vegetarian'
    assert prefs['cuisine_preference'] == 'Italian'
    print('PreferenceAnalyzer: PASS')
except Exception as e:
    errors.append(f'PreferenceAnalyzer: FAIL - {e}')

# Substitution advisor
try:
    from app.agents.substitution_advisor import SubstitutionAdvisor
    sub = SubstitutionAdvisor()
    subs = sub.get_substitutions('butter')
    assert len(subs) > 0
    print('SubstitutionAdvisor: PASS')
except Exception as e:
    errors.append(f'SubstitutionAdvisor: FAIL - {e}')

# Dietary adapter
try:
    from app.agents.dietary_adapter import DietaryAdapter
    da = DietaryAdapter()
    adapt = da.get_adaptation('vegan')
    assert 'eggs' in adapt['avoid_ingredients']
    prompt = da.build_adaptation_prompt('vegan')
    assert 'vegan' in prompt.lower() or 'VEGAN' in prompt
    print('DietaryAdapter: PASS')
except Exception as e:
    errors.append(f'DietaryAdapter: FAIL - {e}')

# Config
try:
    from app.config import get_settings
    s = get_settings()
    assert s.IBM_PROJECT_ID
    print(f'Config: PASS (project={s.IBM_PROJECT_ID[:8]}...)')
except Exception as e:
    errors.append(f'Config: FAIL - {e}')

# Watsonx client
try:
    from app.utils.watsonx_client import WatsonxClient
    client = WatsonxClient()
    assert client.is_configured()
    print('WatsonxClient: PASS (configured)')
except Exception as e:
    errors.append(f'WatsonxClient: FAIL - {e}')

# FastAPI app
try:
    from app.main import app
    print('FastAPI App: PASS')
except Exception as e:
    errors.append(f'FastAPI App: FAIL - {e}')

print()
if errors:
    for e in errors:
        print(f'  ERROR: {e}')
    sys.exit(1)
else:
    print('=== ALL MODULE TESTS PASSED ===')
