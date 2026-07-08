import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('--input_epc_network', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

input_epc_network = args.input_epc_network
output = args.output

spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

spark.conf.set("temporaryGcsBucket", "dataproc-temp-us-central1-403909964498-18nkuj4f")

df_epc_network = spark.read.csv(input_epc_network, header=True)
print(f"¡Éxito! Total de filas cargadas (epc_network): {df_epc_network.count()}")


df_epc_network = df_epc_network \
    .withColumnRenamed('rat_type', 'rat')\
    .withColumnRenamed('timestamp', 'date_ts')


df_epc_network.groupBy('imsi').count().show()

df_epc_network.registerTempTable('epc_nw_data')


df_result = spark.sql("""
SELECT 
    imsi AS imsi,
    date_trunc('month', date_ts) AS date_ts_month, 
    event_type AS event_type,
    result AS result,
    COUNT(*) AS total_events

FROM
    epc_nw_data
GROUP BY
    1, 2, 3, 4
""")

df_result.write.format('bigquery').option('table', output).mode('overwrite').save()





