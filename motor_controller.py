import serial
import time
import numpy as np


RELATIVE = 'G91'
ABSOLUTE = ''

class MotorController:
    ''' Sends code to motor '''
    def __init__(self,COM_port):
        # a set of coordinate that sends to motor controller
        self.curr_motor_pos = [0,0]
        self.height = 800
        self.load_calib_param()
        try:
            self.serial = serial.Serial(COM_port, 115200)
        except serial.serialutil.SerialException:
            print("Port not found!")
            #raise
        time.sleep(2)
        #self.zero_position()

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

    def calc_move_dist(self, rect_detector, phone_detector, override_pos=None):
        ''' Find position between rectangle and phone'''
        # If diff is positive that means the motor needs to move up or right
        rect_world_coord = self.px2world(rect_detector.calibrator.center)
        phone_world_coord_list = [self.px2world(i.center) for i in phone_detector.devices]
        #if override_pos is None:
        is_motor_under_phone_region = self.is_motor_under_phone_region(self.curr_motor_pos, phone_detector)
        if not is_motor_under_phone_region:
            # Find the distance need to move if carriage is not under phone's region
            x_diff, y_diff = phone_world_coord_list[0][0] - rect_world_coord[0], phone_world_coord_list[0][1] - rect_world_coord[1]
            if abs(self.curr_motor_pos[0]-x_diff) > 10 or abs(self.curr_motor_pos[1]-y_diff) > 10:
                self.curr_motor_pos = [x_diff,y_diff]
                move_dist = self.curr_motor_pos
                print(move_dist)
        #else:
            #move_dist = self.px2world(override_pos)

        #if move_dist[0] < 1750 and move_dist[1] < 500: 
            #self.send_2d_coordinate(move_dist)
            #self.send_1d_coordinate(move_dist[0])
            

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
    
    def is_motor_under_phone_region(self, curr_motor_pos, phone_detector):
        for each_phone in phone_detector.devices:
            bbox_world_coord = [self.px2world(point) for point in each_phone.bbox]
            if bbox_world_coord[0][0] < curr_motor_pos[0] < bbox_world_coord[1][0] and bbox_world_coord[0][1] < curr_motor_pos[1] < bbox_world_coord[1][1]:
                return True
        return False

