import urllib.parse

# https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id=<Your-API-Key-Here>&redirect_uri=<Your-Redirect-URI-Here>&state=<Your-Optional-State-Parameter-Here>
# Login to upstox and get "code"

url = "https://127.0.0.1:7000/"
rurl = urllib.parse.quote(url, safe='')


# Get Access token
import requests

url = 'https://api.upstox.com/v2/login/authorization/token'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'code': '{your_code}',
    'client_id': '{your_client_id}',
    'client_secret': '{your_client_secret}',
    'redirect_uri': '{your_redirect_url}',
    'grant_type': 'authorization_code',
}

response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.json())
