import requests
import json

url = "http://localhost:8000/align_cost"
payload = {
    "description": "RCC slab M25 150mm thick",
    "unit": "m3",
    "top_k": 3
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
