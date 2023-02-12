import serial
import time


class MotorController:
    ''' Sends code to motor '''
    def __init__(self,COM_port):
        # a set of coordinate that sends to motor controller
        self.move_distance = [0,0]
        self.cal_phone_dist = [0,0]
        try:
            self.serial = serial.Serial(COM_port, 115200)
        except serial.serialutil.SerialException:
            print("Arduino not found!")

    def calc_move_dist(self, rect_detector, phone_detector):
        ''' Find position between rectangle and phone'''
        # If diff is positive that means the motor needs to move up or right
        x_diff = phone_detector.device.center_point[0] - rect_detector.calibrator.center_point[0]
        y_diff = phone_detector.device.center_point[1] - rect_detector.calibrator.center_point[1]
        if abs(self.cal_phone_dist[0]-x_diff) > 20 or abs(self.cal_phone_dist[1]-y_diff) > 20:
            self.cal_phone_dist = [x_diff, y_diff]
            #print(self.cal_phone_dist)
            actual_dist = [round(x / rect_detector.get_rect_dimension()/10) for x in self.cal_phone_dist]
            print(actual_dist)
            #self.send_to_controller(actual_dist)

    def send_to_controller(self, move_dist):
        self.serial.write(b'Hello, Arduino')

    def reset_motor():
        pass

    def convert_to_adn(self, cal_phone_dist):
        pass

    def close_serial(self):
        self.serial.close()

    def send_hard_coordinate(self,actual_dist = [0,0], speed = 3000):

        command = f"G21G91 X{str(actual_dist[0])} Y{str(actual_dist[1])} F{speed}"
        #self.serial.write(str.encode(command))
        self.serial.write(b'G21G91 X10 F1000\n')
        time.sleep(1)
        while True:
            line = self.serial.readline()
            print(line)
            if line == b'ok\n':
                break
        #self.serial.write(f'{coordinate}')


