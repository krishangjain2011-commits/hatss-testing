from flask import Flask, render_template, Response
import cv2
import face_recognition
import time
import os

from face_model import load_embeddings
from firebase_upload import upload_intruder_image

app = Flask(__name__)

INTRUDER_FOLDER = "intruder_snaps"
os.makedirs(INTRUDER_FOLDER, exist_ok=True)

known_encodings, known_names = load_embeddings()

if len(known_encodings) == 0:
    print("⚠️ No embeddings found!")
    print("Run:")
    print("python register_known.py")
    print("python train_embeddings.py")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

last_alert_time = 0
alert_delay = 10


def generate_frames():
    global last_alert_time

    while True:
        success, frame = cap.read()
        if not success:
            break

        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            # Green for known, Red for unknown
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # Intruder alert
            if name == "Unknown":
                current_time = time.time()

                if current_time - last_alert_time > alert_delay:
                    snap_path = os.path.join(INTRUDER_FOLDER, f"intruder_{int(current_time)}.jpg")
                    cv2.imwrite(snap_path, frame)

                    print("🚨 INTRUDER DETECTED!")
                    print("📸 Snapshot saved:", snap_path)

                    try:
                        url = upload_intruder_image(snap_path)
                        print("☁ Uploaded to Firebase:", url)
                    except Exception as e:
                        print("❌ Firebase upload failed:", e)

                    last_alert_time = current_time

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)
