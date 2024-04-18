import serial
import time


port = serial.Serial('COM5', baudrate=9600, timeout=1)
def call():
    port.write(b'AT\r')
    rcv = port.read(10)
    print(rcv)
    time.sleep(1)
    port.write(b'ATD9995234163;\r')
    print('Calling…')
    time.sleep(30)
    # port.write(b’ATH\r’)
    # print(“Hang Call…”)