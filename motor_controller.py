import serial
import time
import numpy as np
import threading
import queue


RELATIVE = 'G21G91'
ABSOLUTE = 'G21G90'
PRB_INTR = 'G38.2'

class MotorController:
    ''' Sends code to motor '''
    def __init__(self,COM_port):
        # a set of coordinate that sends to motor controller
        self.old_actual_dist = [0,0]
        self.cal_phone_dist = [0,0]
        self.height = 780
        self.load_calib_param()
        self.count = 0
        try:
            self.serial = serial.Serial(COM_port, 115200)
        except serial.serialutil.SerialException:
            print("Port not found!")
            raise
        time.sleep(2)
        self.go_home()
        self.zero_position()
        #self.message_queue = queue.Queue()
        #self.is_charging = False
        #self.indicator_listener = threading.Thread(target=self.poll_serial)#, args=('/dev/ttyACM0', 9600))
        #self.indicator_listener.start()

    # def calc_move_dist(self, rect_detector, phone_detector):
    #     ''' Find position between rectangle and phone'''
    #     # If diff is positive that means the motor needs to move up or right
    #     x_diff = phone_detector.devices[0].center[0] - rect_detector.calibrator.center[0]
    #     y_diff = phone_detector.devices[0].center[1] - rect_detector.calibrator.center[1]
    #     if abs(self.cal_phone_dist[0]-x_diff) > 10 or abs(self.cal_phone_dist[1]-y_diff) > 10:
    #         self.cal_phone_dist = [x_diff, y_diff]
    #         new_actual_dist = [round(x / rect_detector.get_rect_dimension()/10) for x in self.cal_phone_dist]
    #         actual_dist = new_actual_dist
    #         print(actual_dist)
    #         #if actual_dist[0] < 1750 and actual_dist[1] < 500: 
    #             #self.send_2d_coordinate(actual_dist)
    #             #self.send_1d_coordinate(actual_dist[0])

    def calc_move_dist(self, rect_detector, phone_detector):
        ''' Find position between rectangle and phone'''
        # If diff is positive that means the motor needs to move up or right
        rect_world_coord = self.px2world(rect_detector.calibrator.center)
        phone_world_coord = self.px2world(phone_detector.devices[0].center)
        # x+是往外走 y-是往外走
        x_diff = phone_world_coord[0] - rect_world_coord[0] # should be positive
        y_diff = phone_world_coord[1] - rect_world_coord[1] # should be positive
        #x_diff = rect_world_coord[0] - phone_world_coord[0]
        #y_diff = rect_world_coord[1] - phone_world_coord[1]
        if self.count != 0:
            self.count+=1
        if self.count >=5 or abs(self.cal_phone_dist[0]-x_diff) > 20 or abs(self.cal_phone_dist[1]-y_diff) > 20:
            self.count +=1
            print("phone_coord={}".format(phone_world_coord))
            print("rect_coord={}".format(rect_world_coord))
            print("cal_phone_dist={}".format(self.cal_phone_dist))
            print("x_diff={}, y_diff={}".format(x_diff,y_diff))
            self.cal_phone_dist = [x_diff, y_diff]
            if abs(self.cal_phone_dist[0]) < 855 and self.cal_phone_dist[1] < 350: 
                if self.count >=5:
                    print("Actual dist: {}".format(self.cal_phone_dist))
                    self.send_2d_coordinate(self.cal_phone_dist)
                    self.count=0
            #self.send_1d_coordinate(self.cal_phone_dist[0])

    def self_correct(self, rect_detector, phone_detector):
        self.message_queue.queue.clear()
        pass

    def reset_motor():
        pass

    def close_serial(self):
        self.serial.close()

    def send_2d_coordinate(self, actual_dist, speed = 6000):
        #if actual_dist[0] > 0:
        send_phase_1_command = False
        if actual_dist[1] < 0:
            command = f"$X\n"
            self.send_command(command)
            phase_1_x= actual_dist[0] - 12 * (actual_dist[0] < 0) + 12 * (actual_dist[0] >= 0)
            phase_1_y= actual_dist[1] - 12 * (actual_dist[1] < 0) + 12 * (actual_dist[1] >= 0)
            if actual_dist[0] > 700:
                phase_1_x= actual_dist[0] - 23 * (actual_dist[0] < 0) + 23 * (actual_dist[0] >= 0)
            #command = f"{PRB_INTR} X{str(phase_1_x)} Y{str(phase_1_y)} F{6000}\n"
            #print('Phase 1 command is {}'.format(command))
            #self.send_command(command)
            command = f"$J={ABSOLUTE} X{str(phase_1_x)} Y{str(phase_1_y)} F{speed}\n"
            #command = f"$J={ABSOLUTE} X{str(actual_dist[0])} Y{str(actual_dist[1])} F{speed}\n"
            #command = f"{PRB_INTR} X{str(actual_dist[0])} Y{str(actual_dist[1])} F{speed}\n"
            print('Phase 2 command is {}'.format(command))
            self.send_command(command)
            self.send_command(f"$X\n")

    def send_1d_coordinate(self, actual_dist, speed = 3000):
        # + is going toward home
        #if actual_dist > 0:
            command = f"$X\n"
            self.send_command(command)
            command = f"{PRB_INTR} X{str(actual_dist)} F{speed}\n"
            self.send_command(command)

    def go_home(self):
        ''' Go to zero point for all motors'''
        self.send_command(f'$X\n')
        self.send_command(f'$H\n')
        # while True:
        #     line = self.serial.readline()
        #     if line == b'ok\r\n':
        #         print("Homing finished. ")
        #         break

    def zero_position(self):
        '''Zero out the position'''
        self.send_command(f"G10 L20 P1 X0 Y0 Z0\n")   

    def send_command(self, command):
        '''Send out command'''
        self.serial.write(str.encode(command)) 
        while True:
            line =self.serial.readline()
            print(line)
            if line == b'ok\r\n':
                print("Ok")
                break
        # while True:
        #     line = self.serial.readline()
        #     print(line)
        #     #if line[1:4] == 'PRB' and line[-6] == '1':
        #         #print("Motor should stop")
        #     if line == b'ok\r\n':
        #         break

    def px2world(self, coord):
        ''' Convert pixel coordinate to world coordinate '''
        #(u-cx)/fx*z 
        x = (coord[0]-self.intrinsic_mtx[0][2])/self.intrinsic_mtx[0][0]*self.height
        #(v-cy)/fy*z
        y = (coord[1]-self.intrinsic_mtx[1][2])/self.intrinsic_mtx[1][1]*self.height
        return (round(x), round(y))
    
    def load_calib_param(self):
        ''' Load camera params from npz file '''
        try:
            data = np.load('camera_calibration//calib_param.npz')
        except Exception as e:
            print('npz file not found')
            raise
        self.intrinsic_mtx = data['mtx']
        self.camera_dist = data['dist']
        self.rvecs = data['rvecs']
        self.tvecs = data['tvecs']
        #Jupter notebook
        #self.intrinsic_mtx = np.array([[978, 0, 611], [0, 978, 360], [0, 0, 1]])
        #Matlab
        #self.intrinsic_mtx = np.array([[957, 0, 634], [0, 957, 366], [0, 0, 1]])

    def poll_serial(self):
        while True:
            line = self.serial.readline()
            print(line)
            if line != b'ok\r\n':
                if line[1:4] == 'PRB':
                    self.is_charging = [-6]
                self.message_queue.put(line)
            # if line == b'ok\r\n':
            #     break
