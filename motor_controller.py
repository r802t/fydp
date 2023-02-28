import serial
import time
import numpy as np


RELATIVE = 'G91'
ABSOLUTE = ''

class MotorController:
    ''' Sends code to motor '''
    def __init__(self,COM_port):
        # a set of coordinate that sends to motor controller
        self.old_actual_dist = [0,0]
        self.cal_phone_dist = [0,0]
        try:
            self.serial = serial.Serial(COM_port, 115200)
        except serial.serialutil.SerialException:
            print("Port not found!")
            #raise
        time.sleep(2)
        #self.zero_position()

    def calc_move_dist(self, rect_detector, phone_detector):
        ''' Find position between rectangle and phone'''
        # If diff is positive that means the motor needs to move up or right
        x_diff = phone_detector.devices[0].center[0] - rect_detector.calibrator.center[0]
        y_diff = phone_detector.devices[0].center[1] - rect_detector.calibrator.center[1]
        if abs(self.cal_phone_dist[0]-x_diff) > 10 or abs(self.cal_phone_dist[1]-y_diff) > 10:
            self.cal_phone_dist = [x_diff, y_diff]
            new_actual_dist = [round(x / rect_detector.get_rect_dimension()/10) for x in self.cal_phone_dist]
            #ratio = rect_detector.get_rect_dimension()/10
            #print('Ratio: {} x_diff: {} y_diff: {}'.format(ratio, x_diff, y_diff))
            actual_dist = new_actual_dist
            print(actual_dist)
            #if actual_dist[0] < 1750 and actual_dist[1] < 500: 
                #self.send_2d_coordinate(actual_dist)
                #self.send_1d_coordinate(actual_dist[0])
            

    def reset_motor():
        pass

    def close_serial(self):
        self.serial.close()

    def send_2d_coordinate(self, actual_dist, speed = 100):
        command = f"G21{ABSOLUTE} X{str(actual_dist[0])} Y{str(-actual_dist[1])} F{speed}\n"
        self.send_command(command)

    def send_1d_coordinate(self, actual_dist, speed = 100):
        command = f"G21{ABSOLUTE} X{str(actual_dist)} F{speed}\n"
        self.send_command(command)

    def go_home(self):
        ''' Go to zero point for all motors'''
        self.send_command(f"G90\n")
        self.send_command(f"G0 X0 Y0\n")

    def zero_position(self):
        '''Zero out the position'''
        self.send_command(f"G10 L20 P1 X0 Y0 Z0\n")   

    def send_command(self, command):
        '''Send out command'''
        self.serial.write(str.encode(command)) 
        while True:
            line = self.serial.readline()
            print(line)
            if line == b'ok\r\n':
                break