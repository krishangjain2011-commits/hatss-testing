import face_recognition
import os
import pickle

KNOWN_FOLDER = "known_faces"
EMBEDDINGS_FILE = "embeddings.pkl"

def train_embeddings():
    known_encodings = []
    known_names = []

    if not os.path.exists(KNOWN_FOLDER):
        os.makedirs(KNOWN_FOLDER)

    for person_name in os.listdir(KNOWN_FOLDER):
        person_path = os.path.join(KNOWN_FOLDER, person_name)

        if not os.path.isdir(person_path):
            continue

        for file in os.listdir(person_path):
            img_path = os.path.join(person_path, file)

            try:
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)

                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_names.append(person_name)

            except:
                continue

    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump((known_encodings, known_names), f)

    print("✅ Embeddings trained successfully!")
    print("Total Samples:", len(known_encodings))


def load_embeddings():
    if not os.path.exists(EMBEDDINGS_FILE):
        return [], []

    with open(EMBEDDINGS_FILE, "rb") as f:
        known_encodings, known_names = pickle.load(f)

    return known_encodings, known_names
