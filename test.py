import requests
import json

url = f'http://192.168.100.42/api/generate'

data = json.dumps({
            "model": "tinyllama",
            "prompt": "Hi how ya doing",
            "stream": False
        })

r = requests.post(url, data=data, timeout=10)

print(r.text)