import torch
from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import util
from dataclasses import dataclass


#arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)

class PhoneDetector:
    @dataclass
    class phone:
        is_detected: bool
        bbox: list[int]
        center_point: tuple

    def __init__(self) -> None:
        self.model = self.load_model()
        self.device = PhoneDetector.phone(is_detected = False, bbox=None, center_point=(0,0))

    def load_model(self):
        ''' Load model from torch hub '''
        model = torch.hub.load('ultralytics/yolov5', 'yolov5l')
        model.classes = [67] # only detect phones
        return model
    
    def detect_phone(self, img):
        ''' Detect phone from a given image '''
        detect_result = self.model(img)
        center = self.get_phone_center_point(detect_result)
        if center:
            points = ([(int(detect_result.xyxy[0][0][0]),int(detect_result.xyxy[0][0][1])), #top left
                       (int(detect_result.xyxy[0][0][2]),int(detect_result.xyxy[0][0][3]))]) #bottom right
            self.device.is_detected = True
            self.device.bbox = points
            self.device.center_point = center
            cv.rectangle(img, points[0], points[1], (0, 0, 255), 2)
            cv.circle(img, center, 5, (0,255,0), -1)
            cv.putText(img=img, text=f'{center}', org=center, fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)             
            #detect_result = np.squeeze(detect_result.render())
        return img

    def save_live_img(save_to_directory:str, model):
        video_capture = cv.VideoCapture(0)
        num_img = util.count_img_in_folder(save_to_directory)
        if video_capture.isOpened(): # try to get the first frame
            rval, frame = video_capture.read()
        else:
            rval = False
            print('Camera not connected')
            return
        while rval:
            results = model(frame)
            # results.show()
            cv.imshow("preview", np.squeeze(results.render()))
            rval, frame = video_capture.read()
            key = cv.waitKey(1)
            if key == 27:
                break
            elif key == 32:
                img_name = f'{save_to_directory}\img_{num_img+1}.jpg'
                cv.imwrite(img_name, frame)
                num_img += 1

        video_capture.release()
        cv.destroyAllWindows()

    def get_phone_center_point(self, result):
        ''' Calculate center point from detected image '''
        if result.xyxy[0].numel():
            x_midpoint = int((result.xyxy[0][0][0]+result.xyxy[0][0][2])/2)
            y_midpoint = int((result.xyxy[0][0][1]+result.xyxy[0][0][3])/2)
            center = [x_midpoint, y_midpoint]
        else:
            center = None
        return center


    #def write_to_arduino(coordinate):
    #    arduino.write(bytes(coordinate, 'utf-8'))
    #    time.sleep(0.05)
