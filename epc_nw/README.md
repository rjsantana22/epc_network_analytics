Welcome to your new dbt project!

### Using the starter project

Try running the following commands:
- dbt run
- dbt test


### Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices

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

# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1

dbt deps          # instala el paquete
dbt run --select dim_apn   # materializa solo la dimensión
dbt test --select dim_apn  # corre los tests
pip install dbt-utils

dbt test
dbt build

```
