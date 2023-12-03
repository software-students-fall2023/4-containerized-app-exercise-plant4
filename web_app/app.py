from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import pymongo.errors

app = Flask(__name__)


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
    return render_template("index.html")


@app.route("/save_photo", methods=["POST"])
def save_photo():
    data = request.json
    photo_data_url = data.get("photoDataUrl")

    # SAVE PHOTO TO DATABASE
    collection.insert_one({"photoDataUrl": photo_data_url, "processed": False})

    return "Photo saved successfully!"


@app.route("/view_data")
def view_data():
    # THIS NEEDS TO BE CHANGED EVENTUALLY EVEN ML DATA IS RETURNED!!!
    collection2 = db["mlresults"]
    data_from_mongo = list(collection2.find())

    return render_template("view_data.html", data=data_from_mongo)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
