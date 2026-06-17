#!/usr/bin/env python3
import argparse
import json
import pandas as pd
import os
from pathlib import Path
from sqlalchemy.engine import create_engine



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Carga archivos JSON de /app/data/raw a PostgreSQL."
    )
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("RAW_DATA_DIR", "/app/data/raw"),
        help="Directorio local con archivos JSON para cargar (por defecto: /app/data/raw)",
    )
    parser.add_argument(
        "--table",
        #default=os.environ.get("EVENT_TABLE", "events"),
        default="events",
        help="Nombre de la tabla de destino en PostgreSQL (por defecto: events)",
    )
    parser.add_argument(
        "--host",
        #default=os.environ.get("POSTGRES_HOST", "pgdatabase2"),
        default="pgdatabase2",
        help="Host de PostgreSQL (por defecto: pgdatabase2)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("POSTGRES_PORT", 5432)),
        help="Puerto de PostgreSQL (por defecto: 5432)",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("POSTGRES_DB", "event_generator"),
        help="Base de datos de PostgreSQL (por defecto: event_generator)",
    )
    parser.add_argument(
        "--user",
        default=os.environ.get("POSTGRES_USER", "root"),
        help="Usuario de PostgreSQL (por defecto: root)",
    )
    parser.add_argument(
        "--password",
        #default=os.environ.get("POSTGRES_PASSWORD", "root"),
        default="root",
        help="Password de PostgreSQL (por defecto: root)",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Vacía la tabla antes de insertar los datos.",
    )
    return parser.parse_args()


def get_json_files(data_dir: Path) -> list[Path]:
    if not data_dir.exists():
        raise FileNotFoundError(f"No existe el directorio de datos: {data_dir}")

    files = sorted(data_dir.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos JSON en {data_dir}")

    return files


def load_records(files: list[Path]) -> list[dict]:
    records = []
    for json_file in files:
        with json_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError(f"El archivo {json_file} no contiene una lista JSON.")
        records.extend(data)
    return records


def read_json_chunks(json_file: Path, chunk_size: int):
    with json_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError(f"El archivo {json_file} no contiene una lista JSON.")

    for start in range(0, len(data), chunk_size):
        chunk = data[start : start + chunk_size]
        yield pd.DataFrame.from_records(chunk)


def run(files: list[Path], username, password, port, database, chunk_size, table_name, hostname):
    engine = create_engine(
        f"postgresql+psycopg://{username}:{password}@{hostname}:{port}/{database}"
    )
    print(engine)
    for file in files:
        print(f"Cargando datos desde {file}...")
        df_iter = read_json_chunks(file, chunk_size)

        first_chunk = next(df_iter, None)
        if first_chunk is None or first_chunk.empty:
            print(f"Advertencia: el archivo {file} está vacío o no tiene registros.")
            continue

        #first_chunk.head(0).to_sql(
        #    name=f"{table_name}",
        #    con=engine,
        #    if_exists="replace",
        #)

        print("Table created")

        first_chunk.to_sql(
            name=f"{table_name}",
            con=engine,
            if_exists="append",
        )

        print("Inserted first chunk:", len(first_chunk))

        for df_chunk in df_iter:
            if df_chunk.empty:
                continue
            df_chunk.to_sql(
                name=f"{table_name}",
                con=engine,
                if_exists="append",
            )
            print("Inserted chunk:", len(df_chunk))

def main() -> int:
    args = parse_args()
    data_dir = Path(args.data_dir)

    json_files = get_json_files(data_dir)
    print(f"Cargando {len(json_files)} archivo(s) desde {data_dir}")

    records = load_records(json_files)
    print(f"Total de registros encontrados: {len(records)}")

    run(files = json_files,
        username=args.user,
        password=args.password,
        port=args.port,
        database=args.db,
        chunk_size=1000,
        table_name=args.table,
        hostname=args.host
    )
    print(f"Insertados {len(records)} registros en la tabla {args.table}.")

    return 0






if __name__ == "__main__":
    raise SystemExit(main())
