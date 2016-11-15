import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  # for using the names of the pins


class Wind:
    """This will house all of functions used to control the fans"""
    def __init__(self, powerpin, speedpin, speed = 0):  # add lights, if need be
        self.powerpin = powerpin
        GPIO.setup(powerpin, GPIO.OUT, initial=1)
        GPIO.setup(speedpin, GPIO.OUT)
        self.pwm = GPIO.PWM(speedpin, 25000) # 25 Kilohertz is inaudible to human ears
        self._speed = speed
        self.pwm.start(speed)
#        self.lights = lights

    @property
    def speed(self):
        # handles the speed of the fans, including master power, on/off.
        return self._speed

    @speed.setter
    # fans need power to have a speed
    def speed(self, value):
        if 0 < value <= 100:
            self._speed = value
            self.pwm.ChangeDutyCycle(value)
            # GPIO.output(self.powerpin, GPIO.LOW) # power on
            self.on()
            print "ON"
        elif value == 0:
            self.off()
            print "OFF"
            # GPIO.output(self.powerpin, GPIO.HIGH)  # power off
            # if self.lights.state:  #lights.state = 1 means lights are off
            #     GPIO.output(self.powerpin, GPIO.HIGH)  # power off
            # else:
            #     raise ValueError("cannot set speed to 0 when lights are on")
        else:
            raise ValueError("Speed must be between 0-100")

    def on(self):
        """switches GPIO pin to LOW/0 - in open state relays, this turns the relay ON."""
        GPIO.output(self.pin, GPIO.LOW)


    def off(self):
        """ switches GPIO pin to HIGH/1 - in open state relays, this turns the relay OFF."""
        GPIO.output(self.pin, GPIO.HIGH)


if __name__ == "__main__":
    wind = Wind(19,18)

    try:
        while True:
            inputspeed = input("Enter fan speed(0.0-100.0): ")
            print inputspeed
            print type(inputspeed)
            try:
                wind.speed = inputspeed
                # new_duty = 100.0 - speed
                # wind.pwm.ChangeDutyCycle(new_duty)
            except ValueError:
                print "invalid set speed"
            except:
                break
                print "broken"
            else:
                print("New duty cycle = ", inputspeed)

    finally:
        wind.pwm.stop()
        GPIO.cleanup()
        print('PWM stopped, GPIO pins have been cleaned up. Goodbye.')
