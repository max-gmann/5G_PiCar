import requests, time

pi_url = "http://192.168.0.168:8000/run/"

cam_left = {"action": "camleft"}
cam_right = {"action": "camright"}
cam_camready = {"action": "cam_camready"}


for i in range(2):
    requests.get(pi_url, cam_left)
    time.sleep(1)
for i in range(4):
    requests.get(pi_url, cam_right)
    time.sleep(1)

requests.get(pi_url, cam_camready)
