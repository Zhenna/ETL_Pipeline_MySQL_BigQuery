#!/bin/bash
########################################
# 
# run chmod +x deploy.sh to make the script executable
# 
# Execute this script:  src/deploy.sh
#
########################################

set -e

LOCAL_IMAGE_NAME="" 
GCP_IMAGE_NAME=""
GCP_PROJECT_ID=""
GCP_REGION_NAME="us-central1"
GCP_REPO_NAME=""

echo "Deploying to Docker Container"

# Build a local image
docker build -t $LOCAL_IMAGE_NAME .

# Tag the local image
docker tag $LOCAL_IMAGE_NAME:latest $GCP_REGION_NAME-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_REPO_NAME/$GCP_IMAGE_NAME

# Push to GCP Artifact Registry
docker push $GCP_REGION_NAME-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_REPO_NAME/$GCP_IMAGE_NAME