from phone_detector import PhoneDetector
from calibrator import Calibrator, RectangleDetector
from motor_controller import MotorController
import cv2 as cv
import numpy as np
import os
import util
#TODO: 颜色有问题，不能constantly检测到红色

def capture_live(calibrator:RectangleDetector, phone_detector: PhoneDetector, motor_controller):
    #video_capture = cv.VideoCapture(os.getcwd()+'\\testing_img\\phone_labelling_test\\video_1.mp4')
    video_capture = cv.VideoCapture(0)
    if video_capture.isOpened(): # try to get the first frame
        is_capturing, frame = video_capture.read()
    else:
        is_capturing = False
        print('Camera not connected')
        return

    while is_capturing:
        is_capturing, frame = video_capture.read() # capture new frame
        if not is_capturing:
            break

        frame = phone_detector.detect_phone(frame)
        calibrator.find_cal_ref(frame)
        calibrator.draw_boundary_and_center(frame)
        draw_line(calibrator, phone_detector, frame)
        control_motor(motor_controller, calibrator, phone_detector)
        calibrator.clear_calibrator()
        phone_detector.clear_device()
        
        cv.imshow("Live capture", frame)

        key = cv.waitKey(25)
        if key & 0xFF == ord(" "):
            while key & 0xFF != ord(" "):
                key = cv.waitKey(25)
            #break
        
    video_capture.release()
    cv.destroyAllWindows()

def draw_line(calibrator:RectangleDetector, phone_detector:PhoneDetector, frame):
    if calibrator.calibrator.is_detected and phone_detector.devices:
        if phone_detector.devices[0].is_detected:
            cv.line(frame, calibrator.calibrator.center, phone_detector.devices[0].center, (0, 0, 255), 2)

def control_motor(motor_controller: MotorController,calibrator:RectangleDetector, phone_detector:PhoneDetector):
    if calibrator.calibrator.is_detected and phone_detector.devices:
        if phone_detector.devices[0].is_detected:
            motor_controller.calc_move_dist(calibrator, phone_detector)

def main():
    ''' This function is used to run the main program '''
    phone_detector = PhoneDetector()
    rect_detector = RectangleDetector()
    motor_controller = MotorController('COM3')

    # img_loc = os.getcwd()+'\\testing_img\\phone_labelling_test\\img_1.jpg'
    # img = cv.imread(img_loc)
    # img = phone_detector.detect_phone(img)
    # rect_detector.find_cal_ref(img)
    # rect_detector.draw_boundary_and_center(img)
    # draw_line(rect_detector, phone_detector, img)
    # #motor_controller.calc_move_dist(rect_detector,phone_detector)
    # cv.imshow("Img", img)
    # cv.waitKey(0)

    capture_live(rect_detector, phone_detector, motor_controller)
    #util.capture_img(r'C:\\Users\\a7568\\Documents\\UW\\Project\\yolo_phone_detection\\training_img\\images')
    #util.randomly_copy_img(os.getcwd()+'\\training_img', os.getcwd()+'\\training_img', 35, True )

if __name__ == "__main__":
    main()