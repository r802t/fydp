import serial
import time

class MotorController:
    ''' Sends code to motor '''
    def __init__(self,COM_port):
        # a set of coordinate that sends to motor controller
        self.old_actual_dist = [0,0]
        self.cal_phone_dist = [0,0]
        try:
            self.serial = serial.Serial(COM_port, 115200)
        except serial.serialutil.SerialException:
            print("Arduino not found!")
        # if self.serial:    
        #     time.sleep(15)

        #     self.serial.write(b'G10 L20 P1 X0 Y0 Z0')
        #     while True:
        #         line = self.serial.readline()
        #         print(line)
        #         if line == b'ok\r\n':
        #             break
            time.sleep(5)

    def calc_move_dist(self, rect_detector, phone_detector):
        ''' Find position between rectangle and phone'''
        # If diff is positive that means the motor needs to move up or right
        x_diff = phone_detector.device.center_point[0] - rect_detector.calibrator.center_point[0]
        y_diff = phone_detector.device.center_point[1] - rect_detector.calibrator.center_point[1]
        if abs(self.cal_phone_dist[0]-x_diff) > 40 or abs(self.cal_phone_dist[1]-y_diff) > 40:
            self.cal_phone_dist = [x_diff, y_diff]
            #print(self.cal_phone_dist)
            new_actual_dist = [round(x / rect_detector.get_rect_dimension()/10) for x in self.cal_phone_dist]
            if self.old_actual_dist == [0,0]:
                actual_dist = new_actual_dist[0]
            else:
                actual_dist = new_actual_dist[0] - self.old_actual_dist[0]
            #elif new_actual_dist[0] < self.old_actual_dist[0]:
            #    actual_dist = self.old_actual_dist[0] - new_actual_dist[0]
            self.old_actual_dist = new_actual_dist
            print(actual_dist)
            if actual_dist < 1750: #TODO: add [1]
                self.send_hard_coordinate(actual_dist)
            #self.send_to_controller(actual_dist)

    def reset_motor():
        pass

    def close_serial(self):
        self.serial.close()

    def send_hard_coordinate(self, actual_dist, speed = 100):
        #command = f"G21G91 X{str(actual_dist[0])} Y{str(actual_dist[1])} F{speed}\n"
        command = f"G21G91 X{str(-actual_dist/5)} F{speed}\n"
        self.serial.write(str.encode(command))
        #self.serial.write(b'G21G91 X-10 F3000\n') #- is to away from motor 
        time.sleep(1)
        while True:
            line = self.serial.readline()
            print(line)
            if line == b'ok\r\n':
                break
        #self.serial.write(f'{coordinate}')


