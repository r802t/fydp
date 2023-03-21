import cv2
import mediapipe as mp
import time

class HandDetector:

    def __init__(self) -> None:
        self.mp_hands = mp.solutions.hands.Hands(
                        max_num_hands=1,
                        min_detection_confidence=0.8, 
                        min_tracking_confidence=0.5)
        self.finger_on_phone = False
        self.is_detected = False
        self.pos= [0,0]
        self.last_pos = [0,0]
        self.last_time = time.time()

    def detect_finger_tip(self, frame):   
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                self.pos = [int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])]
                self.is_detected = True
        else:
            self.pos = [0,0]
            self.last_pos = [0,0]
            self.is_detected = False


    def draw_finger_tip(self, frame):
        cv2.circle(frame, self.pos, 5, (0, 255, 0), -1)
    
    def is_finger_stay_still(self):
        ''' Detect if a finger is at the same place for more than 2 seconds '''
        if self.pos == [0,0]:
            return False 
        if abs(self.last_pos[0]-self.pos[0]) <= 30 and abs(self.last_pos[1]-self.pos[1]) <= 30:
            current_time = time.time()
            elapsed_time = current_time - self.last_time
            if elapsed_time > 3.0:
                #print("Finger has been in the same position for 3 seconds")
                return True
            return False
        else:
            self.last_pos = self.pos
            self.last_time = time.time()
            return False
        
    def clear_finger(self):
        self.pos = None
