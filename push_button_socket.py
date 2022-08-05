import board
import digitalio
import time
import serial
import asyncio
import websockets

'''
It will recognize and transfer quick push after 0.2 seconds
and will recognize and transfer long push after 1.5 seconds

NOTICE - if you change the init time constants it will change the response time!!
'''

class push_button():
    def __init__(self):
        self.button = digitalio.DigitalInOut(board.C0)
        self.button.direction = digitalio.Direction.INPUT
        self.processor_burdon_time = 0.1
        self.considerated_debounce_time = 1
        self.chest_basic_blue = "L15<9?"
        self.chest_green = "L18<9?"
        self.chest_red = "L13<9?"
        self.quick_long_timeloop = 0.1
        self.quick_long_loopnum = 10
        self.turnoff_LED = "L1_01?"
        self.ser = serial.Serial(port='/dev/fpga_tx',baudrate=115200)
        try:
            self.ser.open()
        except serial.SerialException:
            print("port already open")
        self.command = "not L15<9?"
        push_button.main(self)


    async def socket_msg(msg):
        async with websockets.connect("ws://0.0.0.0:8001/ws/pushbutton") as websocket:
            await websocket.send(msg)
            

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
        self.command = self.chest_green
        push_button.LEDs_writer(self)
        time.sleep(self.quick_long_timeloop)
        loop = asyncio.get_event_loop()
        for i in range(self.quick_long_loopnum):
            time.sleep(self.quick_long_timeloop)
            if self.button.value:
                msg = "quick press"
                loop.run_until_complete(push_button.socket_msg(msg))
                push_button.main(self)
        self.command = self.chest_red 
        push_button.LEDs_writer(self)
        msg = "long press"
        loop.run_until_complete(push_button.socket_msg(msg))
        time.sleep(self.considerated_debounce_time)
        push_button.main(self)


    def exit_LEDs(self):
        self.command = self.turnoff_LED
        self.ser.write(self.command.encode())
        print("\nkeyboard interupt.... exiting")
        exit()


    def main(self):
        try:
            while True:
                if not self.button.value:
                    push_button.push_manager(self)
                elif not self.command == self.chest_basic_blue:
                    self.command = self.chest_basic_blue
                    push_button.LEDs_writer(self)
                time.sleep(self.processor_burdon_time)
        except KeyboardInterrupt:
            push_button.exit_LEDs(self)


push_button()

