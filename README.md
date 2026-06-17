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

export GEMINI_API_KEY="AQ.Ab8RN6KjRDoTk4sBFEVuY7wRSASw_KEfonm14IGlBBvmVevGSw"


