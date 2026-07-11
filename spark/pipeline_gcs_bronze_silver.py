import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, DateType
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

# 1. Defines el esquema exacto
schema = StructType([
    StructField("cdr_id", IntegerType(), True),      # Entero
    StructField("imsi", StringType(), True),           # Texto
    StructField("session_start_time", DateType(), True),           # Decimal / Flotante
    StructField("session_end_time", DateType(), True),      # Fecha (YYYY-MM-DD)
    StructField("duration_seconds", IntegerType(), True),      # Fecha (YYYY-MM-DD)
    StructField("apn", StringType(), True),      # Fecha (YYYY-MM-DD)
    StructField("plmn_id", IntegerType(), True),     # Fecha (YYYY-MM-DD)
    StructField("tracking_area", IntegerType(), True),      # Fecha (YYYY-MM-DD)
    StructField("cell_id", IntegerType(), True),      # Fecha (YYYY-MM-DD)
    StructField("rat_type", StringType(), True),      # Fecha (YYYY-MM-DD)
    StructField("bytes_uplink", IntegerType(), True),      # Fecha (YYYY-MM-DD)
    StructField("bytes_downlink", IntegerType(), True),      # Fecha (YYYY-MM-DD)
    StructField("bytes_total", IntegerType(), True),      # Fecha (YYYY-MM-DD)
    StructField("charging_type", StringType(), True),      # Fecha (YYYY-MM-DD)
    StructField("service_class", StringType(), True)      # Fecha (YYYY-MM-DD)

])

#spark.conf.set("temporaryGcsBucket", "dataproc-temp-us-central1-403909964498-18nkuj4f")

df_epc_network = spark.read.option("multiLine", "true").json(input_epc_network)

print(f"¡Éxito! Total de filas cargadas (epc_network): {df_epc_network.count()}")

if df_epc_network.isEmpty():
    print("⚠️ El path no contiene archivos o está vacío. Finalizando job sin error.")
    spark.stop()
    exit(0)

print(f"¡Éxito! Total de filas cargadas (epc_network): {df_epc_network.count()}")
print("Columnas originales:", df_epc_network.columns)

# 4. Transformaciones (Descomenta las fechas si las necesitas, ya funcionan)
df_epc_network = df_epc_network.withColumn('session_start_time', F.to_timestamp(F.col('session_start_time'), 'yyyy-MM-dd HH:mm:ss'))
df_epc_network = df_epc_network.withColumn('session_end_time', F.to_timestamp(F.col('session_end_time'), 'yyyy-MM-dd HH:mm:ss'))

# CORRECCIÓN AQUÍ: Reemplazar el prefijo 'IMSI_' correctamente en la columna 'imsi'
df_epc_network = df_epc_network.withColumn(
    'imsi', 
    F.regexp_replace(F.col('imsi'), '^IMSI_', '')
)

# 5. Escritura en Parquet
print(f"Escribiendo resultado en formato Parquet en: {output}")
df_epc_network.write.parquet(output, mode='overwrite')

print("🚀 ¡Proceso completado con éxito!")
spark.stop()