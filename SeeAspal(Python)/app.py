#6D 18090122 Dimas Ilham Mardiyanto
#6D 18090139 Alfan Nur Rabbani
import os

import cv2
import numpy as np
import glob
import random
import time

from datetime import datetime

from flask import Flask
from flask_pymongo import PyMongo
from bson.json_util import dumps
from flask import jsonify, request
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename


# memasukan hasil training dan settingan training ke openCV
net = cv2.dnn.readNet("static/yolo/yolov3_training_final.weights", "static/yolo/yolov3_testing.cfg")

classes = []
with open("static/yolo/classes.txt", "r") as f:
    classes = f.read().splitlines()

app = Flask(__name__)
app.secret_key = "secret key"
app.config["MONGO_URI"] = "mongodb://localhost:27017/lihataspal"
mongo = PyMongo(app)


UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENTIONS = set(['jpg', 'jpeg', 'png'])


@app.route('/add', methods=['POST'])
def add_user():
    _json = request.json
    _name = _json['name']
    _username = _json['username']
    _password = _json['pwd']
    # validate the received values
    if _name and _username and _password and request.method == 'POST':
        # do not save password as a plain text
        _hashed_password = generate_password_hash(_password)
        # save details
        mongo.db.users.insert_one({'name': _name, 'username': _username, 'pwd': _hashed_password})
        resp = jsonify('User added successfully!')
        resp.status_code = 200
        return resp
    else:
        return not_found()


@app.route('/users')
def users():
    users = mongo.db.user.find()
    resp = dumps(users)
    return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.route('/login', methods=['POST'])
def login():
    _json = request.json
    _username = _json['username']
    _password = _json['pwd']

    _hashed_password = generate_password_hash(_password)

    mongo.db.users.find_one({'username': _username, 'pwd': _hashed_password})
    resp = jsonify('User login successfully!')
    resp.status_code = 200

    return resp

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS

@app.route('/upload', methods=['POST'])
def upload():
    created = datetime.today()

    file = request.files['inputFile']
    filename = secure_filename(file.filename) #copas prediksi

    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        mongo.db.log_detection.insert_one({'gambar': filename, 'waktu': created})
        images_path = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))
        random.shuffle(images_path)
        for img_path in images_path:
            img = cv2.imread(img_path)
            img = cv2.resize(img, (480, 360))
            height, width, channels = img.shape

            blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            start = time.time()
            outs = net.forward(output_layers)
            end = time.time()
            print("[INFO] Waktu deteksi yolo {:.6f} detik".format(end - start))

            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            font = cv2.FONT_HERSHEY_PLAIN
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            unique, counts = np.unique(class_ids, return_counts=True)
            tambah = 0
            cv2.rectangle(img, (3, 3), (165, 80), (0, 0, 255), 1)
            for i in range(len(counts)):
                cv2.putText(img, str(classes[i]) + " = " + str(counts[i]), (5, 15 + tambah), font, 1, (0, 0, 255), 1)
                tambah = tambah + 15
            print(indexes)
            daftar = []
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    daftar.append(label)
                    color = colors[class_ids[i]]
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)
                    text = "{}: {:.2f}".format(label, confidences[i])
                    cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, color, 1)

            print(daftar)
            if daftar:
                resp = jsonify(text)
            else:
                resp = jsonify('Tidak ada kerusakan yang terdeteksi')
                return resp
            key = cv2.waitKey(0)
        return resp
    else:
        resp = jsonify('Gagal upload hanya bisa upload file berformat jpg jpeg dan png')
        return resp

if __name__ == "__main__":
    app.run()