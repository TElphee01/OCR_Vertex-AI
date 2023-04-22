
Install cloud cli

Initialize

Enable CloudRun

Configure GCloud
```
gcloud config set project psiparch
gcloud config set run/region us-east4
```

Add Topic to PubSub
```
gcloud pubs topics create imageFeed
```

Build Project
```
gcloud builds submit --tag gcr.io/psiparch/pubsub
```

Deploy Functions
```
gcloud run deploy psiparch-function --image gcr.io/psiparch/pubsub
gcloud run deploy psiparch-function --image gcr.io/psiparch/pubsub --no-allow-unauthenticated
```

Function Address
https://psiparch-function-ro5cujvoja-uk.a.run.app

Create Storage Bucket
```
gsutil mb gs://screenshots
```

Create Service Account for PubSub
```
gcloud iam service-accounts create cloud-run-pubsub-invoker --display-name "Cloud Run Pub/Sub Invoker"
```

Create Subscription and assign permission to invoke service
```
gcloud run services add-iam-policy-binding psiparch-function \
--member=serviceAccount:cloud-run-pubsub-invoker@psiparch.iam.gserviceaccount.com \
--role=roles/run.invoker
```

Allow PubSub to create auth tokens
```
gcloud projects add-iam-policy-binding psiparch \
   --member=serviceAccount:service-223554570259@gcp-sa-pubsub.iam.gserviceaccount.com \
   --role=roles/iam.serviceAccountTokenCreator
```

Create PubSub Subscription
```
gcloud pubsub subscriptions create myRunSubscription --topic imageFeed \
--ack-deadline=600 \
--push-endpoint=https://psiparch-function-ro5cujvoja-uk.a.run.app/ \
--push-auth-service-account=cloud-run-pubsub-invoker@psiparch.iam.gserviceaccount.com
```

Create Service Account
```
gsutil kms serviceaccount -p psiparch
```

Turn on Storage Notifications
```
gsutil notification create -t imageFeed -f json gs://screenshots_storage
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

