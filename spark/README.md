# Spark

There many way to run Spark for batch:

1. Create the Dataproc or Spark Cluster throught Terraform:

```HCF
resource "google_dataproc_cluster" "epc_cluster" {
  name    = var.dataproc_name
  project = var.project_id
  region  = var.region

  cluster_config {
##    staging_bucket = google_storage_bucket.demo-bucket.name
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

```

Then run it, and execute the following commands for run spark job:

```Shell

gsutil cp spark/pipeline_gcs_bronze_silver.py gs://epc_network_bucket/code/pipeline_gcs_bronze_silver.py #Copy the python script to cluster

Run a job:

#GCS TO GCS
gcloud dataproc jobs submit pyspark \
    --cluster=epc-dataproc-cluster \
    --region=us-central1 \
    gs://epc_network_bucket/code/pipeline_gcs_bronze_silver.py \
    -- \
    --input_epc_network=gs://epc_network_bucket/bronze/batch/raw_cdrs/*.json \
    --output=gs://epc_network_bucket/silver_cdrs/batch/

#GCS TO BIGQUERY
gcloud dataproc jobs submit pyspark \
    --cluster=epc-dataproc-cluster \
    --region=us-central1 \
    gs://epc_network_bucket/code/pipeline_gcs_bronze_silver.py \
    -- \
    --input_epc_network=gs://epc_network_bucket/batch/raw_cdrs/*.json \
    --output=careful-airfoil-367403:demo_dataset.epc_network_stg
```

2. Create a job like serveless from **Kestra**: 

This is the option implement in this project, because it is better than to try managed a local cluster:

```Yaml
    - id: write_file_to_internal_storage
      type: io.kestra.plugin.core.storage.Write
      content: "{{ read('pipeline_gcs_bronze_silver.py') }}"
      extension: ".py" # Le damos la extensión explícitamente para evitar fallos
    - id: upload_python_file_to_gcs
      type: io.kestra.plugin.gcp.gcs.Upload
      projectId: "{{ kv('GCP_PROJECT_ID') }}"
      # Al estar dentro de WorkingDirectory, usamos la expresión de Kestra para obtener la ruta absoluta del archivo local
      from: "{{ outputs.write_file_to_internal_storage.uri }}"
      to: "gs://{{ kv('GCP_BUCKET_NAME') }}/code/{{ kv('GCP_PYTHON_FILE_NAME') }}"

    - id: run_pyspark_batch
      type: io.kestra.plugin.gcp.dataproc.batches.PySparkSubmit
      projectId: "{{ kv('GCP_PROJECT_ID') }}"
      region: "{{ kv('GCP_REGION') }}"
      name: "batch-pyspark-job"
      mainPythonFileUri: "gs://{{ kv('GCP_BUCKET_NAME') }}/code/{{ kv('GCP_PYTHON_FILE_NAME') }}"
      args:
         - "--input_epc_network=gs://epc_network_bucket/bronze/batch/staging/*.json"
         - "--output=gs://epc_network_bucket/silver/batch/staging"
```