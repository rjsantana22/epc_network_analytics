-- 1.- SELECT THE COLUMNS INTERESTED FOR YOU
CREATE OR REPLACE TABLE careful-airfoil-367403.demo_dataset.network_events_ml (
  `event_type` STRING,
  `result` STRING,
  `cell_id` STRING,
  `enodeb_id` STRING,
  `mme_id` STRING,
  `tracking_area` STRING,
  `duration_ms` INT64,
  `rat_type` STRING,
  `apn` STRING
) AS (
  SELECT 
    event_type, 
    result, 
    CAST(cell_id AS STRING) AS cell_id, 
    CAST(enodeb_id AS STRING) AS enodeb_id, 
    CAST(mme_id AS STRING) AS mme_id, 
    CAST(tracking_area AS STRING) AS tracking_area, 
    duration_ms, 
    rat_type, 
    apn
  FROM careful-airfoil-367403.demo_dataset.events_epc_network_partitioned
  WHERE result IS NOT NULL
);

-- 2.- CREATE MODEL WITH DEFAULT SETTING
CREATE OR REPLACE MODEL `careful-airfoil-367403.demo_dataset.network_result_model`
OPTIONS (
  model_type='logistic_reg', -- Logística porque queremos clasificar (success/fail)
  input_label_cols=['result'],
  DATA_SPLIT_METHOD='AUTO_SPLIT'
) AS
SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`;

-- 3. To CHECK THE FEATURES IMPORTANCE
    SELECT * FROM ML.FEATURE_INFO(MODEL `careful-airfoil-367403.demo_dataset.network_result_model`);

-- 4. EVALUATE THE MODEL
    SELECT * FROM ML.EVALUATE(MODEL `careful-airfoil-367403.demo_dataset.network_result_model`,
  (SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`));

-- 5. PREDICT THE MODEL
    SELECT * FROM ML.PREDICT(MODEL `careful-airfoil-367403.demo_dataset.network_result_model`,
  (SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`));
-- 6. PREDICT AND EXPLAIN
SELECT *
FROM ML.EXPLAIN_PREDICT(MODEL `careful-airfoil-367403.demo_dataset.network_result_model`,
(SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`
WHERE result IS NOT NULL), STRUCT(3 as top_k_features));

-- 7. HYPER PARAM TUNNING
CREATE OR REPLACE MODEL `careful-airfoil-367403.demo_dataset.network_hyperparam_model`
OPTIONS (
  model_type='logistic_reg',
  input_label_cols=['result'],
  DATA_SPLIT_METHOD='AUTO_SPLIT',
  num_trials=5,
  max_parallel_trials=2,
  l1_reg=hparam_range(0, 20),
  l2_reg=hparam_candidates([0, 0.1, 1, 10])
) AS
SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`;

-- 3. To CHECK THE FEATURES IMPORTANCE
    SELECT * FROM ML.FEATURE_INFO(MODEL `careful-airfoil-367403.demo_dataset.network_hyperparam_model`);

-- 4. EVALUATE THE MODEL
    SELECT * FROM ML.EVALUATE(MODEL `careful-airfoil-367403.demo_dataset.network_hyperparam_model`,
  (SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`));

-- 5. PREDICT THE MODEL
    SELECT * FROM ML.PREDICT(MODEL `careful-airfoil-367403.demo_dataset.network_hyperparam_model`,
  (SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`));
-- 6. PREDICT AND EXPLAIN
SELECT *
FROM ML.EXPLAIN_PREDICT(MODEL `careful-airfoil-367403.demo_dataset.network_hyperparam_model`,
(SELECT * FROM `careful-airfoil-367403.demo_dataset.network_events_ml`
WHERE result IS NOT NULL), STRUCT(3 as top_k_features));