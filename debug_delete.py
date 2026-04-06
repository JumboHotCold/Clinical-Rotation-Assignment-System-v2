import requests

try:
    token_res = requests.post('http://127.0.0.1:8002/auth/token', data={'username': 'admin', 'password': 'admin123'})
    token_res.raise_for_status()
    token = token_res.json()['access_token']
    
    res = requests.delete('http://127.0.0.1:8002/students/1', headers={'Authorization': f'Bearer {token}'})
    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)
except requests.exceptions.HTTPError as e:
    print("HTTPError:", e)
    print(e.response.text)
except Exception as e:
    print("Error:", e)
