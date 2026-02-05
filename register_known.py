import cv2
import os
import time

KNOWN_FOLDER = "known_faces"
os.makedirs(KNOWN_FOLDER, exist_ok=True)

person_name = input("Enter Family Member Name: ").strip()

person_path = os.path.join(KNOWN_FOLDER, person_name)
os.makedirs(person_path, exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

count = 0
max_images = 30

print("\n📸 Capturing images... Move face in different angles.")
print("Press Q to stop early.\n")

while count < max_images:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera not detected.")
        break

    cv2.putText(frame, f"Capturing: {count+1}/{max_images}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

    cv2.imshow("Register Known Person", frame)

    filename = os.path.join(person_path, f"{person_name}_{count}.jpg")
    cv2.imwrite(filename, frame)

    count += 1
    time.sleep(0.2)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Saved {count} images for {person_name}")
print("Now run: python train_embeddings.py")
