Import Python file to dataproc cluster

```Shell
gsutil cp spark/pipeline_gcs_to_bq.py gs://careful-airfoil-367403-terra-bucket/code/pipeline_gcs_to_bq.py
```

Run a job:

```Shell
#GCS TO BIGQUERY
gcloud dataproc jobs submit pyspark \
    --cluster=epc-dataproc-cluster \
    --region=us-central1 \
    gs://careful-airfoil-367403-terra-bucket/code/pipeline_gcs_to_bq.py \
    -- \
    --input_epc_network=gs://careful-airfoil-367403-terra-bucket/epc_network.parquet \
    --output=careful-airfoil-367403:demo_dataset.epc_network_stg
```