## Python based Paddle OCR image detection model deployed via Docker containers to Google Cloud on commit with Github CICD pipeline
## Recieves image location from PubSub then publishes the result to prompt selection module. 

### Credentials removed for public repo release. Model is now maintained in another project. 


#### General instructions
Install cloud cli

Initialize

Enable CloudRun
```
gcloud init
(If account exists, select 1. Then select existing project)
```

Configure GCloud
```
gcloud config set project funtalkr
gcloud config set run/region us-east4
```

Add Topic to PubSub
```
gcloud pubsub topics create ocrTopic
```

Build Project
```
gcloud builds submit --tag gcr.io/funtalkr/pubsub
```

Deploy Functions
```
gcloud run deploy ocr-service --image gcr.io/funtalkr/pubsub
```

Function Address
https://ocr-service-dycqqwdmza-uk.a.run.app


Create Storage Bucket
```
gsutil mb gs://incoming-screenshots
```

Create Service Account for PubSub
```
gcloud iam service-accounts create ocr-service-pubsub-invoker --display-name "OCR Service Pub/Sub Invoker"
```

Create Subscription and assign permission to invoke service
```
gcloud run services add-iam-policy-binding ocr-service --member=serviceAccount:ocr-service-pubsub-invoker@funtalkr.iam.gserviceaccount.com --role=roles/run.invoker
```

Allow PubSub to create auth tokens
```
gcloud projects add-iam-policy-binding funtalkr --member=serviceAccount:service-487320900158@gcp-sa-pubsub.iam.gserviceaccount.com --role=roles/iam.serviceAccountTokenCreator
```

Create PubSub Subscription
```
gcloud pubsub subscriptions create ocrSubscription --topic ocrTopic --ack-deadline=600 --push-endpoint=https://ocr-service-dycqqwdmza-uk.a.run.app/ --push-auth-service-account=ocr-service-pubsub-invoker@funtalkr.iam.gserviceaccount.com
```

Create Service Account
```
gsutil kms serviceaccount -p funtalkr
```

Turn on Storage Notifications
```
gsutil notification create -t ocrTopic -f json gs://incoming-screenshots
```



Test image upload
```
gsutil cp <image file> gs://incoming-screenshots
```
gsutil cp C:\Users\telph\OneDrive\Desktop\testImages\snip.png gs://incoming-screenshots
```


Enable Firestore in Native Mode

Create GitHub secrets for WIF_PROVIDER and WIF_SERVICE_ACCOUNT

Workload Identity Provider
```
projects/487320900158/locations/global/workloadIdentityPools/service-pool/providers/service-identity-provider
```

Service Account
```
github-service-account@funtalkr.iam.gserviceaccount.com
```

Test Push Trigger

# Cloud Run Image Processing Sample

This sample service applies [Cloud Storage](https://cloud.google.com/storage/docs)-triggered image processing with [Cloud Vision API](https://cloud.google.com/vision/docs) analysis and ImageMagick transformation.

Use it with the [Image Processing with Cloud Run tutorial](http://cloud.google.com/run/docs/tutorials/image-processing).

[![Run in Google Cloud][run_img]][run_link]

[run_img]: https://storage.googleapis.com/cloudrun/button.svg
[run_link]: https://deploy.cloud.run/?git_repo=https://github.com/GoogleCloudPlatform/python-docs-samples&dir=run/image-processing

## Build

```
docker build --tag pubsub-tutorial:python .
```

## Run Locally

```
docker run --rm -p 9090:8080 -e PORT=8080 pubsub-tutorial:python
```

## Test

```
pytest
```

_Note: you may need to install `pytest` using `pip install pytest`._

## Deploy

```
# Set an environment variable with your GCP Project ID
export GOOGLE_CLOUD_PROJECT=<PROJECT_ID>

# Submit a build using Google Cloud Build
gcloud builds submit --tag gcr.io/${GOOGLE_CLOUD_PROJECT}/pubsub-tutorial

# Deploy to Cloud Run
gcloud run deploy pubsub-tutorial --image gcr.io/${GOOGLE_CLOUD_PROJECT}/pubsub-tutorial --set-env-vars=BLURRED_BUCKET_NAME=<BLURRED_BUCKET_NAME>

```

## Environment Variables

Cloud Run services can be [configured with Environment Variables](https://cloud.google.com/run/docs/configuring/environment-variables).
Required variables for this sample include:

* `INPUT_BUCKET_NAME`: The Cloud Run service will be notified of images uploaded to this Cloud Storage bucket. The service will then retrieve and process the image.
* `BLURRED_BUCKET_NAME`: The Cloud Run service will write blurred images to this Cloud Storage bucket.

## Maintenance Note

* The `image.py` file is copied from the [Cloud Functions ImageMagick sample `main.py`](../../functions/imagemagick/main.py). Region tags are changed.
* The requirements.txt dependencies used in the copied code should track the [Cloud Functions ImageMagick `requirements.txt`](../../functions/imagemagick/requirements.txt)

