"""
This module implements a Rock, Paper, Scissors game using hand gestures.
"""

# pylint: disable=import-error
import random
import base64
import mediapipe
from flask import Flask
import pymongo
from pymongo import MongoClient
import cv2
import numpy as np

moves = ["Rock", "Paper", "Scissors"]
wins = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

# ---------------- DB -----------------

app = Flask(__name__)


def connect_to_mongo():
    """
    Connects to MongoDB and returns the client.

    Returns:
        MongoClient: MongoDB client.
    """
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
    """
    Inserts a result document into the MongoDB collection.

    Args:
        result (dict): Result document to be inserted.
    """
    collection.insert_one(result)


def print_collection_contents():
    """
    Prints the contents of the MongoDB collection.
    """
    cursor = collection.find()

    print("Contents of the MongoDB collection:")
    for document in cursor:
        # Use get() method to safely access the fields
        player_gesture_content = document.get("playerGesture", "N/A")
        comp_gesture_content = document.get("compGesture", "N/A")
        winner_content = document.get("winner", "N/A")

        print(
            f"Player Gesture: {player_gesture_content},"
            f"Comp Gesture: {comp_gesture_content}, Winner: {winner_content}"
        )


def print_one(document):
    """
    Prints details of a single document.

    Args:
        document (dict): Document to be printed.
    """
    player_gesture_content_one = document.get("playerGesture", "N/A")
    comp_gesture_content_one = document.get("compGesture", "N/A")
    winner_content_one = document.get("winner", "N/A")
    print(
        f"Player Gesture: {player_gesture_content_one},"
        f"Comp Gesture: {comp_gesture_content_one}, Winner: {winner_content_one}",
        flush=True,
    )


def print_raw_collection_contents():
    """
    Prints the contents of the RAW MongoDB collection.
    """
    cursor = collection_raw.find()

    print("Contents of the RAW collection:")
    for document in cursor:
        # Use get() method to safely access the fields
        document_id = document.get("_id", "N/A")
        print(f"id: {document_id}")


# ---------------- GAME ------------------
# decode


def decode_photo_data_url(photo_data_url):
    """
    Decodes the photo data URL and returns the image frame.

    Args:
        photo_data_url (str): Photo data URL.

    Returns:
        np.ndarray: Decoded image frame.
    """
    _, encoded_data = photo_data_url.split(",", 1)

    # Decode the Base64-encoded data
    image_data = base64.b64decode(encoded_data)

    image_array = np.frombuffer(image_data, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return frame


# ---------------


def get_comp_move():
    """
    Generates a random move for the computer.

    Returns:
        str: Computer's move.
    """
    comp = random.randint(0, 2)
    return moves[comp]


def calculate_game_state(comp, move):
    """
    Calculates the game state based on computer and player moves.

    Args:
        comp (str): Computer's move.
        move (str): Player's move.

    Returns:
        int: Game state (-1: gesture not detected, 0: tie, 1: player win, 2: computer win).
    """
    if move not in wins:
        return -1  # gesture not detected

    if comp == move:
        return 0  # tie

    if wins[move] == comp:
        return 1  # player win

    return 2  # computer win


def get_finger_status(hand_landmarks, finger_name):
    """
    Gets the status of a finger based on hand landmarks.

    Args:
        hands_module: Mediapipe Hands module.
        hand_landmarks: Hand landmarks data.
        finger_name (str): Name of the finger.

    Returns:
        bool: True if finger is up, False otherwise.
    """
    finger_id_map = {"INDEX": 8, "MIDDLE": 12, "RING": 16, "PINKY": 20}

    finger_tip_y = hand_landmarks.landmark[finger_id_map[finger_name]].y
    # finger_dip_y = hand_landmarks.landmark[finger_id_map[finger_name] - 1].y
    finger_mcp_y = hand_landmarks.landmark[finger_id_map[finger_name] - 2].y

    return finger_tip_y < finger_mcp_y


def get_thumb_status(hands_module, hand_landmarks):
    """
    Gets the status of the thumb based on hand landmarks.

    Args:
        hands_module: Mediapipe Hands module.
        hand_landmarks: Hand landmarks data.

    Returns:
        bool: True if thumb is up, False otherwise.
    """
    thumb_tip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP].x
    thumb_mcp_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 2].x
    thumb_ip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 1].x

    return thumb_tip_x > thumb_ip_x > thumb_mcp_x


def analyze_image(decoded_image):
    """
    Analyzes the hand gesture in the image and determines the corresponding move.

    Args:
        decoded_image: Decoded image frame.

    Returns:
        str: Recognized move ("Rock", "Paper", "Scissors", or "UNKNOWN").
    """
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
        except cv2.error as cv2_ex:
            print(f"OpenCV Error: {cv2_ex}")
            return "UNKNOWN"

        move = "UNKNOWN"
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                current_state = ""
                thumb_status = get_thumb_status(hands_module, hand_landmarks)
                current_state += "1" if thumb_status else "0"

                index_status = get_finger_status(hand_landmarks, "INDEX")
                current_state += "1" if index_status else "0"

                middle_status = get_finger_status(hand_landmarks, "MIDDLE")
                current_state += "1" if middle_status else "0"

                ring_status = get_finger_status(hand_landmarks, "RING")
                current_state += "1" if ring_status else "0"

                pinky_status = get_finger_status(hand_landmarks, "PINKY")
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
    # pylint: disable=invalid-name
    doc_count = 0
    while True:
        new_photo = None
        try:
            res = collection_raw.find().sort("_id", -1)

            if collection_raw.count_documents({}) > doc_count:
                doc_count += 1
                latest_document = res[0]
                latest_document_id = str(latest_document.get("_id", None))
                new_photo = latest_document
            else:
                new_photo = None  # or any other value indicating no result

        except pymongo.errors.PyMongoError as ex:
            print(f"Error getting new input: {ex}")
            new_photo = None

        if new_photo:
            photo_url = new_photo.get("photoDataUrl", None)
            decoded_image_main = decode_photo_data_url(photo_url)
            player_gesture = analyze_image(decoded_image_main)
            comp_gesture = get_comp_move()
            winner = calculate_game_state(comp_gesture, player_gesture)
            to_store = {
                "playerGesture": player_gesture,
                "compGesture": comp_gesture,
                "winner": winner,
                "image": photo_url,
            }
            insert_result_to_db(to_store)
            print_one(to_store)
        # Sleep or wait for some time before querying again to avoid continuous polling
        # time.sleep(2)
