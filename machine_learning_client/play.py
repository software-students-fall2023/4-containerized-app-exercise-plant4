import cv2
import mediapipe
import random
from bson import ObjectId

# decode
import base64
from io import BytesIO
from PIL import Image
import numpy as np

moves = ["Rock", "Paper", "Scissors"]
wins = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

# ---------------- DB -----------------

# Check if MongoDB-related imports should be included
import os

if os.environ.get("CONNECT_TO_MONGODB", "").lower() == "true":
    from flask import Flask
    from pymongo import MongoClient

    app = Flask(__name__)

    def connect_to_mongo():
        print("connected", flush=True)
        return MongoClient("mongodb://mongodb:27017/")

    # MongoDB configuration
    client = connect_to_mongo()
    db = client["mydatabase"]

    # Check if the collection exists
    if "mlresults" not in db.list_collection_names():
        # Create the collection if it doesn't exist
        db.create_collection("mlresults")
    collection = db["mlresults"]

    # check if the collection exists
    if "mycollection" not in db.list_collection_names():
        # create the collection if it doesn't exist
        db.create_collection("mycollection")

    collection_raw = db["mycollection"]

    def insert_result_to_db(result):
        collection.insert_one(result)

    def print_one(document):
        player_gesture = document.get("playerGesture", "N/A")
        comp_gesture = document.get("compGesture", "N/A")
        winner = document.get("winner", "N/A")
        image_base64 = document.get("image", None)

        print(
            f"Player Gesture: {player_gesture}, Comp Gesture: {comp_gesture}, Winner: {winner}",
            flush=True,
        )

else:
    # Define placeholders or mock functions when not connecting to MongoDB
    app = None
    db = None
    collection = None
    collection_raw = None

    def insert_result_to_db(result):
        pass

    def print_one(document):
        pass


# ---------------- GAME ------------------
# decode


def decode_photo_data_url(photo_data_url):
    _, encoded_data = photo_data_url.split(",", 1)

    # Decode the Base64-encoded data
    image_data = base64.b64decode(encoded_data)

    image_array = np.frombuffer(image_data, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return frame


# ---------------


def get_comp_move():
    comp = random.randint(0, 2)
    return moves[comp]


def calculate_game_state(comp, move):
    if move not in wins:
        return -1  # gesture not detected

    if comp == move:
        return 0  # tie

    if wins[move] == comp:
        return 1  # player win

    return 2  # computer win


def get_finger_status(hands_module, hand_landmarks, finger_name):
    finger_id_map = {"INDEX": 8, "MIDDLE": 12, "RING": 16, "PINKY": 20}

    finger_tip_y = hand_landmarks.landmark[finger_id_map[finger_name]].y
    finger_dip_y = hand_landmarks.landmark[finger_id_map[finger_name] - 1].y
    finger_mcp_y = hand_landmarks.landmark[finger_id_map[finger_name] - 2].y

    return finger_tip_y < finger_mcp_y


def get_thumb_status(hands_module, hand_landmarks):
    try:
        thumb_tip_x = (
            hand_landmarks.multi_hand_landmarks[0]
            .landmark[hands_module.HandLandmark.THUMB_TIP]
            .x
        )
        thumb_mcp_x = (
            hand_landmarks.multi_hand_landmarks[0]
            .landmark[hands_module.HandLandmark.THUMB_MCP]
            .x
        )
        thumb_ip_x = (
            hand_landmarks.multi_hand_landmarks[0]
            .landmark[hands_module.HandLandmark.THUMB_IP]
            .x
        )

        return thumb_tip_x > thumb_ip_x > thumb_mcp_x
    except (AttributeError, IndexError):
        # Handle cases where landmarks are not detected or not present
        return False


def analyze_image(decoded_image):
    hands_module = mediapipe.solutions.hands

    # frame = cv2.imread(decoded_image)
    frame = decoded_image

    with hands_module.Hands(
        static_image_mode=True,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.4,
        max_num_hands=2,
    ) as hands:
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

                index_status = get_finger_status(hands_module, hand_landmarks, "INDEX")
                current_state += "1" if index_status else "0"

                middle_status = get_finger_status(
                    hands_module, hand_landmarks, "MIDDLE"
                )
                current_state += "1" if middle_status else "0"

                ring_status = get_finger_status(hands_module, hand_landmarks, "RING")
                current_state += "1" if ring_status else "0"

                pinky_status = get_finger_status(hands_module, hand_landmarks, "PINKY")
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
    docCt = 0
    while True:
        new_photo = None
        try:
            res = collection_raw.find().sort("_id", -1)

            if collection_raw.count_documents({}) > docCt:
                docCt += 1
                latest_document = res[0]
                latest_document_id = str(latest_document["_id"])
                new_photo = latest_document
            else:
                new_photo = None  # or any other value indicating no result

        except Exception as e:
            print(f"Error getting new input: {e}")
            new_photo = None

        if new_photo:
            photo_url = new_photo["photoDataUrl"]
            decoded_image = decode_photo_data_url(photo_url)
            playerGesture = analyze_image(decoded_image)
            compGesture = get_comp_move()
            winner = calculate_game_state(compGesture, playerGesture)
            to_store = {
                "playerGesture": playerGesture,
                "compGesture": compGesture,
                "winner": winner,
                "image": photo_url,
            }
            insert_result_to_db(to_store)
            print_one(to_store)
