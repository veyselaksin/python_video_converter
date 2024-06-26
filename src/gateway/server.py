import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from flask import jsonify

app = Flask(__name__)

app.config['MONGO_URI'] = os.environ['MONGO_URI']

mongo_video = PyMongo(app, uri="mongodb://host.minikube.internal:27017/videos")

mongo_mp3 = PyMongo(app, uri="mongodb://host.minikube.internal:27017/mp3s")

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)


connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

@app.route('/login', methods=['POST'])
def login():
    token, status = access.login(request)
    
    return jsonify(token), status

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
        err = util.upload(fs_videos, file, channel, access)

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

    file, err = util.download(fs_videos, file_id, access)

    if err:
        return err
    
    return file

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)