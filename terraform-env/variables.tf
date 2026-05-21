variable "credentials" {
    description = "My Credentials"
    default     = "./keys/credentials_gcp.json"
}

variable "project_id" {
  description = "My GCP project ID."
  default     = "careful-airfoil-367403"
}

variable "region" {
  description = "Region"
  default     = "us-central1"
}
variable "location" {
  description = "Project location."
  default     = "US"
}

variable "bq_dataset_name" {
  description = "My BigQuery dataset name."
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "My storage Bucket name"
  default     = "careful-airfoil-367403-terra-bucket"
}
variable "gcs_storge_class" {
    description = "Bucket Storage Class"
    default = "STANDARD" 
}
