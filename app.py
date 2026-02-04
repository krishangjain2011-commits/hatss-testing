import streamlit as st
import os
import numpy as np
from PIL import Image

st.set_page_config(page_title="HATSS", layout="centered")

st.title("🏠 HATSS – Intruder Detection (Cloud Friendly Prototype)")

KNOWN_FOLDER = "known_faces"
os.makedirs(KNOWN_FOLDER, exist_ok=True)

# ---------------------------
# IMAGE EMBEDDING (LIGHTWEIGHT)
# ---------------------------
def get_embedding(image):
    image = image.convert("L")         # grayscale
    image = image.resize((64, 64))     # fixed size
    arr = np.array(image).astype("float32")
    arr = arr / 255.0                 # normalize
    return arr.flatten()              # 4096-d vector

def match_face(known_embeddings, new_embedding, threshold=0.25):
    for name, emb in known_embeddings:
        dist = np.linalg.norm(emb - new_embedding)
        if dist < threshold:
            return True, name
    return False, None

# ---------------------------
# STEP 1: REGISTER KNOWN PEOPLE
# ---------------------------
st.header("Step 1: Register Known Family Member")

name = st.text_input("Enter Name")
uploaded = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png"])

if st.button("Save as Known"):
    if name == "" or uploaded is None:
        st.error("Please enter name and upload an image.")
    else:
        img = Image.open(uploaded).convert("RGB")
        save_path = os.path.join(KNOWN_FOLDER, f"{name}.png")
        img.save(save_path)
        st.success(f"✅ Saved {name} as Known Person")
        st.image(img, caption=name)

# ---------------------------
# LOAD KNOWN EMBEDDINGS
# ---------------------------
known_embeddings = []

for file in os.listdir(KNOWN_FOLDER):
    path = os.path.join(KNOWN_FOLDER, file)
    img = Image.open(path)
    emb = get_embedding(img)
    person_name = file.split(".")[0]
    known_embeddings.append((person_name, emb))

st.divider()

# ---------------------------
# STEP 2: TEST IMAGE
# ---------------------------
st.header("Step 2: Detect Intruder")

test_img_file = st.file_uploader("Upload Image to Detect", type=["jpg", "jpeg", "png"], key="test")

if test_img_file is not None:
    test_img = Image.open(test_img_file).convert("RGB")
    st.image(test_img, caption="Test Image", use_column_width=True)

    test_embedding = get_embedding(test_img)

    if len(known_embeddings) == 0:
        st.warning("⚠️ No known family members registered yet.")
    else:
        matched, matched_name = match_face(known_embeddings, test_embedding)

        if matched:
            st.success(f"✅ Person Identified: {matched_name}")
        else:
            st.error("🚨 Intruder Detected! Unknown Person")
