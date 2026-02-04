import streamlit as st
import os
import numpy as np
from PIL import Image

from firebase_upload import upload_known_face
from firebase_config import db

st.set_page_config(page_title="HATSS", layout="centered")

st.title("🏠 HATSS – House and Tech Security System")
st.write("AI-Based Intruder Detection Prototype (Firebase Connected)")

# ---------------------------
# LIGHTWEIGHT EMBEDDING (Cloud Friendly)
# ---------------------------
def get_embedding(image):
    image = image.convert("L")
    image = image.resize((64, 64))
    arr = np.array(image).astype("float32") / 255.0
    return arr.flatten()

def match_face(known_embeddings, new_embedding, threshold=0.35):
    best_match = None
    best_dist = 999

    for name, emb in known_embeddings:
        dist = np.linalg.norm(emb - new_embedding)
        if dist < best_dist:
            best_dist = dist
            best_match = name

    if best_dist < threshold:
        return True, best_match, best_dist

    return False, None, best_dist


# ---------------------------
# LOAD ALL KNOWN PEOPLE FROM FIRESTORE
# ---------------------------
def load_known_people_embeddings():
    known_embeddings = []

    people_docs = db.collection("known_people").stream()

    for person in people_docs:
        person_name = person.id

        image_docs = db.collection("known_people").document(person_name).collection("images").stream()

        for img_doc in image_docs:
            data = img_doc.to_dict()
            url = data.get("url")

            if url:
                try:
                    # Download image temporarily
                    import requests
                    response = requests.get(url)

                    if response.status_code == 200:
                        temp_file = "temp_known.jpg"
                        with open(temp_file, "wb") as f:
                            f.write(response.content)

                        img = Image.open(temp_file).convert("RGB")
                        emb = get_embedding(img)

                        known_embeddings.append((person_name, emb))
                        os.remove(temp_file)

                except:
                    continue

    return known_embeddings


# ---------------------------
# STEP 1: REGISTER KNOWN PERSON
# ---------------------------
st.header("Step 1: Register Known Family Member")

name = st.text_input("Enter Family Member Name")
uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if st.button("Save as Known"):
    if name == "" or uploaded is None:
        st.error("Please enter name and upload an image.")
    else:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Uploaded Image", use_column_width=True)

        img.save("temp.jpg")
        url = upload_known_face("temp.jpg", name)
        os.remove("temp.jpg")

        st.success(f"✅ Uploaded {name} image to Firebase!")
        st.write("📌 Firebase URL:", url)

st.divider()

# ---------------------------
# STEP 2: DETECT INTRUDER
# ---------------------------
st.header("Step 2: Detect Intruder")

st.info("Loading known embeddings from Firebase...")
known_embeddings = load_known_people_embeddings()
st.success(f"✅ Loaded {len(known_embeddings)} known face samples")

test_file = st.file_uploader("Upload Image to Detect", type=["jpg", "jpeg", "png"], key="test")

if test_file:
    test_img = Image.open(test_file).convert("RGB")
    st.image(test_img, caption="Test Image", use_column_width=True)

    test_embedding = get_embedding(test_img)

    if len(known_embeddings) == 0:
        st.warning("⚠️ No known family members stored in Firebase yet.")
    else:
        matched, matched_name, score = match_face(known_embeddings, test_embedding)

        st.write(f"📌 Similarity Score: **{score:.3f}** (lower is better)")

        if matched:
            st.success(f"✅ Person Identified: {matched_name}")
        else:
            st.error("🚨 Intruder Detected! Unknown Person")

            st.subheader("Choose Action")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📞 Report to Emergency Services"):
                    st.warning("🚨 Emergency Alert Sent (Prototype Demo)")

            with col2:
                if st.button("✅ Mark as Known Person"):
                    new_name = st.text_input("Enter Name to Save This Person")

                    if new_name:
                        test_img.save("temp_intruder.jpg")
                        url = upload_known_face("temp_intruder.jpg", new_name)
                        os.remove("temp_intruder.jpg")

                        st.success(f"✅ Intruder marked as Known: {new_name}")
                        st.write("📌 Firebase URL:", url)
