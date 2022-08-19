import torch
from matplotlib import pyplot as plt
import numpy as np
import cv2 as cv
import os
import pathlib
import serial
import time

TRAINING_IMG_DIR = os.getcwd()+'\Training set'
TESTING_IMG_DIR = os.getcwd()+'\Testing set'

arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)

def count_img_in_folder(directory: str) -> int:
    num_img = 0
    for path in pathlib.Path(directory).iterdir():
        if path.is_file():
            num_img += 1
    return num_img

def capture_live_video(save_to_directory:str):
    video_capture = cv.VideoCapture(0)
    num_img = count_img_in_folder(save_to_directory)
    if video_capture.isOpened(): # try to get the first frame
        rval, frame = video_capture.read()
    else:
        rval = False
        print('Camera not connected')
        return
    while rval:
        cv.imshow("preview", frame)
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

def load_model():
    ''' Load model from torch hub '''
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    model.classes = [67] # only detect phones
    return model

def detect_phone(model):
    ''' Apply model to detect phones '''
    img = "C:\\Users\\a7568\\Desktop\\UW\\Project\\GoogleDrive\\training_set\\img_1.jpg"
    results = model(img)
    get_center_point(results)

def get_center_point(image):
    ''' Calculate center point from detected image '''
    x_midpoint = int(image.xyxy[0][0][0]+image.xyxy[0][0][2])
    y_midpoint = int(image.xyxy[0][0][1]+image.xyxy[0][0][3])
    center = [x_midpoint, y_midpoint]
    print(center)

def write_to_arduino(coordinate):
    arduino.write(bytes(coordinate, 'utf-8'))
    time.sleep(0.05)

def main():
    ''' This function is used to run the main program '''
    print("Hello world")
    model = load_model()
    detect_phone(model)

if __name__ == "__main__":
    main()