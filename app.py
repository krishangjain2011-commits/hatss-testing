import streamlit as st
import os
import numpy as np
from PIL import Image

st.set_page_config(page_title="HATSS", layout="centered")
st.title("🏠 HATSS – Intruder Detection (Cloud Friendly Prototype)")

KNOWN_FOLDER = "known_faces"
os.makedirs(KNOWN_FOLDER, exist_ok=True)

# ---------------------------
# IMAGE EMBEDDING FUNCTION
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
# STEP 1: REGISTER KNOWN PERSON
# ---------------------------
st.header("Step 1: Register Known Family Member")

name = st.text_input("Enter Name (Example: Tony)")
uploaded = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png"])

if st.button("Save as Known"):
    if name == "" or uploaded is None:
        st.error("Please enter name and upload an image.")
    else:
        img = Image.open(uploaded).convert("RGB")

        # Save multiple images per person
        existing = [f for f in os.listdir(KNOWN_FOLDER) if f.startswith(name + "_")]
        next_index = len(existing) + 1

        save_path = os.path.join(KNOWN_FOLDER, f"{name}_{next_index}.png")
        img.save(save_path)

        st.success(f"✅ Saved {name} image {next_index}")
        st.image(img, caption=f"{name}_{next_index}")


# ---------------------------
# LOAD KNOWN EMBEDDINGS
# ---------------------------
known_embeddings = []

for file in os.listdir(KNOWN_FOLDER):
    path = os.path.join(KNOWN_FOLDER, file)
    img = Image.open(path)
    emb = get_embedding(img)

    person_name = file.split("_")[0]  # Tony_1.png -> Tony
    known_embeddings.append((person_name, emb))

st.divider()

# ---------------------------
# STEP 2: DETECT PERSON
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
        matched, matched_name, score = match_face(known_embeddings, test_embedding)

        st.write(f"📌 Similarity Score (Lower is better): **{score:.3f}**")

        if matched:
            st.success(f"✅ Person Identified: {matched_name}")
        else:
            st.error("🚨 Intruder Detected! Unknown Person")

            st.subheader("Choose Action")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📞 Report to Emergency Services"):
                    st.warning("🚨 Emergency Report Sent (Prototype Demo)")

            with col2:
                if st.button("✅ Mark as Known Person"):
                    new_name = st.text_input("Enter Name to Save This Person As Known")

                    if new_name:
                        existing = [f for f in os.listdir(KNOWN_FOLDER) if f.startswith(new_name + "_")]
                        next_index = len(existing) + 1

                        save_path = os.path.join(KNOWN_FOLDER, f"{new_name}_{next_index}.png")
                        test_img.save(save_path)

                        st.success(f"✅ Person saved as Known: {new_name}")
