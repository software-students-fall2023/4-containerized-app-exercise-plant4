import pytest
from unittest.mock import patch, MagicMock, Mock
import cv2
import mediapipe
import numpy as np
# # # test_play.py
# from unittest.mock import Mock, patch

# # sys.path.append('../')  # Adjust the path accordingly
# print("Current working directory:", os.getcwd())
# print("Contents of the current directory:", os.listdir())

# from play import get_comp_move, calculate_game_state, analyze_image
from play import get_comp_move, calculate_game_state, analyze_image, get_thumb_status, get_finger_status,decode_photo_data_url

def test_get_comp_move():
    moves = ["Rock", "Paper", "Scissors"]
    comp_move = get_comp_move()
    # print("Current working directory:", os.getcwd())
    # print("Contents of the current directory:", os.listdir())

    assert comp_move in moves

def test_calculate_game_state():
    # Test tie scenario
    result = calculate_game_state("Rock", "Rock")
    assert result == 0

    # Test player win scenario
    result = calculate_game_state("Rock", "Paper")
    assert result == 1

    # Test computer win scenario
    result = calculate_game_state("Paper", "Rock")
    assert result == 2

    # Test invalid move scenario
    result = calculate_game_state("Rock", "Invalid")
    assert result == -1

# Testing analyze_image
@patch("mediapipe.solutions.hands.Hands")
def test_analyze_image(mock_hands):
    decoded_image = np.zeros((100, 100, 3), dtype=np.uint8)

    # Mocking hands.process method
    hands_instance = mock_hands.return_value
    hands_instance.process.return_value.multi_hand_landmarks = [MagicMock()]
    
    move = analyze_image(decoded_image)
    assert move == "UNKNOWN"

@staticmethod
def create_mock_new_photo(photo_data_url):
    return {"photoDataUrl": photo_data_url}

def test_decode_photo_data_url():
    # Assume 'url.txt' contains the Base64-encoded image URL
    with open("machine_learning_client/url.txt", "r") as file:
        photo_url = file.read()

    expected_frame = Mock()
    with patch("cv2.imdecode", return_value=expected_frame) as mock_imdecode:
        frame = decode_photo_data_url(photo_url)

    mock_imdecode.assert_called_once()
    assert frame == expected_frame



def test_integration():
    # Integration test using real data
    with open("machine_learning_client/url.txt", "r") as file:
        photo_url = file.read()

    new_photo = create_mock_new_photo(photo_url)
    decoded_image = decode_photo_data_url(new_photo["photoDataUrl"])
    move = analyze_image(decoded_image)

    assert isinstance(move, str)  # Adjust based on your expectations

# def test_get_finger_status():
#     hands_module = Mock()
#     hand_landmarks = Mock()

#     # Configure hand_landmarks Mock to have the necessary attributes
#     hand_landmarks.landmark = {
#         8: Mock(y=0.5),  # Assuming 0.5 as an example value
#         # ... configure other landmarks as needed
#         7: Mock(y=0.4),  # Add the required key with a Mock value

#     }

#     with patch("play.get_thumb_status", return_value=True):
#         status = get_finger_status(hands_module, hand_landmarks, "INDEX")

#     assert status is True

# def test_get_thumb_status():
#     hands_module = Mock()
#     hand_landmarks = Mock()

#     # Configure hand_landmarks Mock to have the necessary attributes
#     hand_landmarks.multi_hand_landmarks = [Mock()]
#     hand_landmarks.multi_hand_landmarks[0].landmark = {
#         hands_module.HandLandmark.THUMB_TIP: Mock(x=0.8),  # Assuming 0.8 as an example value
#         # ... configure other landmarks as needed
#     }

#     status = get_thumb_status(hands_module, hand_landmarks)

#     assert status is True

# def test_analyze_image():
#     hands_module = Mock()
#     decoded_image = Mock()
#     hands_module.Hands.return_value.process.return_value.multi_hand_landmarks = [Mock()]

#     move = analyze_image(decoded_image)

#     assert move == "Scissors"  # Adjust based on your mock values


# def test_get_finger_status(self):
#     hand_landmarks = self.create_mock_hand_landmarks()
#     finger_status = get_finger_status(mediapipe.solutions.hands, hand_landmarks, "INDEX")
#     assert finger_status is True  



# def test_get_finger_status(self):
#     hand_landmarks = self.create_mock_hand_landmarks()
#     finger_status = get_finger_status(mediapipe.solutions.hands, hand_landmarks, "INDEX")
#     assert finger_status is True  # Adjust based on your mock values

# @patch("mediapipe.solutions.hands.Hands")
# def test_get_thumb_status(mock_hands):
#     hands_module = mock_hands.return_value
#     hand_landmarks = MagicMock()

#     # Mocking landmark positions for testing
#     hand_landmarks.landmark = {
#         hands_module.HandLandmark.THUMB_TIP: MagicMock(x=20),  # Thumb tip
#         hands_module.HandLandmark.THUMB_MCP: MagicMock(x=15),  # MCP joint
#         hands_module.HandLandmark.THUMB_IP: MagicMock(x=10),   # IP joint
#     }

#     with patch("play.get_thumb_status", wraps=get_thumb_status):
#         # Test for a thumb extended
#         thumb_status = get_thumb_status(hands_module, hand_landmarks)
#         assert thumb_status is True

#         # Test for a thumb not extended
#         hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP].x = 5
#         thumb_status = get_thumb_status(hands_module, hand_landmarks)
#         assert thumb_status is False


# #----------------


# @pytest.fixture
# def dummy_image():
#     return None  # Replace this with an actual dummy image if needed

# def test_get_comp_move():
#     moves = ["Rock", "Paper", "Scissors"]
#     comp_move = get_comp_move()
#     assert comp_move in moves

# def test_calculate_game_state():
#     # Test tie scenario
#     result = calculate_game_state("Rock", "Rock")
#     assert result == 0

#     # Test player win scenario
#     result = calculate_game_state("Paper", "Rock")
#     assert result == 1

#     # Test computer win scenario
#     result = calculate_game_state("Rock", "Paper")
#     assert result == 2

#     # Test invalid move scenario
#     result = calculate_game_state("InvalidMove", "Rock")
#     assert result == -1

# @patch('play.cv2.imread')
# @patch('play.mediapipe.solutions.hands.Hands.process')
# def test_analyze_image(mock_cv2_imread, mock_hands_process, dummy_image):
#     # Mocking cv2.imread to return a dummy image
#     mock_cv2_imread.return_value = dummy_image

#     # Mocking mediapipe.solutions.hands.Hands.process to return dummy results
#     mock_hands_process.return_value.multi_hand_landmarks = [None]

#     # Test with a dummy image
#     result = analyze_image(dummy_image)
#     assert result == "UNKNOWN"
