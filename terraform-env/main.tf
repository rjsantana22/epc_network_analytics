terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.32.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true


  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name
  location = var.location
  delete_contents_on_destroy = true
}

########

resource "google_dataproc_cluster" "epc_cluster" {
  name    = var.dataproc_name
  project = var.project_id
  region  = var.region

  cluster_config {
#    staging_bucket = google_storage_bucket.demo-bucket.name
    gce_cluster_config {
      zone              = "us-central1-b"
      subnetwork        = "default"

      shielded_instance_config {
        enable_secure_boot          = true
        enable_vtpm                 = true
        enable_integrity_monitoring = true
      }
    }

    master_config {
      num_instances = 1
      machine_type  = "c3-standard-4"

      disk_config {
        boot_disk_type    = "hyperdisk-balanced"
        boot_disk_size_gb = 200
      }
    }

    # Sin worker_config -> junto con la propiedad de abajo, define el single-node
    software_config {
      image_version       = "2.3.30-debian12"
      optional_components = ["JUPYTER"]

      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }

    endpoint_config {
      enable_http_port_access = true
    }
  }
}

resource "google_service_account_iam_member" "dataproc_sa_user" {
  service_account_id = "projects/careful-airfoil-367403/serviceAccounts/403909964498-compute@developer.gserviceaccount.com"
  role                = "roles/iam.serviceAccountUser"
  member              = "serviceAccount:dtc-de-sa@careful-airfoil-367403.iam.gserviceaccount.com"
}