import cv2 as cv
from dataclasses import dataclass
import numpy as np
from abc import ABC, abstractmethod

RECT_SIDE_LENGTH = 400

class Calibrator(ABC):
    
    @dataclass
    class CalibratorInfo:
        is_detected: bool
        corner_points: np.ndarray
        center: tuple

    @abstractmethod
    def find_cal_ref(frame):
        pass

class RectangleDetector(Calibrator):
    
    def __init__(self):
        #self.calibrator = super().CalibratorInfo(False, np.ndarray([]), tuple())
        self.calibrators = list()

    def find_cal_ref(self, frame:np.ndarray):
        ''' Find all red rectangles in a given frame '''
        #hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        frame_blur = cv.GaussianBlur(frame, (5, 5), 0)
        frame_hsv = cv.cvtColor(frame_blur, cv.COLOR_BGR2HSV)
        hsv = cv.erode(frame_hsv, None, iterations=2) 

        # # Define range of red color in HSV
        # lower_red_1 = np.array([0,25,20])
        # upper_red_1 = np.array([50,100,255])
        # lower_red_2 = np.array([160,100,20])
        # upper_red_2 = np.array([179,255,255])
        # Another set
        # lower_red_1 = np.array([0, 50, 50])
        # upper_red_1 = np.array([10, 255, 255])
        # lower_red_2 = np.array([170, 50, 50])
        # upper_red_2 = np.array([180, 255, 255])
        lower_red_1 = np.array([0,70,50]) #70
        upper_red_1 = np.array([10,255,255])
        lower_red_2 = np.array([160,70,50])
        upper_red_2 = np.array([180,255,255])
        lower_mask = cv.inRange(hsv, lower_red_1, upper_red_1)
        upper_mask = cv.inRange(hsv, lower_red_2, upper_red_2)
        mask = lower_mask + upper_mask
        cv.imshow("Mask", mask)

        #At night only
        # lower_red = np.array([0,150,150])
        # upper_red = np.array([180,255,255])
        # lower_red = np.array([0, 50, 50])
        # upper_red = np.array([10, 255, 255])

        #one that I've determined myself
        # lower_red = np.array([0,150,50])
        # upper_red = np.array([180,255,255])
        # mask = cv.inRange(hsv, lower_red, upper_red)

        # Find contours in the mask
        contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if 1500 <cv.contourArea(cnt) < 5000 : # adjust threshold if needed
                approx = cv.approxPolyDP(cnt, 0.02*cv.arcLength(cnt,True),True)
                #cv.fillPoly(frame,[cnt],(0,255,0))
                #if len(approx) == 4:
                x, y, w, h = cv.boundingRect(cnt)
                ratio = float(w)/h
                if ratio >= 0.9 and ratio <= 1.1:
                # Get the rectangle bounding the contour
                    rect = cv.minAreaRect(cnt)
                    center = self.get_center(rect)
                    if center[0] < 100 or center[0]>1000:
                        new_calibrator = Calibrator.CalibratorInfo(True, self.get_corner_points(rect), self.get_center(rect))
                        self.calibrators.append(new_calibrator)
                        #self.calibrator.is_detected = True
                        #self.calibrator.corner_points = self.get_corner_points(rect)
                        #self.calibrator.center = self.get_center(rect)


    def draw_boundary_and_center(self, frame):
        ''' Draw the boundary and center given the contours in a frame'''
        # if self.calibrator.is_detected is True and self.calibrator.center[0] > 800:
        #     cv.polylines(frame, [self.calibrator.corner_points], True, (255, 255, 0), 2)
        #     self.draw_center(frame)
        for each_calib in self.calibrators:
            cv.polylines(frame, [each_calib.corner_points], True, (255,255,0),2)
            self.draw_center(frame, each_calib)

    def draw_area(self, frame):
        ''' Fill out the area of rectangle with green color'''
        if self.calibrator.is_detected is True:
            cv.drawContours(frame,[self.calibrator.corner_points],0,(0,0,255),2)

    def get_center(self, rect):
        '''Find the center points of all rectangle from a frame'''
        # Unpack the rectangle information
        (center_x, center_y), (width, height), angle = rect
        center = (int(center_x), int(center_y))

        return center

    def get_corner_points(self, rect):
        '''Return corner points of the rectangle'''
        box = cv.boxPoints(rect)
        box = np.int0(box)

        return box

    def draw_center(self, frame, rect):
        '''Draw center point on a frame'''
        center = rect.center
        cv.circle(frame, center, 5, (0, 255, 0), -1)
        cv.putText(img=frame, text=f'{center}', org=center, fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(
            0, 0, 255), thickness=1)

    def clear_calibrator(self):
        #self.calibrator.is_detected = False
        self.calibrators.clear()

    def get_rect_dimension(self):
        ''' Return a ratio of px/mm'''
        ratio = (self.calibrator.corner_points[2][0]-self.calibrator.corner_points[0][0]) / RECT_SIDE_LENGTH
        return ratio