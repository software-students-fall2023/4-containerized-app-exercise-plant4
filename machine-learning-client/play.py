import cv2
import mediapipe
import random

moves = ["Rock", "Paper", "Scissors"]
wins = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

# ---------------- DB -----------------

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

def insert_result_to_db(result):
    collection.insert_one(result)

def print_collection_contents():
    cursor = collection.find()

    print("Contents of the MongoDB collection:")
    for document in cursor:
        # Use get() method to safely access the fields
        player_gesture = document.get('playerGesture', 'N/A')
        comp_gesture = document.get('compGesture', 'N/A')
        winner = document.get('winner', 'N/A')
        image_base64 = document.get('image', None)

        print(f"Player Gesture: {player_gesture}, Comp Gesture: {comp_gesture}, Winner: {winner}")



# ---------------- GAME ------------------

import base64
from io import BytesIO
from PIL import Image
import numpy as np

def decode_photo_data_url(photo_data_url):
    _, encoded_data = url.split(',', 1)

    # Decode the Base64-encoded data
    image_data = base64.b64decode(encoded_data)

    image_array = np.frombuffer(image_data, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return frame

# Example usage:

# Now, 'decoded_image' contains the image in a format that OpenCV can handle


# ---------------

def get_comp_move():
    comp = random.randint(0, 2)
    return moves[comp]

def calculate_game_state(comp, move):

    if move not in wins:
        return -1 # gesture not detected
    
    if comp == move:
        return 0 # tie

    if wins[move] == comp:
        return 1 # player win

    return 2 # computer win

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

def analyze_image(decoded_image):
    hands_module = mediapipe.solutions.hands

    # frame = cv2.imread(decoded_image)
    frame = decoded_image

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
    import json
    with open('message.txt', 'r') as file:
        file_content = file.read()

    # Parse the JSON content
    json_data = json.loads(file_content)

    # Access and print the content of the 'PhotoUrl' key
    photoBase64 = json_data["photoDataUrl"]


    with open('url.txt', 'r') as file:
        url = file.read()

    decoded_image = decode_photo_data_url(url)
    playerGesture = analyze_image(decoded_image)
    compGesture = get_comp_move()
    winner = calculate_game_state(compGesture, playerGesture)

    insert_result_to_db({"playerGesture": playerGesture, 
                         "compGesture": compGesture,
                         "winner": winner,
                         "image": url})

    # print("Final recognized gesture:", playerGesture)
    print_collection_contents()
