import board
import digitalio
import time
import serial

'''
It will recognize and transfer quick push after 0.2 seconds
and will recognize and transfer long push after 1.5 seconds

NOTICE - if you change the init time constants it will change the response time!!
'''

class push_button():
    def __init__(self):
        self.button = digitalio.DigitalInOut(board.C0)  # Defining GPIO C0 as a button
        self.button.direction = digitalio.Direction.INPUT  # Defining C0 as an input
        self.processor_burdon_time = 0.1
        self.considerated_debounce_time = 1
        self.ser = serial.Serial(port='/dev/fpga_tx',baudrate=115200)
        try:
            self.ser.open()
        except serial.SerialException:
            print("port already open")
        self.command = "not L15<9?"
        push_button.main(self)


    def read_response(self):
        while (True):
            if self.ser.inWaiting()>0:
                break
        data = ""
        data+=self.ser.read().decode()
        return data


    def LEDs_writer(self):
        try:
            self.ser.write(self.command.encode())
        except KeyboardInterrupt:
            push_button.exit_LEDs(self)


    def push_manager(self):
        self.command = "L18<9?"
        push_button.LEDs_writer(self)
        time.sleep(0.1)
        for i in range(10):
            time.sleep(0.1)
            if self.button.value:
                push_button.main(self)
        self.command = "L13<9?"
        push_button.LEDs_writer(self)
        time.sleep(self.considerated_debounce_time)
        push_button.main(self)


    def exit_LEDs(self):
        self.command = "L1_01?"
        self.ser.write(self.command.encode())
        print("\nkeyboard interupt.... exiting")
        exit()


    def main(self):
        try:
            while True:
                if not self.button.value:
                    push_button.push_manager(self)
                elif not self.command == "L15<9?":
                    self.command = "L15<9?"
                    push_button.LEDs_writer(self)
                time.sleep(self.processor_burdon_time)
        except KeyboardInterrupt:
            push_button.exit_LEDs(self)


push_button()

