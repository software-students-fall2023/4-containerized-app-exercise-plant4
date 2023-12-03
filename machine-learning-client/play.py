import cv2
import mediapipe

# --------- DB

from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from retry import retry
import pymongo.errors

app = Flask(__name__)

@retry(pymongo.errors.ServerSelectionTimeoutError, delay=1, tries=30)
def connect_to_mongo():
    return MongoClient("mongodb://mongodb:27017/")

# MongoDB configuration
client = connect_to_mongo()
db = client["mydatabase"]

# Check if the collection exists
if "mycollection" not in db.list_collection_names():
    # Create the collection if it doesn't exist
    db.create_collection("mycollection")

collection = db["mycollection"]

def insert_result_to_db(move):
    collection.insert_one({'gesture': move})

def print_collection_contents():
    cursor = collection.find()

    print("Contents of the MongoDB collection:")
    for document in cursor:
        print(document['gesture'])


# --------- DB



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

def analyze_image(image_path):
    hands_module = mediapipe.solutions.hands

    frame = cv2.imread(image_path)

    with hands_module.Hands(static_image_mode=True, min_detection_confidence=0.7,
                            min_tracking_confidence=0.4, max_num_hands=2) as hands:
        try:
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except cv2.error as e:
            print(f"OpenCV Error: {e}")
            return "UNKNOWN"

        move = "UNKNOWN"
        if results and results.multi_hand_landmarks:
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

                # print("Recognized gesture: " + move)

    return move

if __name__ == "__main__":
    image_path = "hand.png"
    result = analyze_image(image_path)
    insert_result_to_db(result)
    print("Final recognized gesture:", result)
    print_collection_contents()
