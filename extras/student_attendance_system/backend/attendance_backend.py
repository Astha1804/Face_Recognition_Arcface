import os
import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from insightface.app import FaceAnalysis
import pandas as pd
import base64
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'classroom_photos'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("known_faces", exist_ok=True)

faceapp = FaceAnalysis(name="buffalo_l")
faceapp.prepare(ctx_id=0, det_size=(640, 640))

def load_known_faces():
    known_face_encodings = {}
    for fname in os.listdir("known_faces"):
        if fname.lower().endswith(('.jpg', '.png', '.jpeg')):
            img = cv2.imread(os.path.join("known_faces", fname))
            if img is None: continue
            faces = faceapp.get(img)
            if faces:
                emb = faces[0].embedding
                name = os.path.splitext(fname)
                known_face_encodings[name] = emb
    return known_face_encodings

KNOWN_FACES = load_known_faces()

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    data = request.json['image']
    imgdata = base64.b64decode(data.split(",")[1])
    fname = f"{app.config['UPLOAD_FOLDER']}/photo_{len(os.listdir(app.config['UPLOAD_FOLDER']))+1}.jpg"
    with open(fname, 'wb') as f:
        f.write(imgdata)
    return jsonify({'success': True, 'filename': fname})

@app.route('/analyze_attendance', methods=['GET'])
def analyze_attendance():
    present_students = set()
    THRESHOLD = 0.65
    for img_name in os.listdir(app.config['UPLOAD_FOLDER']):
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
        img = cv2.imread(img_path)
        if img is None: continue
        faces = faceapp.get(img)
        for face in faces:
            emb = face.embedding
            for name, known_emb in KNOWN_FACES.items():
                sim = cosine_similarity([emb], [known_emb])[0]
                if sim > (1 - THRESHOLD):
                    present_students.add(name)
    attendance = [{'name': name, 'attendance': 'Present' if name in present_students else 'Absent'}
                  for name in KNOWN_FACES.keys()]
    df = pd.DataFrame(attendance)
    df.to_csv('attendance.csv', index=False)
    return jsonify({'attendance': attendance})

@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    attendance = request.json['attendance']
    df = pd.DataFrame(attendance)
    df.to_csv('attendance.csv', index=False)
    return jsonify({'success': True})

@app.route('/download_csv', methods=['GET'])
def download_csv():
    return send_file('attendance.csv', as_attachment=True)

@app.route('/reset_photos', methods=['POST'])
def reset_photos():
    folder = app.config['UPLOAD_FOLDER']
    for f in os.listdir(folder):
        os.remove(os.path.join(folder, f))
    return jsonify({'success': True})

if __name__ == "__main__":
    # If sharing with others, use host="0.0.0.0"; otherwise "localhost"
    app.run(host="0.0.0.0", port=5000, debug=True)
