from time import sleep
import  time
from Pi_Car_Controls import pi_car

car = pi_car(default_speed=30)

#with pi_car(default_speed=30) as car:

car.ready()
car.turn(-10)
time.sleep(2)
car.straight()
