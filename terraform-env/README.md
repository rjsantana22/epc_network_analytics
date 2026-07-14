# Terraform

Execute the services that you define in main.tf

```Shell

terraform init

terraform plan

terraform apply

terraform destroy

```

alias terra-init='terraform -chdir=/home/rsantana/one_project/terraform-env/ init'
alias terra-plan='terraform -chdir=/home/rsantana/one_project/terraform-env/ plan'
alias terra-apply='terraform -chdir=/home/rsantana/one_project/terraform-env/ apply'
alias terra-destroy='terraform -chdir=/home/rsantana/one_project/terraform-env/ destroy'

## Connect with GCP

Create a services Account
- Administrador de storage
- Administrador de bigquery
- administrador de comppute

## Pre-Requisites
- Terraform client installation: https://www.terraform.io/downloads
- Cloud Provider account: https://console.cloud.google.com/


## Project infrastructure modules in GCP:
- Google Cloud Storage (GCS): Data Lake
- BigQuery: Data Warehouse

## Initial Setup
For this course, we'll use a free version (upto EUR 300 credits).

Create an account with your Google email ID
Setup your first project if you haven't already

eg. "DTC DE Course", and note down the "Project ID" (we'll use this later when deploying infra with TF)

- Setup service account & authentication for this project
- Grant Viewer role to begin with.
- Download service-account-keys (.json) for auth.
- Download SDK for local setup
- Set environment variable to point to your downloaded GCP keys:
```Shell
export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"
```

# Refresh token/session, and verify authentication
```Shell
gcloud auth application-default login
Setup for Access
IAM Roles for Service account:

Go to the IAM section of IAM & Admin https://console.cloud.google.com/iam-admin/iam
Click the Edit principal icon for your service account.
Add these roles in addition to Viewer : Storage Admin + Storage Object Admin + BigQuery Admin
Enable these APIs for your project:

https://console.cloud.google.com/apis/library/iam.googleapis.com
https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com
Please ensure GOOGLE_APPLICATION_CREDENTIALS env-var is set.

export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"

```

## GCP and Terraform on Windows
```Shell
Google Cloud SDK
For this tutorial, you'll need a Linux-like environment, e.g. GitBash, MinGW or cygwin
Power Shell should also work, but will require adjustments
Download SDK in zip: https://dl.google.com/dl/cloudsdk/channels/rapid/google-cloud-sdk.zip
source: https://cloud.google.com/sdk/docs/downloads-interactive
Unzip it and run the install.sh script
When installing it, you might see something like that:

The installer is unable to automatically update your system PATH. Please add
  C:\tools\google-cloud-sdk\bin
To fix that, adjust your .bashrc to include this in PATH (instructions)
You can also do it system-wide (instructions)
Now we need to point it to correct Python installation. Assuming you use Anaconda:

export CLOUDSDK_PYTHON=~/Anaconda3/python
Now let's check that it works:

$ gcloud version
Google Cloud SDK 367.0.0
bq 2.0.72
core 2021.12.10
gsutil 5.5
Google Cloud SDK Authentication
Now create a service account and generate keys like shown in the videos
Download the key and put it to some location, e.g. .gc/ny-rides.json
Set GOOGLE_APPLICATION_CREDENTIALS to point to the file
export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/ny-rides.json
Now authenticate:

gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
Alternatively, you can authenticate using OAuth like shown in the video

gcloud auth application-default login
If you get a message like quota exceeded

WARNING: Cannot find a quota project to add to ADC. You might receive a "quota exceeded" or "API not enabled" error. Run $ gcloud auth application-default set-quota-project to add a quota project.
```

Then run this:

PROJECT_NAME="ny-rides-alexey"
gcloud auth application-default set-quota-project ${PROJECT_NAME}
Terraform
Download Terraform
Put it to a folder in PATH
Go to the location with Terraform files and initialize it
terraform init
Optionally you can configure your terraform files (variables.tf) to include your project id:

variable "project" {
  description = "Your GCP Project ID"
  default = "ny-rides-alexey"
  type = string
}
Now follow the instructions
Run terraform plan
Next, run terraform apply
