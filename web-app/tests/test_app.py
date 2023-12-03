import json
import pytest
from flask import url_for
import base64
import sys

from web_app.app import app, collection

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Webcam Photo App' in response.data


def generate_base64_image_data():
    image_path = "/pikachu.png"
    
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    return f"data:image/png;base64,{image_data}"

def test_save_photo_route(client):
    photo_data_url =  generate_base64_image_data()
    response = client.post('/save_photo', json={'photoDataUrl': photo_data_url})
    assert response.status_code == 200
    assert b'Photo saved successfully' in response.data

    # Check if the data is saved in the collection
    saved_data = collection.find_one({'photoDataUrl': photo_data_url})
    assert saved_data is not None
    assert saved_data['processed'] is False  # Check the default value

def test_view_data_route(client):
    response = client.get('/view_data')
    assert response.status_code == 200
    assert b'View Data' in response.data

# def test_beforeunload_route(client):
#     response = client.get('/beforeunload')
#     assert response.status_code == 200
#     assert b'' in response.data  # Assuming this route doesn't return any content

