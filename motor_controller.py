import serial
import time
import numpy as np
import threading
import queue


RELATIVE = 'G21G91'
ABSOLUTE = 'G21G90'
PRB_INTR = 'G38.2'
UNLOCK = f"$X\n"

class MotorController:
    ''' Sends code to motor '''
    def __init__(self,COM_port, run_on_motor):
        # a set of coordinate that sends to motor controller
        self.charger_pos = [0,0]
        self.height = 780
        self.load_calib_param()
        self.move_count = 0  
        self.on_phone_count = 0
        if run_on_motor:
            try:
                self.serial = serial.Serial(COM_port, 115200)
            except serial.serialutil.SerialException:
                print("Port not found!")
                raise
            time.sleep(2)
            self.go_home()
            self.zero_position()

    def calc_move_dist(self, rect_detector, phone_detector, override_pos):
        ''' Find position between rectangle and phone'''
        #Get all distance between calibrator to all phones
        dists = self.get_all_dist(rect_detector, phone_detector)
        if override_pos is not None:
            if abs(dists[override_pos-1][0]-self.charger_pos[0])>10 or abs(dists[override_pos-1][1]-self.charger_pos[1])>10:
                self.charger_pos = dists[override_pos-1]
                self.send_2d_coordinate(self.charger_pos)
            return 
        
        if not self.is_charger_under_phone(self.charger_pos, dists): # If the charger is not under phone's region than move else move
            if abs(self.charger_pos[0] - dists[0][0]) > 10 or abs(self.charger_pos[1] - dists[0][1]) > 10:
                # If the left most phone moved, move the charger to the left most phone
                self.move_count +=1
                if self.move_count >= 20: # Wait until the phone has stayey long enough at the same position (in case a phone is not detected at certain frames)
                    self.charger_pos = dists[0] # Update motor position
                    self.send_2d_coordinate(self.charger_pos) # Move motor
                    print("Actual dist: {}".format(self.charger_pos))
                    self.move_count = 0
    
        

    def self_correct(self, rect_detector, phone_detector):
        self.message_queue.queue.clear()
        pass

    def reset_motor():
        pass

    def close_serial(self):
        self.serial.close()

    def send_2d_coordinate(self, distance, speed = 6000):
        if distance[1] < 0:
            # Adjust factor to get a more precise location
            x_dest= distance[0] - 12 * (distance[0] < 0) + 12 * (distance[0] >= 0)
            y_dest= distance[1] - 12 * (distance[1] < 0) + 12 * (distance[1] >= 0)
            if distance[0] > 700:
                # If distance is too larger than the adjust factor should be changed
                x_dest= distance[0] - 23 * (distance[0] < 0) + 23 * (distance[0] >= 0)
            if self.is_in_allowable_region([x_dest, y_dest]): # Check if motor will go out of bound
                self.send_command(UNLOCK)
                command = f"$J={ABSOLUTE} X{str(x_dest)} Y{str(y_dest)} F{speed}\n"
                self.send_command(command)
            else:
                print("Destination is out of bound: {}".format([x_dest,y_dest]))

    def send_1d_coordinate(self, actual_dist, speed = 3000):
        command = f"$X\n"
        self.send_command(command)
        command = f"{PRB_INTR} X{str(actual_dist)} F{speed}\n"
        self.send_command(command)

    def go_home(self):
        ''' Go to zero point for all motors'''
        self.send_command(f'$X\n')
        self.send_command(f'$H\n')

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
                #print("Ok")
                break

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

    def is_charger_under_phone(self, charger_pos, dists):
        for each_dist in dists:
            if abs(charger_pos[0]-each_dist[0])<10 and abs(charger_pos[1]-each_dist[1])<10:
                # The charger is under a phone
                return True 
        return False
    
    @staticmethod
    def has_phone_moved(cal_phone_dist, x_diff, y_diff):
       return abs(cal_phone_dist[0]-x_diff) > 20 or abs(cal_phone_dist[1]-y_diff) > 20
    
    @staticmethod
    def is_in_allowable_region(destination):
        return 0 < destination[0] < 855 and abs(destination[1]) < 350
    
    def get_all_dist(self, calibrator, phones):
        rect_world_coord = self.px2world(calibrator.calibrator.center)
        calibrator_phone_dists = []
        for each_phone in phones.devices:
            phone_world_coord = self.px2world(each_phone.center)
            x_diff = phone_world_coord[0] - rect_world_coord[0] # should be positive
            y_diff = phone_world_coord[1] - rect_world_coord[1] # should be positive
            calibrator_phone_dists.append([x_diff,y_diff])
        return calibrator_phone_dists
