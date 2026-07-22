# Orchestrators

This project uses Kestra as its orchestrator; it's a solid alternative to Airflow, since YAML files are a good way to define each flow.

## Kestra

It is important before to run each flow, to create the following variable in Kestra, in the KV section To allow kestra connect to GCP:

- GCP_PROJECT_ID
- GCP_LOCATION
- GCP_BUCKET_NAME
- GCP_DATASET

## Flows

**Load files from generator Logs Container to GCS**

![alt text](flow_1.png)

Kestra also uploads the `pipeline_gcs_bronze_silver.py` file to GCS, since it's needed by the Spark job. Finally, move each file load in GCS, to processed_events/ folder.

**Spark Cluster GCS - Dataproc**

![alt text](flow_2.png)

This flow (`pipeline_spark_dataproc_gcs.yml`) is active by a trigger, here is created the spark cluster in GCP and run Spark job. Also, it is load from Kestra to GCS, the `pipeline_gcs_bronze_silver.py` file due to is needed to spark job.

**Load from Parquet files in GCS to Tables in BigQuery**

![alt text](flow_3.png)

Also, this is active by trigger. Here is load from Parquet files in GCS to BigQuery like table. Each processed parquet file is moved to silver-processed.

**Execute DBT**

![alt text](flow_4.png)

Finally, runs dbt flows, where it used to model the warehouse and obtained staging, intermediate and marts models. Through a BI tools we can visualiza the data building a dashboard.

## Suggestion

**Enabling AI in the Kestra Environment**

This step is optional, but in my experience was very useful. So, the AI helped me pick the right functions.

This are some step to Active it:

```Shell
cd orchestrators/
export GEMINI_API_KEY="your-api-key-here" # The API key is  https://aistudio.google.com/api-keys
```
Also, to add this line in Docker Compose file, for IA in Kestra:

```yaml
#To add IA to Kestra:
#into the docker compose
        kestra:
          ai:
            type: gemini
            gemini:
              model-name: gemini-2.5-flash
              api-key: ${GEMINI_API_KEY}
```




