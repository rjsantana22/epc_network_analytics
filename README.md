# One-Project

# Script generator of data
to this script you can execute:

```shell
docker run -it generate:python 
docker run -it -v ebm_raw:/app/data/raw generate:python
docker run -it -v ebm_raw:/app/data/raw pipeline:python

docker run -it --network=database_postgresql_default -v ebm_raw:/app/data/raw pipeline:python
```
To allow kestra connect to GCP:
I have to create Variable:
GCP_PROJECT_ID
GCP_LOCATION
GCP_BUCKET_NAME
GCP_DATASET

To add IA to Kestra:

into the docker compose
        kestra:
          ai:
            type: gemini
            gemini:
              model-name: gemini-2.5-flash
              api-key: ${GEMINI_API_KEY}


#DBT

pip install dbt-bigquery

dbt init dbt


[1] bigquery
[2] duckdb

(Don't see the one you want? https://docs.getdbt.com/docs/available-adapters)

Enter a number: 1
[1] oauth
[2] service_account
Desired authentication method option (enter a number): 2
keyfile (/path/to/bigquery/keyfile.json): /home/rsantana/one_project/terraform-env/keys/credentials_gcp.json                         
project (GCP project id): careful-airfoil-367403
dataset (the name of your dbt dataset): analytics
threads (1 or more): 4
job_execution_timeout_seconds [300]: 
[1] US
[2] EU
Desired location option (enter a number): 1
05:15:34  Profile epc_nw written to /home/rsantana/.dbt/profiles.yml using target's profile_template.yml and your supplied values. Run 'dbt debug' to validate the connection.


```Shell
dbt debug
dbt run
cd ~/projects/epc-data-pipeline/dbt

# Elimina la carpeta example que vino con dbt init
rm -rf models/example

# Crea la estructura
mkdir -p models/{staging,marts,intermediate}
mkdir -p tests
touch models/sources.yml
touch models/staging/stg_network_events.sql
touch models/marts/fct_diameter_calls.sql
touch models/marts/fct_sessions.sql

dbt docs generate
dbt docs serve
```