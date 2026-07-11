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