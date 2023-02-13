from phone_detector import PhoneDetector
from calibrator import Calibrator, RectangleDetector
from motor_controller import MotorController
import cv2 as cv
import numpy as np
import os
import util
#TODO: 颜色有问题，不能constantly检测到红色
#TODO: add list of phones
#TODO: fix absolute coordinate
#TODO: continue to train phone
#TODO: train calibration point

motor_move_distance = []

def capture_live(calibrator:RectangleDetector, phone_detector: PhoneDetector, motor_controller):
    video_capture = cv.VideoCapture(1)
    #video_capture.set(cv.CAP_PROP_FPS, 5)
    if video_capture.isOpened(): # try to get the first frame
        is_capturing, frame = video_capture.read()
    else:
        is_capturing = False
        print('Camera not connected')
        return

    while is_capturing:
        is_capturing, frame = video_capture.read() # capture new frame
        frame = phone_detector.detect_phone(frame)
        calibrator.find_cal_ref(frame)
        calibrator.draw_boundary_and_center(frame)
        draw_line(calibrator, phone_detector, frame)
        control_motor(motor_controller, calibrator, phone_detector)
        calibrator.clear_calibrator()
        cv.imshow("Live capture", frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        
    video_capture.release()
    cv.destroyAllWindows()

def draw_line(calibrator:RectangleDetector, phone_detector:PhoneDetector, frame):
    if calibrator.calibrator.is_detected and phone_detector.device.is_detected:
        cv.line(frame, calibrator.calibrator.center_point, phone_detector.device.center_point, (0, 0, 255), 2)

def control_motor(motor_controller: MotorController,calibrator:RectangleDetector, phone_detector:PhoneDetector):
    if calibrator.calibrator.is_detected and phone_detector.device.is_detected:
        motor_controller.calc_move_dist(calibrator, phone_detector)

def run_on_image(rect_detector: Calibrator, phone_detector: PhoneDetector, motor_controller: MotorController):
    img_loc = os.getcwd()+'\\calibration_img\\img_1.jpg'
    img = cv.imread(img_loc)
    img = phone_detector.detect_phone(img)
    rect_detector.find_cal_ref(img)
    rect_detector.draw_boundary_and_center(img)
    #rect_detector.draw_area(img)
    draw_line(rect_detector, phone_detector, img)
    if rect_detector.calibrator.is_detected and phone_detector.device.is_detected:
        motor_controller.calc_move_dist(rect_detector,phone_detector)
    cv.imshow("Img", img)
    cv.waitKey(0)

def main():
    ''' This function is used to run the main program '''
    phone_detector = PhoneDetector()
    rect_detector = RectangleDetector()
    motor_controller = MotorController('COM8')

    #run_on_image(rect_detector,phone_detector,motor_controller)

    capture_live(rect_detector, phone_detector, motor_controller)
    #util.capture_img(r'C:\\Users\\a7568\\Documents\\UW\\Project\\yolo_phone_detection\\calibration_img\\images')
    #util.capture_img(os.getcwd()+'\\calibration_img')
    #util.randomly_copy_img(os.getcwd()+'\\calibration_img', os.getcwd()+'\\calibration_img', 35, True )
    #motor_controller.send_hard_coordinate()

if __name__ == "__main__":
    main()