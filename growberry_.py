#!/usr/bin/env python
"""
#####################################################################
#   code developed by: austinmeier                                  #
#   developed on: 04/10/2016                                        #
#   contact:austinmeier on github                                   #
#####################################################################
"""

###########################  Imports here  ##########################


# from datetime import datetime, time
import os
import datetime
from threading import Thread
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
from picamera import PiCamera

#####################################################################
#                           Parameters
#####################################################################
# Change these things to change how the threasholds work

# Read interval
measurement_interval = 10.00

# LIGHTS ON TIME
lights_on_time = 11.00

# LIGHTS OFF TIME
lights_off_time = 23.00

# TEMP that activates fans
fan_temp = 24.0

# toggle picture capture on/off
toggle_camera = True

# file to write the log file to
logfile = '/home/pi/usbdrv/growberry_testlog/grow1_log.txt'

# directory to save pictures in
pic_dir = '/home/pi/usbdrv/growberry_testlog/pictures/'

#####################################################################
#                           GPIO pin set up
#####################################################################
# select one of these two modes:
GPIO.setmode(GPIO.BCM)  # for using the names of the pins
# or
# GPIO.setmode(GPIO.BOARD)   #for true pin number IDs (pin1 = 1)

#GPIO.cleanup()  # shouldn't need to use this, but just in case.  Should be done at the end

GPIO.setwarnings(True)  # set to false if the warnings bother you, helps troubleshooting

############################ Activating pins ########################
# GPIO.setup(<put pin number here>,GPIO.IN/OUT)  #will depend on setmode above, use "IN" for sensors, and "OUT" for LEDs

GPIO.setup(12, GPIO.OUT, initial=1)
GPIO.setup(19, GPIO.OUT, initial=1)

#####################################################################
#                           Classes
#####################################################################
class bcolors:  # these are the color codes
    """
    Toggle switch for printing in color. Once activated, everything following is in color X

    This color class is completely unecessary, but it makes the output cooler, and doesn't really cause any harm
    if you remove it, you'll have to remove all uses of it in the functions
                        example:
    print(bcolors.YELLOW + "Warning" + bcolors.END)
    this prints "Warning" in yellow, then turns off colors, so everything printed after END will be normal
    """

    PURPLE = '\033[95m'  # purple
    BLUE = '\033[94m'  # blue
    GREEN = '\033[92m'  # green
    YELLOW = '\033[93m'  # yellow
    RED = '\033[91m'  # red
    END = '\033[0m'  # turns off color
    BOLD = '\033[1m'  # turns on bold

    def disable(self):
        self.PURPLE = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.END = ''
        self.BOLD = ''


class LED:
    """
    Turns GPIO pins from LOW(off) to HIGH(on) and back again

    this class pretty much works for any device connected to a single GPIO pin
    as instances of LED are created, their names are added as keys in the LED.dictionary
    """
    dictionary = {}  # a dictionary will all created LED instances' names as keys

    # state = None
    def __init__(self, pin, name, color, power):
        self.pin = int(pin)  # this is the GPIO pin number (will depend on GPIO config)
        self.name = name
        self.color = color
        self.power = power  # enter power in miliamps
        self.state = GPIO.input(self.pin)  # was going to use conditional loop if I could have got backgrounding to work
        LED.dictionary[name] = self  # auto adds every instance of LED to the dictionary

    def getstate(self):
        self.state = GPIO.input(self.pin)
        return self.state

    def fake(self):
        if GPIO.output(self.pin):  # if self.pin == 1
            print "%s on port %s is 1/GPIO.HIGH/True" % (self.name, self.pin)
        else:
            print "%s on port %s is 0/GPIO.LOW/False" % (self.name, self.pin)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        print("%s LED is" % self.color + bcolors.BOLD + bcolors.GREEN + " on." + bcolors.END)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
        print("%s LED is" % self.color + bcolors.BOLD + bcolors.RED + " off." + bcolors.END)

    def blink(self, *args):
        # print (len(args))          #troubleshooting print statement
        # print args                 # another
        try:
            repeat = int(args[0])
        except:
            repeat = 1
        try:
            speed = (float(args[1])) / 2
        except:
            speed = .5
        # print repeat               #troubleshooting print statement
        # print speed                # another
        print("%s LED is" % self.color + bcolors.BOLD + bcolors.PURPLE + " blinking." + bcolors.END)
        while repeat > 0:
            self.state = "blinking"
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(speed)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(speed)
            repeat -= 1


