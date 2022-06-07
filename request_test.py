import requests

pi_url = "http://192.168.178.156:8000/run/"
data = {"action": "stop"}

for i in range(4):
    requests.get(pi_url, data)