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
    return "", 200


@app.route("/predict", methods=["POST"])
def index():
    request_input = request.get_json()
    from pprint import pprint
    pprint(request_input)
    if not request_input:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if "instances" not in request_input.keys() or "parameters" not in request_input.keys():
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    try:
        print("Fetching image from Firestore")
        # Parse incoming
        instance = request_input["instances"][0]
        user_id = request_input["parameters"]["user_id"]
        talk_id = request_input["parameters"]["talk_id"]

        # Fetch image location from cloud storage
        bucket = storage_client.get_bucket("funtalkr.appspot.com")
        blob = bucket.blob(f"users/{user_id}/talks/{talk_id}/{instance}")
        # print("Bucket path: " + str(f"users/{user_id}/talks/{talk_id}/{instance}"))

        img_response = decode_image(blob)
        if img_response is not None:
            return img_response, 200
        else:
            raise Exception("No prediction response")
    except Exception as e:
        print(f"error: {e}")
        return "", 500
