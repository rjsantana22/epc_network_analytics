# EPC Network Analytics

## Background
  

I've worked with UMTS/EPC networks since 2019. One thing I've consistently seen as a problem is the sheer volume of data these networks generate every second — and how little of it gets turned into something usable.

EPC networks generate two broad categories of data: Control Plane (CP) and User Plane (UP). This project focuses on CP data, specifically signaling generated at the SGSN-MME, which includes attributes like APN, cell, eNodeB, Tracking Area, Location Area, and event/cause codes. Cause codes and event definitions follow the [3GPP standard](link_to_doc).

## Problem

Even when this data exists, most operators lack the pipeline to turn it into something queryable in time to act on it — answering questions like "which APN had the most failed sessions today?" typically requires manual, ad-hoc digging through raw signaling data.

## What this project does

An end-to-end batch pipeline that ingests simulated CP/SGSN-MME events and turns them into a trusted, documented, query-ready dataset (a **data product**) — from raw event generation to a dimensional model in BigQuery to a dashboard, without manual intervention at any step.
## Objective

Design and deploy a batch pipeline that transforms simulated CP/EPC network events into trusted, queryable KPIs — volume of events, success/failure rate, distribution by APN/PLMN/area — without manual intervention.
## What It Does

The EPC Network Analytics pipeline transforms simulated Control Plane (CP) network events into trusted, query-ready KPIs across five layers:

| Layer              | What happens                                                                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Ingestion**      | Synthetic CP/SGSN-MME events are generated and staged locally, then uploaded to Google Cloud Storage as raw JSON (bronze zone), triggered on a schedule by Kestra. |
| **Processing**     | A Spark job, submitted to a Dataproc cluster, reads bronze events, cleans and transforms them, and writes the result as Parquet to a silver zone in GCS.           |
| **Warehousing**    | Silver Parquet files are loaded into BigQuery staging tables, partitioned and ready for modeling.                                                                  |
| **Transformation** | dbt Core builds a dimensional model on top of staging: dimensions (APN, PLMN, area, event type) and incremental fact tables (sessions, events by APN/area/PLMN).   |
| **Serving**        | Looker Studio connects directly to the BigQuery marts for an operational dashboard — event volume, success/failure rate, and distribution by APN/PLMN/area.        |

All five layers are orchestrated by Kestra, which manages the flow from data generation through the final dbt build.

## What this project does NOT cover (yet)

- Real-time/streaming processing of live events.
- Predictive or prescriptive analytics.

See [Roadmap](./ROADMAP.md) for what's planned next.

---
## Architecture
```mermaid
flowchart TD
    subgraph K[Orchestrated by Kestra]
        A[Ingestion: events staged to GCS]
        B[Processing: Spark on Dataproc, bronze to silver]
        C[Warehousing: silver parquet loaded to BigQuery]
 
        subgraph T[Transformation - dbt]
            direction TB
            T1[Landing zone: raw_epc.events_epc_network]
            T2[Staging zone: stg_network_events, view]
            T3[Data marts / gold zone: dims and facts, tables]
            T1 --> T2 --> T3
        end
 
        E[Serving: Looker Studio dashboard on marts]
 
        A --> B --> C --> T
        T --> E
    end
```
![[architecture.svg]]

---

## Tech Stack
| Category                   | Technology                                                      |
| -------------------------- | --------------------------------------------------------------- |
| **Data Generation**        | Python (synthetic CP/EPC event and CDR generator)               |
| **Infrastructure as Code** | Terraform (GCP: GCS bucket + BigQuery datasets)                 |
| **Workflow Orchestration** | Kestra                                                          |
| **Data Lake**              | Google Cloud Storage                                            |
| **Processing**             | Apache Spark on Dataproc (ephemeral cluster, managed by Kestra) |
| **Data Warehouse**         | Google BigQuery                                                 |
| **Transformations**        | dbt Core                                                        |
| **Visualization**          | Data Studio                                                   |
| **Containerization**       | Docker Compose                                                  |


---
## How to Run It

### Prerequisites

- **Docker Desktop** installed and running
- A **GCP Service Account** JSON key saved as `creds/gcp-key.json`
- **Python** 3.11+ 
- **Terraform**

### 1. Start Infrastructure

Boot up Kestra:

```shell
docker-compose up -d
```

### 2. Provision Cloud Resources

```shell
cd terraform-env
terraform init
terraform plan
terraform apply # -auto-approve
cd ..
```

### 3. **`generator`** Container — generates 1K synthetic events by Batch.

```Shell
cd datasets_generator
docker build -t generate:python .
docker run -it -v raw_data:/app/data/raw --rm generate:python 
```
### 4. Run the Pipeline

Then, open the Kestra UI at [http://localhost:8080](http://localhost:8080/) and execute:

1. **`pipeline_load_to_gcs`** — Init the pipeline by trigger each 15min, load the synthetic events network from source data to GCS (Raw - Bronze zone).
2. **`pipeline_spark_dataproc_gcs`** — These start after `pipeline_load_to_gcs` flow, processed data from **Bronze zone** to **Silver zone** in **GCS**.
3. **`pipeline_silverzone_to_bq`** — start after `pipeline_spark_dataproc_gcs` flow, load the parquet file from **Silver zone** to tables in **Bigquery**.
4. **`pipeline_run_dbt`** — start after `pipeline_silverzone_to_bq` flow, modeling the table to fact and dimension tables.

### 5. Look the data in Data Studio (Looker Studio) 

this point it will be define in other moment....

---
## Project Structure


```
epc_network_analytics/
├── datasets_generator/    # Synthetic EPC events network generator and DockerFile.
├── epc_nw/                # dbt Core models (staging + marts).
├── orchestrators/         # Kestra YAML workflow definitions.
│   ├── kestra/            # YAML file of each flow.
├── spark/                 # Spark batch aggregation.
├── terraform-env/         # IaC for GCS + BigQuery.
│   ├── keys/              # Credentials to GCP.
├── data_warehouse/        # BigQuery table setup.
├── terraform/             # IaC for GCS + BigQuery.
```


---
## Dashboard

This section it will add in the future.