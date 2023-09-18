#!/bin/bash
########################################
# 
# run chmod +x terraform_import.sh to make the script executable
# 
# Execute this script:  ./terraform_import.sh
#
########################################

set -e

GCP_REGION=""
GCP_PROJECT_ID=""
GCP_PROJECT_NUM=""
SERVICE_ACCOUNT_NAME=""


# ---------- import BigQuery Datasets to terraform ---------- 

TERRAFORM_BQ_DATASET_NAME=""
GCP_DATASET_NAME=""

# terraform import google_bigquery_dataset.$TERRAFORM_BQ_DATASET_NAME \
#     projects/$GCP_PROJECT_ID/datasets/$GCP_DATASET_NAME

# ---------- import service account to terraform ---------- 

TERRAFORM_SERVICE_ACCOUNT_NAME=""
SERVICE_ACCOUNT_EMAIL=""

# terraform import google_service_account.$TERRAFORM_SERVICE_ACCOUNT_NAME \
#     projects/$GCP_PROJECT_ID/serviceAccounts/$SERVICE_ACCOUNT_EMAIL

# ---------- import google monitoring alert policy to terraform ------------

GCP_ALERT_POLICY_ID=""
TERRAFORM_ALERT_NAME=""

# terraform import google_monitoring_alert_policy.$TERRAFORM_ALERT_NAME \
#     projects/$GCP_PROJECT_ID/alertPolicies/$GCP_ALERT_POLICY_ID

# ---------- import cloud run job to terraform ---------- 

JOB_NAME=""
TERRAFORM_JOB_NAME=""

# terraform import google_cloud_run_v2_job.$TERRAFORM_JOB_NAME \
#     projects/$GCP_PROJECT_ID/locations/$GCP_REGION/jobs/$JOB_NAME

# ---------- import cloud scheduler job to terraform ---------- 

SCHEDULER_NAME=""
TERRAFORM_SCHEDULER_NAME=""

# terraform import google_cloud_scheduler_job.$TERRAFORM_SCHEDULER_NAME \
#     projects/$GCP_PROJECT_ID/locations/$GCP_REGION/jobs/$SCHEDULER_NAME

# ---------- import artifact registry to terraform ---------- 

GCP_REPO_NAME=""
TERRAFORM_REPO_NAME=""

# import artifact registry
# terraform import google_artifact_registry_repository.$TERRAFORM_REPO_NAME \
#     projects/$GCP_PROJECT_ID/locations/$GCP_REGION/repositories/$GCP_REPO_NAME

# ---------- import GCP secret to terraform ---------- 

SECRET_NAME=""

# terraform import google_secret_manager_secret.$SECRET_NAME \
#     projects/$GCP_PROJECT_NUM/secrets/$SECRET_NAME