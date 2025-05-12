# pattern : move_servos({0: 0, 1: 0, 2: 0, 3: 0}

import serial
import time

ser = None

def connect_arduino(port='/dev/ttyUSB0', baudrate=9600):
    global ser
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        return ser
    except serial.SerialException as e:
        ser = None
        return None

def move_servos(servo_positions):
    command = ', '.join([f"{servo}, {angle}" for servo, angle in servo_positions.items()])
    
    try:
        full_command = command + '\n'
        ser.write(full_command.encode('utf-8'))
    
    except Exception as e:
        print("Error sending to Arduino : {e}")

def main():
    connect_arduino()
    
    if not ser:
        return
    try:
        move_servos({0: 180, 1: 180, 2: 0, 3: 0})
        
    except KeyboardInterrupt:
        print("\nArrêt du programme")
    
    finally:
        if ser:
            ser.close()

if __name__ == "__main__":
    main()