class Relay:
    """
    Turns GPIO pins from LOW(off) to HIGH(on) and back again

    this class pretty much works for any device connected to a single GPIO pin
    as instances of Relays are created, their names are added as keys in the Relay.dictionary
    """
    dictionary = {}  # a dictionary will all created LED instances' names as keys

    # state = None
    def __init__(self, pin, name):
        self.pin = int(pin)  # this is the GPIO pin number (will depend on GPIO config)
        self.name = name
        self.state = GPIO.input(self.pin)  # was going to use conditional loop if I could have got backgrounding to work
        LED.dictionary[name] = self  # auto adds every instance of LED to the dictionary

    def getstate(self):
        self.state = GPIO.input(self.pin)
        return self.state

    def fake(self):
        if GPIO.output(self.pin):  # if self.pin == 1
            print "%s on port %s is 1/GPIO.HIGH/True" % (self.name, self.pin)
        else:
            print "%s on port %s is 0/GPIO.LOW/False" % (self.name, self.pin)

    def on(self):
        """
        switches GPIO pin to LOW/0 - in open state relays, this turns the relay ON.
        """
        GPIO.output(self.pin, GPIO.LOW)
        #print("%s Relay is" % self.name + bcolors.BOLD + bcolors.GREEN + " on." + bcolors.END)

    def off(self):
        """
        switches GPIO pin to HIGH/1 - in open state relays, this turns the relay OFF.
        """
        GPIO.output(self.pin, GPIO.HIGH)
        #print("%s Relay is" % self.name + bcolors.BOLD + bcolors.RED + " off." + bcolors.END)

    def blink(self, *args):
        # print (len(args))          #troubleshooting print statement
        # print args                 # another
        try:
            repeat = int(args[0])
        except:
            repeat = 1
        try:
            speed = (float(args[1])) / 2
        except:
            speed = .5
        # print repeat               #troubleshooting print statement
        # print speed                # another
        print("%s Relay is" % self.name + bcolors.BOLD + bcolors.PURPLE + " blinking." + bcolors.END)
        while repeat > 0:
            self.state = "blinking"
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(speed)
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(speed)
            repeat -= 1


class Sensor:
    def __init__(self, pin, sens_type, name):
        self.sens_type = sens_type
        self.pin = int(pin)  # this is the GPIO pin number (will depend on GPIO config)$
        self.name = name  #

    def read(self):
        humidity, temp = Adafruit_DHT.read(self.sens_type, self.pin)

        #print 'Temperature: {0:0.1f} C'.format(temp)
        #print 'Humidity:    {0:0.1f} %'.format(humidity)

        #print temp
        #print humidity

        # Skip to the next reading if a valid measurement couldn't be taken.$
        # This might happen if the CPU is under a lot of load and the sensor$
        # can't be reliably read (timing is critical to read the sensor).$

        if humidity is None or temp is None:
            time.sleep(2)
            humidity, temp = Adafruit_DHT.read(self.sens_type, self.pin)
        return {"temp": round(temp,1), "humidity": round(humidity,1), "timestamp": datetime.datetime.now()}


############### Define things controlled vi Pi #####################

LIGHTS = Relay(12, "lights")

FANS = Relay(19, "fans")

#H2O_PUMP = Relay(set up a pin for this, "water pump")

sensor1 = Sensor(17, Adafruit_DHT.DHT22, "temp_humidity")

camera = PiCamera()

#####################################################################
#                           FUNCTIONS
#####################################################################
# worksheet.append_row((datetime.datetime.now(),time.strftime('%m/%d/%Y'),time.strftime("%H:%M:%S"), temp, humidity))$

def takepic(save_dir):
    timestamp = time.strftime("%Y-%m-%d.%H%M")
    camera.capture('%s%s.jpg'%(save_dir, timestamp))

def watercycle(pumptime):
    H2O_PUMP.on()
    time.sleep(pumptime*60)
    H2O_PUMP.off()
    last_water = datetime.datetime.now()



