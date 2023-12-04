import pytest
from unittest.mock import patch

# # # test_play.py
# # import sys
# # sys.path.append('../')  # Adjust the path accordingly

# from play import get_comp_move, calculate_game_state, analyze_image
from play import get_comp_move, calculate_game_state

def test_get_comp_move():
    moves = ["Rock", "Paper", "Scissors"]
    comp_move = get_comp_move()
    assert comp_move in moves

def test_calculate_game_state():
    # Test tie scenario
    result = calculate_game_state("Rock", "Rock")
    assert result == 0

    # Test player win scenario
    result = calculate_game_state("Paper", "Rock")
    assert result == 1

    # Test computer win scenario
    result = calculate_game_state("Rock", "Paper")
    assert result == 2

    # Test invalid move scenario
    result = calculate_game_state("InvalidMove", "Rock")
    assert result == -1


#----------------


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
