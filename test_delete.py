import urllib.request
import urllib.parse
import json

try:
    data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode()
    req = urllib.request.Request('http://127.0.0.1:8002/auth/token', data=data)
    response = urllib.request.urlopen(req)
    token = json.loads(response.read())['access_token']

    delete_req = urllib.request.Request('http://127.0.0.1:8002/students/1', method='DELETE')
    delete_req.add_header('Authorization', 'Bearer ' + token)
    res = urllib.request.urlopen(delete_req)
    print("Success:", res.read().decode())
except Exception as e:
    print("Exception Occured")
    if hasattr(e, 'read'):
        print(e.read().decode())
    else:
        print(e)
