import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, DateType
import argparse

def run_process():
    try:
        spark = SparkSession.builder \
            .appName('test') \
            .getOrCreate()
    except Exception as e:
        print(f"Error al crear la sesión de Spark: {e}")
        exit(1)

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_epc_network', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    input_epc_network = args.input_epc_network
    output = args.output

    # 1. Defines el esquema exacto
    # Nota: session_start_time / session_end_time llegan como strings desde el JSON
    # (formato 'yyyy-MM-dd HH:mm:ss'), por eso el schema las declara como StringType
    # y la conversión a timestamp se hace explícitamente más abajo con to_timestamp.
    # _corrupt_record captura filas que no matchean el schema en vez de tumbar el job.
    schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("result", StringType(), True),
        StructField("cause_code", StringType(), True),
        StructField("imsi", StringType(), True),
        StructField("cell_id", StringType(), True),
        StructField("enodeb_id", IntegerType(), True),
        StructField("mme_id", IntegerType(), True),
        StructField("tracking_area", IntegerType(), True),
        StructField("duration_ms", IntegerType(), True),
        StructField("rat_type", StringType(), True),
        StructField("apn", StringType(), True),
        StructField("plmn_id", StringType(), True)
                ])

    try:
        df_epc_network = spark.read \
            .option("multiLine", "true") \
            .option("mode", "PERMISSIVE") \
            .schema(schema) \
            .json(input_epc_network)
    except Exception as e:
        print(f"Error al leer el archivo JSON: {e}")
        spark.stop()
        exit(1)

    if df_epc_network.isEmpty():
        print("⚠️ El path no contiene archivos o está vacío. Finalizando job sin error.")
        spark.stop()
        exit(0)

    print(f"¡Éxito! Total de filas cargadas (epc_network): {df_epc_network.count()}")
    print("Columnas originales:", df_epc_network.columns)

    # Filas que no matchean el schema quedan en _corrupt_record en vez de convertirse
    # silenciosamente en nulls. Se descartan del output; si querés inspeccionarlas más
    # adelante, es tan simple como escribir el complemento de este filter a otro path.

    df_valid = df_epc_network.withColumn('timestamp', F.to_timestamp(F.col('timestamp'), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"))

    df_valid = df_valid.withColumn(
        'imsi',
        F.regexp_replace(F.col('imsi'), '^IMSI_', '')
    )

    print(f"Escribiendo resultado en formato Parquet en: {output}")
    df_valid.write.parquet(output, mode='overwrite')

    print("🚀 ¡Proceso completado con éxito!")
    spark.stop()

if __name__ == "__main__":
    run_process()