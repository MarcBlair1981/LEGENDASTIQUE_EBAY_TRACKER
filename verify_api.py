import requests
import json

try:
    print("Checking /api/items...")
    r = requests.get('http://localhost:5000/api/items')
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Item Count: {len(data.get('items', []))}")
    print(f"Data: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Failed: {e}")
