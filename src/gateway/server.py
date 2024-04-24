import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

app = Flask(__name__)

app.config['MONGO_URI'] = os.environ['MONGO_URI']

mongo = PyMongo(app)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

@app.route('/login', methods=['POST'])
def login():
    token, err = access.login(request)

    if err:
        return err
    
    return token

@app.route('/upload', methods=['POST'])
def upload():
    access, error = validate.token(request)

    if error:
        return error
    
    access = json.loads(access)

    if access["admin"]:
        if "file" not in request.files:
            return {"message": "File is missing"}, 400
    
    for file in request.files.getlist("file"):
        err = util.upload(fs, file, channel, access)

        if err:
            return err
    
    return {"message": "Files uploaded successfully"}, 200

@app.route('/download', methods=['GET'])
def download():
    access, error = validate.token(request)

    if error:
        return error
    
    access = json.loads(access)

    if access["admin"]:
        return {"message": "Admins are not allowed to download files"}, 403

    file_id = request.args.get("file_id")

    if not file_id:
        return {"message": "File ID is missing"}, 400

    file, err = util.download(fs, file_id, access)

    if err:
        return err
    
    return file

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)