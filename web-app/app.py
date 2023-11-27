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

@app.route('/')
def index():
    # Retrieve data from MongoDB
    data = collection.find()
    return render_template('index.html', data=data)

@app.route('/add', methods=['POST'])
def add():
    # Get text from the form
    text = request.form.get('text')

    # Insert text into MongoDB
    collection.insert_one({'text': text})

    # Redirect to the home page
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


