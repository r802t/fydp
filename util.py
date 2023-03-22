import pathlib
import cv2 as cv
import os
import random
import shutil

def count_img_in_folder(directory: str) -> int:
    num_img = 0
    for path in pathlib.Path(directory).iterdir():
        if path.is_file():
            num_img += 1
    return num_img

def capture_img(save_to_directory:str):
    video_capture = cv.VideoCapture(0)
    #num_img = count_img_in_folder(save_to_directory)
    num_img = 0
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
            img_name = f'{save_to_directory}/img_{num_img+1}.jpg'
            cv.imwrite(img_name, frame)
            num_img += 1

    video_capture.release()
    cv.destroyAllWindows()

def randomly_copy_img(src_path, dst_path, num_img, copy_label):
    img_src_folder = src_path #'/path/to/src_folder'
    img_dst_folder = dst_path+'\\validation_set' #'/path/to/dst_folder'
    remaining_folder = dst_path+'\\training_set'

    num_images_to_copy = num_img

    # get a list of all the images in the source folder
    img_files = [f for f in os.listdir(img_src_folder+'\\images') if f.startswith('img_')]

    # select `num_images_to_copy` random images from the list
    selected_imgs = random.sample(img_files, num_images_to_copy)

    # copy the selected images to the destination folder
    for img in selected_imgs:
        src_img_path = os.path.join(img_src_folder+'\\images', img)
        dst_img_path = os.path.join(img_dst_folder+'\\images', img)
        shutil.copy2(src_img_path, dst_img_path)

        if copy_label is True:
            label_file = img.replace('jpg','txt')
            src_label_path = os.path.join(img_src_folder+'\\labels', label_file)
            dst_label_path = os.path.join(img_dst_folder+'\\labels', label_file)
            shutil.copy2(src_label_path, dst_label_path)

    # move the remaining images and label files to the remaining folder
    for img in img_files:
        if img in selected_imgs:
            continue
        src_img_path = os.path.join(img_src_folder+'\\images', img)
        dst_img_path = os.path.join(remaining_folder+'\\images', img)
        shutil.copy2(src_img_path, dst_img_path)

        if copy_label is True:
            label_file = img.replace('jpg','txt')
            src_label_path = os.path.join(img_src_folder+'\\labels', label_file)
            dst_label_path = os.path.join(remaining_folder+'\\labels', label_file)
            shutil.copy2(src_label_path, dst_label_path)
