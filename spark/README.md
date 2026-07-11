Import Python file to dataproc cluster

```Shell
gsutil cp spark/pipeline_gcs_bronze_silver.py gs://epc_network_bucket/code/pipeline_gcs_bronze_silver.py
```

Run a job:

```Shell
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