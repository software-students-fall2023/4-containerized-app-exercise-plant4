# source: https://github.com/ramdas-codes/fncoder/tree/main/Python/Intermediate/RockPaperScissors
# program has been modified from the original code to fit purposes of the project

import cv2
import mediapipe
import time
import random

def calculate_game_state(move):
    moves = ["Rock", "Paper", "Scissors"]
    wins = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}
    selected = random.randint(0, 2)
    print("Computer played " + moves[selected])

    if moves[selected] == move:
        return 0, moves[selected]

    if wins[move] == moves[selected]:
        return 1, moves[selected]

    return -1, moves[selected]

def get_finger_status(hands_module, hand_landmarks, finger_name):
    finger_id_map = {'INDEX': 8, 'MIDDLE': 12, 'RING': 16, 'PINKY': 20}
    
    finger_tip_y = hand_landmarks.landmark[finger_id_map[finger_name]].y
    finger_dip_y = hand_landmarks.landmark[finger_id_map[finger_name] - 1].y
    finger_mcp_y = hand_landmarks.landmark[finger_id_map[finger_name] - 2].y
    
    return finger_tip_y < finger_mcp_y

def get_thumb_status(hands_module, hand_landmarks):
    thumb_tip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP].x
    thumb_mcp_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 2].x
    thumb_ip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 1].x
    
    return thumb_tip_x > thumb_ip_x > thumb_mcp_x

def start_video():
    hands_module = mediapipe.solutions.hands

    capture = cv2.VideoCapture("video.mp4")  # Use the local video file

    with hands_module.Hands(static_image_mode=False, min_detection_confidence=0.7,
                            min_tracking_confidence=0.4, max_num_hands=2) as hands:
        while True:
            ret, frame = capture.read()
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            move = "UNKNOWN"
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    current_state = ""
                    thumb_status = get_thumb_status(hands_module, hand_landmarks)
                    current_state += "1" if thumb_status else "0"

                    index_status = get_finger_status(hands_module, hand_landmarks, 'INDEX')
                    current_state += "1" if index_status else "0"

                    middle_status = get_finger_status(hands_module, hand_landmarks, 'MIDDLE')
                    current_state += "1" if middle_status else "0"

                    ring_status = get_finger_status(hands_module, hand_landmarks, 'RING')
                    current_state += "1" if ring_status else "0"

                    pinky_status = get_finger_status(hands_module, hand_landmarks, 'PINKY')
                    current_state += "1" if pinky_status else "0"

                    if current_state == "00000":
                        move = "Rock"
                    elif current_state == "11111":
                        move = "Paper"
                    elif current_state == "01100":
                        move = "Scissors"
                    else:
                        move = "UNKNOWN"

                print("Recognized gesture: " + move)

            if cv2.waitKey(1) == 27:
                break

    capture.release()

if __name__ == "__main__":
    start_video()

if __name__ == "__main__":
    start_video()