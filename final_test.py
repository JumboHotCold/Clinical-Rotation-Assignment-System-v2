import requests

res = requests.post('http://127.0.0.1:8001/auth/token', json={'username': 'admin', 'password': 'admin123'})
token = res.json().get('access_token')
print("Token HTTP code:", res.status_code)

res2 = requests.delete('http://127.0.0.1:8001/students/1', headers={'Authorization': f'Bearer {token}'})
print("Delete HTTP code:", res2.status_code)
print("Response:", res2.text)

res3 = requests.delete('http://127.0.0.1:8001/areas/1', headers={'Authorization': f'Bearer {token}'})
print("Delete Area HTTP code:", res3.status_code)
print("Response:", res3.text)

