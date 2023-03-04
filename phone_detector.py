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
        self.model.conf = 0.7
        self.devices = list() 
        self.devices_prev_frame = list() 
        self.count = 0
        # To remember the location of each phones from last frame
        # so that we can assign the devices in proper order

    def load_model(self):
        ''' Load model from torch hub '''
        model = torch.hub.load('yolov5', 
                                'custom', path='trained_models/yolov5s_phone_3.pt', source='local') 
        return model
    
    # def detect_phone(self, img):
    #     ''' Detect phone from a given image '''
    #     detect_result = self.model(img, size=640)
    #     if detect_result.xyxy[0].numel():
    #         # self.count +=1
    #         # if self.count == 93:
    #         #     print("1 available ids run out")
    #         # if self.count == 105:
    #         #     print("available ids run out")
    #         id=1
    #         available_ids = [i for i in range(1, len(detect_result.xyxy[0]) + 1)]
    #         for each_device in detect_result.xyxy[0]:
    #             closest_distance = float('inf')
    #             closest_device = None
    #             current_center = self.get_center(each_device)
    #             current_device = PhoneDetector.phone(is_detected=True, bbox=self.get_bbox(each_device), 
    #                                          center=current_center, id=id, conf=self.get_conf(each_device))
    #             if len(self.devices_prev_frame):
    #                 for each_prev_device in self.devices_prev_frame:
    #                     distance = math.hypot(each_prev_device.center[0] - current_center[0],
    #                                           each_prev_device.center[1] - current_center[1])
    #                     if distance <= closest_distance:
    #                         closest_distance = distance
    #                         closest_device = each_prev_device

    #                 if closest_distance < 30: 
    #                     id = closest_device.id
    #                     if id not in available_ids:
    #                         id = self.find_closest_id(id, available_ids)
    #                     available_ids.remove(id)
    #                 elif len(available_ids): #只适合加 不适合减
    #                     id = available_ids[0]
    #                     available_ids.remove(id)
    #                 else:
    #                     print("Hello")
    #                     id+=1
    #                     break                    

    #             current_device.id = id
    #             id+=1

    #             self.devices.append(current_device)
    #             self.devices = sorted(self.devices, key=self.sort_key)
    #             self.draw_on_img(img, current_device)
            
    #     self.devices_prev_frame = self.devices.copy()

    #     return img
    
    def detect_phone(self, img):
        detect_result = self.model(img, size=640)
        # Detect all devices and order from left to right
        if detect_result.xywh[0].numel():
            for each_device in detect_result.xywh[0]:
                #sort_point(each_device)
                current_device = PhoneDetector.phone(is_detected=True, bbox=self.get_bbox(each_device), 
                                                    center=self.get_center(each_device), id=0, conf=self.get_conf(each_device))
                #self.print_result(each_device,current_device)
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
        cv.rectangle(img, device.bbox[0], device.bbox[1], (0, 0, 255), 2)
        cv.circle(img, device.center, 5, (0,255,0), -1)
        cv.putText(img=img, text=f'{device.center}', org=device.center, fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)
        cv.putText(img=img, text=f'Device {device.id} {device.conf}', org=device.bbox[0], fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)       

    @staticmethod
    def sort_key(device):
        return device.center[0]
    
    @staticmethod
    def find_closest_id(num, lst):
        return min(lst, key=lambda x:(abs(x-num),-x))