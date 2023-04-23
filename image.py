# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloudrun_imageproc_handler_setup]
# [START run_imageproc_handler_setup]
import os
import tempfile

from google.cloud import storage, vision, firestore
from wand.image import Image
import json

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
# [END run_imageproc_handler_setup]
# [END cloudrun_imageproc_handler_setup]


# [START cloudrun_imageproc_handler_analyze]
# [START run_imageproc_handler_analyze]
def process_images(data):
    file_data = data

    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_uri = f"gs://{bucket_name}/{file_name}"
    blob_source = vision.Image(source=vision.ImageSource(image_uri=blob_uri))

    print(f"Analyzing {file_name}.")
    detect_text(blob_source, file_name)


# [END run_imageproc_handler_analyze]
# [END cloudrun_imageproc_handler_analyze]


# [START cloudrun_imageproc_handler_detect]
# [START run_imageproc_handler_detect]
def detect_text(image, file_name):

    db = firestore.Client(project='funtalkr')
    doc_ref = db.collection(u'screenshot').document(file_name)
    client = vision.ImageAnnotatorClient()

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    # for text in texts:
    #     print('\n"{}"'.format(text.description))
    #
    #     vertices = (['({},{})'.format(vertex.x, vertex.y)
    #                 for vertex in text.bounding_poly.vertices])
    #
    #     print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    doc_ref.set({
        response: json.dumps(response)})
    return response

# [END run_imageproc_handler_detect]
# [END cloudrun_imageproc_handler_detect]
