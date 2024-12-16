import requests

res = requests.get("http://192.168.88.245:5555/api/v1/getcontent?url=https://website.site")

print(res.text)
