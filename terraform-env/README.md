# Terraform

Execute the services that you define in main.tf

```Shell

terraform init # initilize the local enviroment with dependecy and variables for the specific cloud platform.

terraform plan # Compare the enviroment in cloud platform with the configure that write in main.tf

terraform apply # Apply the configure that are in main.tf

terraform destroy # Destroy the configure that are in terraform.tfstate

```

## Connect with GCP

Create a services Account, where need the following roles active:
- Storage Admin
- Bigquery Admin
- Compute Admin

## Pre-Requisites

- Terraform client installation: https://www.terraform.io/downloads
- Cloud Provider account: https://console.cloud.google.com/

## Project infrastructure modules in GCP:
- Google Cloud Storage (GCS): Data Lake
- BigQuery: Data Warehouse

## Initial Setup

# Refresh token/session, and verify authentication

```Shell
gcloud auth application-default login
# Setup for Access
# IAM Roles for Service account:

# Go to the IAM section of IAM & Admin https://console.cloud.google.com/iam-admin/iam
# Click the Edit principal icon for your service account.
# Add these roles in addition to Viewer : Storage Admin + Storage Object Admin + BigQuery Admin
# Enable these APIs for your project:

# https://console.cloud.google.com/apis/library/iam.googleapis.com
# https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com
# Please ensure GOOGLE_APPLICATION_CREDENTIALS env-var is set.

export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"

```

