from firebase_config import db

doc = db.collection("test").document("check")
doc.set({"status": "firebase connected"})

print("Firebase Connected Successfully!")
