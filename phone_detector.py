import torch
import cv2 as cv
from dataclasses import dataclass


class PhoneDetector:
    @dataclass
    class phone:
        is_detected: bool
        bbox: list[int]
        center: tuple
        id : int
        conf: float

    def __init__(self) -> None:
        self.model = self.load_model()
        self.model.conf = 0.5
        self.devices = list()  
        # To remember the location of each phones from last frame
        # so that we can assign the devices in proper order

    def load_model(self):
        ''' Load model from torch hub '''
        model = torch.hub.load('yolov5', 
                                'custom', path='trained_models/yolov5s_phone_5.pt', source='local') 
        return model
    
    def detect_phone(self, img):
        detect_result = self.model(img, size=640)
        # Detect all devices and order from left to right
        if detect_result.xywh[0].numel():
            for each_device in detect_result.xywh[0]:
                if self.is_rect_ratio(each_device):
                    current_device = PhoneDetector.phone(is_detected=True, bbox=self.get_bbox(each_device), 
                                                        center=self.get_center(each_device), id=0, conf=self.get_conf(each_device))
                    self.devices.append(current_device)
            self.devices = sorted(self.devices, key=self.sort_key)
            for i in range(len(self.devices)):
                self.devices[i].id = i+1
                self.draw_on_img(img,self.devices[i])
        return img

    @staticmethod
    def get_center(result):
        ''' Calculate center point from detected object '''
        center = [round(float(result[0])), round(float(result[1]))]
        return center
    
    @staticmethod
    def get_bbox(result):
        ''' Get boundary box from the detected object '''
        # points[0]=top left points[1]=bottom right
        points = ([(round(float(result[0]-result[2]/2)),round(float(result[1]-result[3]/2))), (round(float(result[0]+result[2]/2)),round(float(result[1]+result[3]/2)))])
        return points
    
    @staticmethod
    def get_conf(result):
        ''' Get confidence score from the detected object '''
        return round(result[4].item(),2)

    def clear_device(self):
        self.devices.clear()

    @staticmethod
    def draw_on_img(img, device):
        cv.rectangle(img, device.bbox[0], device.bbox[1], (0, 255, 0), 2)
        cv.circle(img, device.center, 5, (0,255,0), -1)
        cv.putText(img=img, text=f'{device.center}', org=device.center, fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)
        cv.putText(img=img, text=f'Device {device.id} {device.conf}', org=device.bbox[0], fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)       

    @staticmethod
    def sort_key(device):
        return device.center[0]
    
    @staticmethod
    def find_closest_id(num, lst):
        return min(lst, key=lambda x:(abs(x-num),-x))
    
    def is_rect_ratio(self, each_device):
        if each_device[2] / each_device[3] < 0.8 or each_device[3] / each_device[2] < 0.8:
            return True
        return False
        
