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

    def keep_led_on(self):
        while True:
            try:
                self.board.digital[self.pin].write(1)
                self.board.digital[self.pin2].write(1)

                #lets the motors be alive at the same time
                self.board.digital[self.relay_pin].write(1)

                self.light = True
                time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
                break

    def stop(self):
        self.board.digital[self.pin].write(0)
        self.board.digital[self.pin2].write(0)
        self.board.digital[self.relay_pin].write(0)
        self.board.exit()
        sys.exit(0)

# Example usage:
if __name__ == "__main__":
    arduino = ArduinoController('COM3', 8, 7,2)
    arduino.keep_led_on()
