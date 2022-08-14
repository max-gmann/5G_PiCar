from time import sleep
import  time

from requests import request
from Pi_Car_Controls import pi_car
import logging, requests
from multiprocessing.dummy import Pool
import asyncio
import urllib.request

logging.basicConfig(format='[%(asctime)s | %(module)s | %(levelname)s] - %(message)s', level=logging.INFO)

base_url = "http://raspberrypi"
control_url = base_url + ":8000/run/"

loop = asyncio.get_event_loop()
session = requests.Session()
pool = Pool(1)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}


with pi_car(default_speed=30) as car:
    while True:
        input("go?")
        t1 = time.time()
        
        pool.apply_async(requests.get, [car.control_url, {"action": "forward"}])

        t2 = time.time()
        print(t2-t1)

        input("stop?")
        t1 = time.time()

        # requests.get(control_url, {"action": "stop"})
        pool.apply_async(requests.get, [car.control_url, {"action": "stop"}])

        t2 = time.time()
        print(t2-t1)