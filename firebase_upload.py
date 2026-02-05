import uuid
from datetime import datetime
from firebase_config import bucket, db

def upload_intruder_image(local_path):
    filename = f"intruder_{uuid.uuid4()}.jpg"
    storage_path = f"intruders/{filename}"

    blob = bucket.blob(storage_path)
    blob.upload_from_filename(local_path)
    blob.make_public()

    url = blob.public_url

    db.collection("intruder_alerts").add({
        "image_url": url,
        "storage_path": storage_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Intruder Detected"
    })

    return url
