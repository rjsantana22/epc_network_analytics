To indicate the API KEY to Gemini

To define credentials Kestra


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

cd 02-workflow-orchestration/docker
export GEMINI_API_KEY="your-api-key-here"
docker compose up -d