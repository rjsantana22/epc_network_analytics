Model deployment
Tutorial

Steps
gcloud auth login
bq extract --project_id=careful-airfoil-367403 -m demo_dataset.network_hyperparam_model gs://careful-airfoil-367403-terra-bucket/network_hyperparam_model
mkdir /tmp/model
gsutil cp -r gs://careful-airfoil-367403-terra-bucket/network_hyperparam_model /tmp/model
mkdir -p serving_dir/network_hyperparam_model/1
cp -r /tmp/model/network_hyperparam_model/* serving_dir/network_hyperparam_model/1
docker pull tensorflow/serving
docker run -p 8501:8501 --mount type=bind,source=/home/rsantana/one_project/serving_dir/network_hyperparam_model,target=/models/network_hyperparam_model -e MODEL_NAME=network_hyperparam_model -t tensorflow/serving 

curl -d '{"instances": [{
  "event_type": "attach",
  "cell_id": "2341012552",
  "enodeb_id": "1986",
  "mme_id": "2",
  "tracking_area": "234101",
  "duration_ms": 152,
  "rat_type": "LTE",
  "apn": "fwa.mcc10.mnc234.gprs"
}]}' \
-X POST http://localhost:8501/v1/models/network_hyperparam_model:predict