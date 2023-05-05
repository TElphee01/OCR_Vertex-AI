# [START cloudrun_imageproc_controller]
# [START run_imageproc_controller]
import os
from torch import multiprocessing
import base64
import json
from chat_ocr import decode_image
from flask import Flask, request, Response
from google.cloud import storage, firestore
from google.oauth2 import service_account

# Specify the path to the JSON key file in the container
key_path = "credentials.json"

# Create credentials from the JSON key file
credentials = service_account.Credentials.from_service_account_file(key_path)

# Instantiate a Google Cloud Storage client using the credentials
storage_client = storage.Client(credentials=credentials)

app = Flask(__name__)


@app.route("/isalive")
def is_alive():
    print("/isalive request")
    status_code = Response(status=200)
    return status_code


@app.route("/predict", methods=["POST"])
def index():
    envelope = request.get_json()
    from pprint import pprint
    pprint(envelope)
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    # Decode the Pub/Sub message.
    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            data = json.loads(base64.b64decode(pubsub_message["data"]).decode())

        except Exception as e:
            msg = (
                "Invalid Pub/Sub message: "
                "data property is not valid base64 encoded JSON"
            )
            print(f"error: {e}")
            return f"Bad Request: {msg}", 400

        # Validate the message is a Cloud Storage event.
        if not data["name"] or not data["bucket"]:
            msg = (
                "Invalid Cloud Storage notification: "
                "expected name and bucket properties"
            )
            print(f"error: {msg}")
            return f"Bad Request: {msg}", 400

        try:
            print("Fetching image from Firestore")
            # Fetch image location from cloud storage
            file_data = data
            file_name = file_data["name"]
            bucket_name = file_data["bucket"]
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(file_name)

            # blob = storage_client.bucket(bucket_name).get_blob(file_name)
            # blob_uri = f"gs://{bucket_name}/{file_name}"

            # print("Saving to temp_local_filename")
            # _, temp_local_filename = tempfile.mkstemp()
            # blob.download_to_filename(temp_local_filename)
            # print("Sending blob to decode_image: " + str(blob))
            decode_image(blob)
            return ("", 204)

        except Exception as e:
            print(f"error: {e}")
            return ("", 500)

    return ("", 500)
    # [END run_imageproc_controller]
    # [END cloudrun_imageproc_controller]

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True, threaded=False)
