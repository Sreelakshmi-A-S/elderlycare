import serial
import time


ser = serial.Serial('COM3', baudrate=9600, timeout=1)
def collect_data(ser):
    data = ser.readline().decode().strip()
    return data