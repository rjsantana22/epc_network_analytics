# Orchestrators
## Kestra
```Shell
cd orchestrators/
export GEMINI_API_KEY="your-api-key-here"
docker compose up -d
```

Also, to add this line in Docker Compose file, for IA in Kestra:

```Docker
#To add IA to Kestra:

#into the docker compose
        kestra:
          ai:
            type: gemini
            gemini:
              model-name: gemini-2.5-flash
              api-key: ${GEMINI_API_KEY}
```


To allow kestra connect to GCP:
I have to create Variable:
- GCP_PROJECT_ID
- GCP_LOCATION
- GCP_BUCKET_NAME
- GCP_DATASET


