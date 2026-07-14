# DBT
## Start the installation

​
```shell
pip install dbt-bigquery
dbt init epc_nw
#You'll be prompted for: path to your GCP credentials, GCP project ID,
#BigQuery dataset name, number of threads (4), job execution timeout
#(set to none), and the region.
dbt debug
```

---

## Create profiles.yml

Defines the connection dbt uses to reach BigQuery. Lives outside the
repo (`~/.dbt/profiles.yml`) — never commit real credentials.

```Yaml
epc_nw:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: your-gcp-project-id
      dataset: landing_zone        # or your target dataset
      threads: 4
      keyfile: /path/to/credentials.json
      location: US
      job_execution_timeout_seconds: 300
      job_retries: 1
```

---

## Modify dbt_project.yml

> Define the **project name** and the **folders** that will contain the
> models and SQL files — **staging**, **intermediate**, and **marts**.
> Inside each, you define `+schema` and `+materialized`.

### Models

#### Staging
- Reads from **sources**: the raw tables landed in the warehouse.
- 1:1 copy of the source data with minimal cleaning:
  - Data type casting
  - Column renaming

#### Intermediate *(planned — not yet configured)*
- Anything that isn't raw, but also isn't ready to expose to consumers.
- No strict guidelines — useful for heavy transformations or complex
  logic that shouldn't live in staging or marts.

#### Marts
- Consumption-ready: properly modeled, clean tables for dashboards.
- Split by type:
  - `marts/dimensions/` — `dim_apn`, `dim_area`, `dim_plmn`
  - `marts/facts/` — `fct_sessions`, `fct_event_by_apn`, `fct_event_by_area`, `fct_plmn_by_event`

```Yaml
# Important section
models:
  epc_nw:
    staging:
      +schema: staging
      +materialized: view
    marts:
      +schema: analytics
      +materialized: table
```

- `{{ source('name', 'table') }}` → raw data defined in your YAML
- `{{ ref('model_name') }}` → another dbt model

---
## Create the folder structure

```shell
cd epc_nw
rm -rf models/example
mkdir -p models/{staging,marts/dimensions,marts/facts,intermediate}
mkdir -p tests
touch models/sources.yml
touch models/staging/stg_network_events.sql
touch models/marts/facts/fct_sessions.sql
```
---

## Create packages.yml

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1   # double check this matches what's actually pinned in your repo
```

```shell
dbt deps

```
---

## Create sources.yml

- A **YAML file** inside `models/staging/` that tells dbt where your raw data is
- The **name** of the file is arbitrary — common choices are `sources.yml`, `_sources.yml` (underscore so it sorts to the top), or something named after the origin like `bigquery_sources.yml`
- Then you provide three fields that are **not** arbitrary — they must exactly match your warehouse:
    - **database** — the database name or GCP project
    - **schema** — the schema inside that database or BigQuery dataset
    - **tables** — the individual tables you want to reference

```Yaml
version: 2

sources:
  - name: raw_epc
    database: careful-airfoil-367403 # Or name of your GCP project
    schema: demo_dataset # Or name of your BigQuery dataset
    description: "Datos raw de eventos de red EPC"
    tables:
      - name: events_epc_network
        description: "Eventos raw generados por el generador EPC Docker"
```
---

## Create schema.yml

> Defines column-level documentation and tests for each model — this is
> what `dbt docs generate` uses to build searchable data documentation,
> and what `dbt test` runs against.

```Yaml

version: 2

models:
  - name: stg_network_events
    description: "Vista staging: eventos limpios y validados"
    columns:
      - name: event_id
        data_tests:
          - not_null
      - name: event_timestamp
        data_tests:
          - not_null
      - name: result
        data_tests:
          - not_null
          - accepted_values:
              values: ['success', 'failure']    
```
---

## Run and validate
```shell
dbt run --select dim_apn
dbt test --select dim_apn
dbt build
dbt docs generate
dbt docs serve

```