from __future__ import print_function
import time
import RPi.GPIO as GPIO
import os

def getTemp():
  tempStore = open("/sys/bus/w1/devices/28-021313a45aaa/w1_slave")
  data = tempStore.read()
  tempStore.close()
  tempData = data.split("\n")[1].split(" ")[9]
  temperature = float(tempData[2:])
  temperature = temperature / 1000
  
  return temperature

def measure():
  # This function measures a distance
  GPIO.output(GPIO_TRIGGER, True)
  # Wait 10us
  time.sleep(0.00001)
  GPIO.output(GPIO_TRIGGER, False)
  start = time.time()
  
  while GPIO.input(GPIO_ECHO)==0:
    start = time.time()

  while GPIO.input(GPIO_ECHO)==1:
    stop = time.time()

  speedSound = 33100 + (0.6*getTemp())
  elapsed = stop-start
  distance = (elapsed * speedSound)/2

  return distance

def measure_average():
  # This function takes 3 measurements and
  # returns the average.

  distance1=measure()
  time.sleep(0.1)
  distance2=measure()
  time.sleep(0.1)
  distance3=measure()
  distance = distance1 + distance2 + distance3
  distance = distance / 3
  return distance
  
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER = 23
GPIO_ECHO    = 24

GPIO.setwarnings(False)

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

# Allow module to settle
time.sleep(0.5)

try:
  distance = measure_average()
  distance = float("{0:5.1f}".format(distance))
  print(distance)
  gap = 15 - 5  # top of tank to run off valve + length of sensor
  distance = distance - gap
  print(distance)
  tank = 226 - 15 # height of tank minus gap
  
  full = (tank - distance) / tank * 100
  full = float("{0:5.1f}".format(full))
  #print(distance)
  print(str(full) + "% Full")
  temp = getTemp()
  temp = round(temp, 2)
  print(str(temp) + " degrees celsius in tank")
  os.system("mosquitto_pub -h 10.0.0.5 -t 'water_tank' -m " + str(full) + " -u '[SECRET]' -P '[SECRET]'")
  os.system("mosquitto_pub -h 10.0.0.5 -t 'water_tank/temp' -m " + str(temp) + " -u '[SECRET]' -P '[SECRET]'")

except KeyboardInterrupt:
  # User pressed CTRL-C
  # Reset GPIO settings
  GPIO.cleanup()
