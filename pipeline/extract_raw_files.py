#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path


def copy_with_docker_cli(container: str, container_path: str, host_dest: Path) -> None:
    command = [
        "docker",
        "cp",
        f"{container}:{container_path}/.",
        str(host_dest),
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrae los archivos de /app/data/raw desde un contenedor Docker al directorio pipeline."
    )
    parser.add_argument(
        "--container",
        default="0b8ce8afbe6f",
        help="Nombre o ID del contenedor Docker (por defecto: generator:python)",
    )
    parser.add_argument(
        "--container-path",
        default="/app/data/raw",
        help="Ruta dentro del contenedor donde están los archivos (por defecto: /app/data/raw)",
    )
    parser.add_argument(
        "--host-dest",
        default="raw",
        help="Directorio destino en el host donde se copiarán los archivos (por defecto: pipeline)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    host_dest = Path(args.host_dest).resolve()
    host_dest.mkdir(parents=True, exist_ok=True)

    try:
        print("Usando docker CLI como respaldo.")
        copy_with_docker_cli(args.container, args.container_path, host_dest)
        print(f"Archivos copiados desde {args.container}:{args.container_path} a {host_dest} usando docker cp.")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"Error ejecutando docker cp: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
