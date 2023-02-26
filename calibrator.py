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
        self.calibrator = super().CalibratorInfo(False, np.ndarray([]), tuple())

    def find_cal_ref(self, frame:np.ndarray):
        ''' Find all red rectangles in a given frame '''
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # # Define range of red color in HSV
        # lower_red_1 = np.array([0,25,20])
        # upper_red_1 = np.array([50,100,255])
        # lower_red_2 = np.array([160,100,20])
        # upper_red_2 = np.array([179,255,255])
        #Another set
        lower_red_1 = np.array([0, 50, 50])
        upper_red_1 = np.array([10, 255, 255])
        lower_red_2 = np.array([170, 50, 50])
        upper_red_2 = np.array([180, 255, 255])
        lower_mask = cv.inRange(hsv, lower_red_1, upper_red_1)
        upper_mask = cv.inRange(hsv, lower_red_2, upper_red_2)
        mask = lower_mask + upper_mask

        #At night only
        # lower_red = np.array([0,150,150])
        # upper_red = np.array([180,255,255])
        #mask = cv.inRange(hsv, lower_red, upper_red)

        # Find contours in the mask
        contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if 300 < cv.contourArea(cnt) < 850 : # adjust threshold if needed
                approx = cv.approxPolyDP(cnt, 0.02*cv.arcLength(cnt,True),True)
                if len(approx) == 4:
                    x, y, w, h = cv.boundingRect(cnt)
                    ratio = float(w)/h
                    if ratio >= 0.9 and ratio <= 1.1:
                    # Get the rectangle bounding the contour
                        rect = cv.minAreaRect(cnt)
                        self.calibrator.is_detected = True
                        self.calibrator.corner_points = self.get_corner_points(
                            rect)
                        self.calibrator.center = self.get_center(
                            rect)


    def draw_boundary_and_center(self, frame):
        ''' Draw the boundary and center given the contours in a frame'''
        if self.calibrator.is_detected is True:
            cv.polylines(frame, [self.calibrator.corner_points], True, (255, 255, 0), 2)
            self.draw_center(frame)


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

    def draw_center(self, frame):
        '''Draw center point on a frame'''
        center = self.calibrator.center
        cv.circle(frame, center, 5, (0, 255, 0), -1)
        cv.putText(img=frame, text=f'{center}', org=center, fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(
            0, 255, 0), thickness=1)

    def clear_calibrator(self):
        self.calibrator.is_detected = False

    def get_rect_dimension(self):
        ''' Return a ratio of px/mm'''
        ratio = (self.calibrator.corner_points[2][0]-self.calibrator.corner_points[0][0]) / RECT_SIDE_LENGTH
        return ratio


class QRCodeDetector(Calibrator):
    
    def __init__(self):
        self.qr_code_detector = cv.QRCodeDetector()
        self.calibrator_info = super().CalibratorInfo()
        
    def find_cal_ref(self, frame:np.ndarray):
        '''Detect QR code in a frame'''
        img = cv.imread(frame)

        is_detected, points = self.qr_code_detector.detect(img)
        #TODO: get qr_code center
        corner_points = self.points_to_corner_points(is_detected, points)
        center = self.get_center(points)
        self.calibrator_info.is_detected = is_detected
        self.calibrator_info.corner_points = corner_points
        self.calibrator_info.center = center

        if self.calibrator_info.is_detected:
            print("QR code detected, data:")
        else:
            print("QR code not detected")
        return self.calibrator_info

    def points_to_corner_points(is_detected, points):
        '''Convert raw points to corner points'''
        if is_detected:
            return np.array(points).reshape((-1,1,2)).astype(np.int32)
        else:
            return np.empty((1,4,2))

    def draw_boundary_and_center(self, frame):
        '''Draw boundary around the QR code'''
        cv.drawContours(frame, [self.calibrator_info.corner_points], -1, (0, 0, 255), 2)
        center = self.calibrator_info.center
        cv.circle(frame, center, 5, (0,255,0), -1)
        cv.putText(img=frame, text=f'{center}', org=center, fontFace=cv.FONT_HERSHEY_TRIPLEX, fontScale=0.5, color=(0, 255, 0),thickness=1)   
        return frame


    def get_center(points):
        if points is not None:
            # calculate the center point
            corner_centers = np.mean(points, axis=0)
            # convert to integers
            corner_centers = np.int0(corner_centers)
            avg_x = (corner_centers[0][0]+corner_centers[1][0]+corner_centers[2][0]+corner_centers[3][0])/4
            avg_y = (corner_centers[0][1]+corner_centers[1][1]+corner_centers[2][1]+corner_centers[3][1])/4
            center = (int(avg_x), int(avg_y))
        else:
            print("No QR Code detected")
        
        return center
    
    def detect_live_qr(self):
        video_capture = cv.VideoCapture(0)
        if video_capture.isOpened(): # try to get the first frame
            is_capturing, frame = video_capture.read()
        else:
            is_capturing = False
            print('Camera not connected')
            return

        while is_capturing:
            is_capturing, frame = video_capture.read() # capture new frame
            self.calibrator_info.is_detected, points = self.qr_code_detector.detect(frame)
            if self.calibrator_info.is_detected:
                frame = self.draw_boundary_and_center(frame)
            cv.imshow("Live capture", frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
           
        video_capture.release()
        cv.destroyAllWindows()
