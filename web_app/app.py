"""
Backend for the web app.
"""

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import pymongo

app = Flask(__name__)

"""
    This will attempt connect to the database.

    Returns:
        client: MongoDB client.
    """


def connect_to_mongo():
    return MongoClient("mongodb://mongodb:27017/")


# MongoDB configuration
client = connect_to_mongo()
db = client["mydatabase"]

# check if the collection exists
if "mycollection" not in db.list_collection_names():
    # create the collection if it doesn't exist
    db.create_collection("mycollection")

collection = db["mycollection"]


@app.route("/")
def index():
    """
    This will render the index.html template for the main page.

    Returns:
        str: Rendeed HTML content.
    """
    return render_template("index.html")


@app.route("/save_photo", methods=["POST"])
def save_photo():
    """
    Send the initial unprocessed image to MongoDB.

    Returns:
        str: Message saying that send was successful.
    """
    data = request.json
    photo_data_url = data.get("photoDataUrl")

    # SAVE PHOTO TO DATABASE
    collection.insert_one({"photoDataUrl": photo_data_url, "processed": False})

    return "Photo saved successfully!"


@app.route("/view_data")
def view_data():
    """
    This will render the view_data.html template which shows the results after the ML client.

    Returns:
        str: Rendered HTML content.
    """
    # THIS NEEDS TO BE CHANGED EVENTUALLY EVEN ML DATA IS RETURNED!!!
    collection2 = db["mlresults"]
    data_from_mongo = list(collection2.find().sort("_id", pymongo.DESCENDING))

    return render_template("view_data.html", data=data_from_mongo)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
