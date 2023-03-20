from phone_detector import PhoneDetector
from calibrator import Calibrator, RectangleDetector
from motor_controller import MotorController
from hand_detector import HandDetector
import cv2 as cv
import os
import util

def capture_live(calibrator:RectangleDetector, phone_detector: PhoneDetector, motor_controller: MotorController):#, hand_detector: HandDetector):
    #video_capture = cv.VideoCapture(os.getcwd()+'/testing_img/video_1.mp4')
    video_capture = cv.VideoCapture(0)
    video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 1024)
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
        frame = undistort_frame(frame, motor_controller.intrinsic_mtx, motor_controller.camera_dist)
        frame = phone_detector.detect_phone(frame)
        calibrator.find_cal_ref(frame)
        calibrator.draw_boundary_and_center(frame)
        #hand_detector.detect_finger_tip(frame)
        #hand_detector.draw_finger_tip(frame)
        #phone_pos = None
        #if hand_detector.is_finger_stay_still():
            #phone_pos = is_finger_on_phone(hand_detector, phone_detector)
        draw_line(calibrator, phone_detector, frame)
<<<<<<< HEAD
        control_motor(motor_controller, calibrator, phone_detector, phone_pos=None)
=======
        control_motor(motor_controller, calibrator, phone_detector)#, hand_detector)
        # for message in motor_controller.message_queue.queue:
        #     print("Message is {}".format(message))
        #     if message[1:4] == 'PRB' and not motor_controller.is_charging:
        #         motor_controller.self_correct(calibrator, phone_detector)
        #         print("The device need to self correct! ")
        #         break
>>>>>>> multi_device_detection
        calibrator.clear_calibrator()
        phone_detector.clear_device()
        
        cv.imshow("Live capture", frame)

        key = cv.waitKey(1)
        if key & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv.destroyAllWindows()

def draw_line(calibrator:RectangleDetector, phone_detector:PhoneDetector, frame):
    if calibrator.calibrator.is_detected and phone_detector.devices:
        #if phone_detector.devices[0].is_detected:
            cv.line(frame, calibrator.calibrator.center, phone_detector.devices[0].center, (0, 0, 255), 2)

<<<<<<< HEAD
def control_motor(motor_controller: MotorController,calibrator:RectangleDetector, phone_detector:PhoneDetector, phone_pos):
    if calibrator.calibrator.is_detected and phone_detector.devices:
        motor_controller.calc_move_dist(calibrator, phone_detector)
=======
def control_motor(motor_controller: MotorController,calibrator:RectangleDetector, phone_detector:PhoneDetector):#, hand_detector: HandDetector):
    if calibrator.calibrator.is_detected and phone_detector.devices:
        if phone_detector.devices[0].is_detected:
            #is_finger_on_phone(hand_detector, phone_detector)
            motor_controller.calc_move_dist(calibrator, phone_detector)
>>>>>>> multi_device_detection

def is_finger_on_phone(hand_detector:HandDetector, phone_detector:PhoneDetector):
    if hand_detector.is_detected and phone_detector.devices:
        for device in phone_detector.devices:
            if device.bbox[0][0] < hand_detector.x < device.bbox[1][0] and device.bbox[0][1] < hand_detector.y < device.bbox[1][1]:
                return device.center
    return None

def run_on_image(rect_detector: Calibrator, phone_detector: PhoneDetector, motor_controller: MotorController):
    img_loc = os.getcwd()+'/testing_img/img_2.jpg'
    img = cv.imread(img_loc)
    img = phone_detector.detect_phone(img)
    rect_detector.find_cal_ref(img)
    rect_detector.draw_boundary_and_center(img)
    #rect_detector.draw_area(img)
    draw_line(rect_detector, phone_detector, img)
    if rect_detector.calibrator.is_detected and phone_detector.devices:
        motor_controller.calc_move_dist(rect_detector,phone_detector)
    cv.imshow("Img", img)
    cv.waitKey(0)

def undistort_frame(frame, mtx, dist):
    h,w = frame.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    undistorted_frame = cv.undistort(frame, mtx, dist, None, newcameramtx)
    return undistorted_frame



def main():
    ''' This function is used to run the main program '''
    phone_detector = PhoneDetector()
    rect_detector = RectangleDetector()
<<<<<<< HEAD
    motor_controller = MotorController('COM8')
=======
    motor_controller = MotorController('/dev/tty.usbmodem11201', run_on_motor=False)
>>>>>>> multi_device_detection
    #hand_detector = HandDetector()

    run_on_image(rect_detector,phone_detector,motor_controller)

<<<<<<< HEAD
    capture_live(rect_detector, phone_detector, motor_controller, hand_detector=None)
    #util.capture_img(r'C:\\Users\\a7568\\Documents\\UW\\Project\\yolo_phone_detection\\calibration_img\\images')
=======
    #capture_live(rect_detector, phone_detector, motor_controller)#, hand_detector)
    #util.capture_img(os.getcwd()+'/testing_img')
>>>>>>> multi_device_detection
    #util.capture_img(os.getcwd()+'\\calibration_img')
    #util.randomly_copy_img(os.getcwd()+'\\calibration_img', os.getcwd()+'\\calibration_img', 35, True )
   
if __name__ == "__main__":
    main()