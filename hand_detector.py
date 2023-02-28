import cv2
import mediapipe as mp

class HandDetector:

    def __init__(self) -> None:
        self.mp_hands = mp.solutions.hands.Hands(
                        max_num_hands=1,
                        min_detection_confidence=0.8, 
                        min_tracking_confidence=0.5)
        self.x = 0
        self.y = 0
        self.finger_on_phone = False

    def detect_finger_tip(self, frame):   
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_hands.process(frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                self.x, self.y = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])


    def draw_finger_tip(self, frame):
        cv2.circle(frame, (self.x, self.y), 5, (0, 255, 0), -1)
    