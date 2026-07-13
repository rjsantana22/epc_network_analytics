# Datasets Generator Script

## 📋 Descripción

Este proyecto implementa un script generador de eventos, que emula el comportamiento de redes moviles visto desde el Core de datos, especificamente desde el SGSN-MME. El script genera datasets los cuales pueden ser usado para analizar eventos de señalización en redes de telecomunicaciones móviles. Con ingenieria de datos se puede procesar y analizar eventos como attach, handover, paging y otros procedimientos de señalización SGSN-MME.

**Caso de uso:** Monitoreo y análisis de rendimiento de red móvil en tiempo casi-real, permitiendo detectar anomalías, calcular KPIs de red y optimizar la experiencia del usuario.

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.10+
- **Containerización:** Docker

## 📊 Métricas y KPIs Analizados

### KPIs Principales
- **Attach Success Rate (ASR):** % de attach procedures exitosos
- **Handover Success Rate (HOSR):** % de handovers sin fallo
- **Paging Success Rate:** Tiempo de respuesta promedio de paging
- **Service Request Success Rate:** % de service requests exitosos

### Análisis Dimensionales
- Distribución temporal (horaria, diaria, semanal)
- Performance por celda/eNodeB
- Análisis de causas de fallo
- Detección de anomalías
- Comparativa horas pico vs normales

## 🚀 Quick Start

### Prerequisitos

```bash
Python 3.10 o superior
Git
```

### Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/redbull123/telecom-network-analytics.git
cd telecom-network-analytics
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Crear estructura de directorios:**
```bash
mkdir -p data/raw data/processed data/staging
```

#### Generar dataset una sola vez

```bash
# Generar 10,000 eventos en JSON
python data_generator/generator_2.py --mode batch --events 10000 --format json

# Generar 50,000 eventos en CSV
python data_generator/generator_2.py --mode batch --events 50000 --format csv
```

#### Ejecutar en modo continuo (simulación de stream)

```bash
# Generar 1,000 eventos cada 60 segundos
python data_generator/generator_2.py --mode continuous --events 1000 --interval 60

# Detener con Ctrl+C
```

#### Opciones adicionales

```bash
# Con seed para reproducibilidad
python data_generator/generator_2.py --mode batch --events 10000 --seed 42

# Especificar directorio de salida
python data_generator/generator_2.py --mode batch --events 10000 --directory data/custom_output
```


To build the images:

```Shell
docker build -t generate:python .
```

To run the generator script.

```Shell
docker run -it -v raw_data:/app/data/raw --rm generate:python
```

### Estructura de Datos Sintéticos

Los eventos generados incluyen los siguientes campos:

- `event_id`: Identificador único del evento
- `timestamp`: Marca de tiempo en formato ISO
- `event_type`: Tipo de evento (attach, handover, paging, service_request)
- `result`: Resultado (success, failure)
- `cause_code`: Código de causa del resultado
- `imsi`: Identificador internacional de suscriptor móvil
- `cell_id`: ID de la celda (ECGI)
- `enodeb_id`: ID del eNodeB
- `mme_id`: ID del MME
- `tracking_area`: Área de rastreo (TAI)
- `duration_ms`: Duración en milisegundos
- `rat_type`: Tipo de tecnología de acceso radio (LTE)
- `apn`: Nombre del punto de acceso de red
- `plmn_id`: Identificador de red pública móvil


### Ejemplos de Uso

```python
# Usar el generador en código Python
from data_generator.generator import TelecomEventGenerator

# Crear generador
generator = TelecomEventGenerator(seed=42)

# Generar eventos
events = generator.generate_batch(num_events=1000)

# Guardar a archivo
from pathlib import Path
generator.save_to_json(events, Path("data/raw/my_events.json"))
```

## 📝 Datos Sintéticos

Los eventos generados incluyen los siguientes campos:

```json
{
        "event_id": "event_1",
        "timestamp": "2026-03-22T17:46:16.635485",
        "event_type": "attach",
        "result": "success",
        "cause_code": "0_attach success",
        "imsi": "234133562293375",
        "cell_id": 2341019851,
        "enodeb_id": 1986,
        "mme_id": 2,
        "tracking_area": 234101,
        "duration_ms": 152,
        "rat_type": "LTE",
        "apn": "fwa.mcc10.mnc234.gprs",
        "plmn_id": "23413"
}
```

### Tipos de Eventos Soportados

- **attach** (35%): Initial attach, handover attach, periodic TAU
- **handover** (25%): X2 handover, S1 handover
- **paging** (20%): MT call, MT SMS
- **service_request** (15%): Data, voice, SMS