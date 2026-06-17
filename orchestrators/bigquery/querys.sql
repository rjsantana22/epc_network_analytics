-- Query public available table
SELECT
    cause_code,
    imsi,
    enodeb_id
FROM `careful-airfoil-367403.demo_dataset.events_epc_network`
LIMIT 100;

-- Create an external table referencing files in GCS
CREATE OR REPLACE EXTERNAL TABLE `careful-airfoil-367403.demo_dataset.events_epc_network_external`
OPTIONS (
    format = 'CSV',
    uris = [
        'gs://careful-airfoil-367403-terra-bucket/events_processed*.csv'
    ]
);

-- Preview yellow trip data from the external table
SELECT *
FROM careful-airfoil-367403.demo_dataset.events_epc_network_external
LIMIT 10;

-- Create a non-partitioned table from the external table
CREATE OR REPLACE TABLE careful-airfoil-367403.demo_dataset.events_epc_network_non_partitioned AS
SELECT *
FROM careful-airfoil-367403.demo_dataset.events_epc_network_external;


-- Create a partitioned table from the external table
CREATE OR REPLACE TABLE careful-airfoil-367403.demo_dataset.events_epc_network_partitioned
PARTITION BY DATE(timestamp) AS
SELECT *
FROM careful-airfoil-367403.demo_dataset.events_epc_network_external;


1	2026-06-03
2	2026-05-22
3	2026-05-29
4	2026-05-23
-- Impact of partition
-- Scanning 1.6GB of data
SELECT DISTINCT(imsi)
FROM careful-airfoil-367403.demo_dataset.events_epc_network_non_partitioned
WHERE DATE(timestamp) BETWEEN '2026-05-29' AND '2026-06-03';

-- Scanning ~106 MB of DATA
SELECT DISTINCT(imsi)
FROM careful-airfoil-367403.demo_dataset.events_epc_network_partitioned
WHERE DATE(timestamp) BETWEEN '2026-05-29' AND '2026-06-03';

-- Inspect table partitions
SELECT
    table_name,
    partition_id,
    total_rows
FROM `demo_dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'events_epc_network_partitioned'
ORDER BY total_rows DESC;

-- Creating a partition and cluster table
CREATE OR REPLACE TABLE careful-airfoil-367403.demo_dataset.events_epc_network_partitioned_clustered
PARTITION BY DATE(timestamp)
CLUSTER BY VendorID AS
SELECT * 
FROM careful-airfoil-367403.demo_dataset.events_epc_network_external;

-- Query scans 1.1 GB
SELECT count(*) as trips
FROM careful-airfoil-367403.demo_dataset.events_epc_network_partitioned
WHERE DATE(timestamp) BETWEEN '2026-05-29' AND '2026-06-03'
  AND imsi=1;

-- Query scans 864.5 MB
SELECT count(*) as trips
FROM careful-airfoil-367403.demo_dataset.events_epc_network_partitioned_clustered
WHERE DATE(timestamp) BETWEEN '2026-05-29' AND '2026-06-03'
  AND imsi=1;