def growmonitor(interval, set_temp, lights_on, lights_off):
    """
    Every interval minutes, read the temp/humidity, if temp exceeds set_temp, turn on fans, 
    if time falls between set_time1 and set_time2: turn light on
    """
    #break float input date into python time object
    on_hour = int(str(lights_on).split(".")[0])
    on_min = int(str(lights_on).split(".")[1])

    off_hour = int(str(lights_off).split(".")[0])
    off_min = int(str(lights_off).split(".")[1])
    last_water = None
    fan_status = None
    light_status = None
    while True:
        #take picture and write it to the pic directory
        if toggle_camera:
            takepic(pic_dir)
        # read the sensor, check temp, turn fans on/off
        sensor_reading = sensor1.read()  # returns a dictionary with "temp", "humidity", and "timestamp" keys
        if sensor_reading["temp"] > float(set_temp):
            fan_status = "Fans:ON"
            FANS.on()
        else:
            fan_status = "Fans:OFF"
            FANS.off()
        # check if the time in within the set_times
        ontime = datetime.time(on_hour, on_min)
        offtime = datetime.time(off_hour, off_min)
        now = datetime.datetime.now()
        if ontime <= now.time() <= offtime:
            light_status = "Lights:ON"
            LIGHTS.on()
        else:
            light_status = "Lights:OFF"
            LIGHTS.off()

        data_line = (str(sensor_reading["timestamp"])+'\t'+ str(time.strftime("%Y-%m-%d.%H%M")) +'\t'+ str(sensor_reading["temp"]) +'\t'+ str(sensor_reading["humidity"]) +'\t'+ light_status +'\t'+ fan_status + '\n')

        print_light_status = None
        if light_status.split(':')[1]== "ON":
            print_light_status = "Lights:"+ bcolors.GREEN + 'ON' +bcolors.END
        elif light_status.split(':')[1]== "OFF":
            print_light_status = "Lights:"+ bcolors.RED + 'OFF' +bcolors.END

        print_fan_status = None
        if fan_status.split(':')[1]== "ON":
            print_fan_status = "Fans:"+ bcolors.GREEN + 'ON' +bcolors.END
        elif fan_status.split(':')[1]== "OFF":
            print_fan_status = "Fans:"+ bcolors.RED + 'OFF' +bcolors.END

        print(str(sensor_reading["timestamp"])+'\t'+ str(time.strftime("%Y-%m-%d.%H%M")) +'\t'+ str(sensor_reading["temp"]) +'\t'+ str(sensor_reading["humidity"]) +'\t'+ print_light_status +'\t'+ print_fan_status)

        with open(logfile, "a") as data_log:
            data_log.write(data_line)

        time.sleep(interval * 60)


def main():
    print('\n\n\n\n\n')

    print(bcolors.RED + bcolors.BOLD +
        '  ________                    ___.                                                 \n'+\
        ' /  _____/______  ______  _  _\_ |__   __________________ ___.__.    ______ ___.__.\n'+bcolors.YELLOW +\
        '/   \  __\_  __ \/  _ \ \/ \/ /| __ \_/ __ \_  __ \_  __ <   |  |    \____ <   |  |\n'+\
        '\    \_\  \  | \(  <_> )     / | \_\ \  ___/|  | \/|  | \/\___  |    |  |_> >___  |\n'+bcolors.GREEN +\
        ' \______  /__|   \____/ \/\_/  |___  /\___  >__|   |__|   / ____| /\ |   __// ____|\n'+\
        '        \/                         \/     \/              \/      \/ |__|   \/     \n'+bcolors.END)

    growmonitor(measurement_interval, fan_temp, lights_on_time, lights_off_time)


########################  activityentered_code()  ###########################

def activitycode(choices):
    """
    In manual mode, you can enter a string, split into arguments at each space.
    Each argument is checked against the list of possible choices, and if the argument is in the list,
    the argument immediately following will dictate the behavior
    """
    entered_code = [str(x) for x in
                    raw_input('\n[--system--] enter code for relay behavior: Relay name on/off/blink..\n>>>').split()]
    for argument in entered_code:
        if argument in choices:
            behavior_choice_index = entered_code.index(argument) + 1
            # print(argument, entered_code[behavior_choice_index])
            if entered_code[behavior_choice_index] == "on":
                choices[argument].on()
            elif entered_code[behavior_choice_index] == "off":
                choices[argument].off()
            elif entered_code[behavior_choice_index] == "blink":
                try:
                    blinkrepeat = entered_code[behavior_choice_index + 1]
                except:
                    blinkrepeat = None
                try:
                    blinkspeed = entered_code[behavior_choice_index + 2]
                except:
                    blinkspeed = None
                # background the call of LED.blink
                b1 = Thread(target=choices[argument].blink, args=(blinkrepeat, blinkspeed))
                # choices[argument].blink(blinkrepeat,blinkspeed)
                b1.start()
        elif argument == "exit":
            return False


##############################################################################
#                       Executable code below:
##############################################################################

try:
    main()
except KeyboardInterrupt:
    print "Goodbye!"
    GPIO.cleanup()
finally:
    GPIO.cleanup()
