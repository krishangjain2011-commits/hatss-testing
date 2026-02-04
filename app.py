import streamlit as st
import os
from PIL import Image

st.title("🏠 HATSS - Register Known Family Members")

# Folder to store known faces
KNOWN_FOLDER = "known_faces"
os.makedirs(KNOWN_FOLDER, exist_ok=True)

st.header("Upload Family Member Image")

name = st.text_input("Enter Family Member Name")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if st.button("Save Image"):
    if name == "":
        st.error("Please enter a name.")
    elif uploaded_file is None:
        st.error("Please upload an image.")
    else:
        img = Image.open(uploaded_file).convert("RGB")

        # Save image with name
        save_path = os.path.join(KNOWN_FOLDER, f"{name}.jpg")
        img.save(save_path)

        st.success(f"✅ Image saved for {name}!")
        st.image(img, caption=f"Saved Image of {name}", use_column_width=True)

st.divider()

st.header("📂 Saved Family Members")

saved_files = os.listdir(KNOWN_FOLDER)

if len(saved_files) == 0:
    st.info("No family member images saved yet.")
else:
    for file in saved_files:
        st.write("✅", file)
