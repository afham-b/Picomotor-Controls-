#this script awakens the newport controller box if it's not on already, if its is already on,
#then this script effectively provides a restart


import sys
import pyfirmata
import time

class ArduinoController:
    def __init__(self, port, pin1, pin2, relay_pin=2,):
        self.board = pyfirmata.Arduino(port)
        self.pin = pin1
        self.pin2 = pin2
        self.relay_pin = relay_pin
        time.sleep(2)  # Allow time for the board to initialize

        # default is to start with the light on and relay open
        self.board.digital[self.pin].write(1)
        self.board.digital[self.pin2].write(1)
        #self.board.digital[self.relay_pin].write(0)

        self.light = True  # light is true :. light is on

    def motors_on(self):
        self.board.digital[self.relay_pin].write(1)
        time.sleep(1)
        #self.board.digital[self.relay_pin].write(0)
        self.board.exit()
        sys.exit(0)

# Example usage:
if __name__ == "__main__":
    arduino = ArduinoController('COM3', 8, 7,2)
    arduino.motors_on()
