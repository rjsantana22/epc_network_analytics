# Datasets Generator Script

## Description

This project implements an event generator script that emulates the behavior of a mobile network as seen from the Core network side, specifically from the **SGSN-MME**.

The script generates datasets that are used to analyze signaling events in mobile telecommunications networks. With data engineering, these events can be processed and turned into analysis-ready data for analytics or BI dashboards, including **Control Plane (CP)** events such as **attach**, **handover**, **paging**, and other **SGSN-MME** signaling procedures.

**Use case:** Near real-time monitoring and analysis of mobile network performance, allowing you to detect anomalies, calculate network KPIs, and improve the subscriber experience.

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Dependency management:** uv
- **Containerization:** Docker

## 📊 Metric and KPIs

### Main KPIs
- **Attach Success Rate (ASR):** % of successful attach procedures
- **Handover Success Rate (HOSR):** % of handovers without failure
- **Paging Success Rate:** Average paging response time
- **Service Request Success Rate:** % of successful service requests

### Dimensional Analysis
- Time-based distribution (hourly, daily, weekly)
- Performance by cell/eNodeB
- Failure cause analysis
- Anomaly detection
- Peak hours vs. normal hours comparison

## Synthetic Data

### Events
Each generated event is a **Control Plane network event**, i.e., a signaling event produced at the SGSN-MME, not user-plane traffic. Events include the following fields:

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
- `event_id`: Unique event identifier
- `timestamp`: Timestamp in ISO format
- `event_type`: Event type (`attach`, `handover`, `paging`, `service_request`)
- `result`: Result (`success`, `failure`)
- `cause_code`: Result cause code, based on the corresponding 3GPP standard for each event type
- `imsi`: International Mobile Subscriber Identity
- `cell_id`: Cell ID (ECGI)
- `enodeb_id`: eNodeB ID
- `mme_id`: MME ID
- `tracking_area`: Tracking area (TAI)
- `duration_ms`: Duration in milliseconds
- `rat_type`: Radio access technology type (LTE)
- `apn`: Access Point Name
- `plmn_id`: Public Land Mobile Network identifier


### CDRs (Call Detail Records)

> Note: these events doesn't uses yet.

Not every event generates a CDR. Only **successful `attach` events** are treated as the start of a billable session, so a CDR is generated exclusively from those. CDRs include the following fields:

```json
{
    "cdr_id": "cdr_1",
    "imsi": "IMSI_234133562293375",
    "session_start_time": "2026-03-22T17:46:16.635485",
    "session_end_time": "2026-03-22T18:01:52.635485",
    "duration_seconds": 936,
    "apn": "fwa.mcc10.mnc234.gprs",
    "plmn_id": "23413",
    "tracking_area": 234101,
    "cell_id": 2341019851,
    "rat_type": "LTE",
    "bytes_uplink": 4523112,
    "bytes_downlink": 98234511,
    "bytes_total": 102757623,
    "charging_type": "prepaid",
    "service_class": "streaming"
}
```

- `cdr_id`: Unique CDR identifier
- `imsi`: Subscriber IMSI (linked to the originating event)
- `session_start_time`: Session start timestamp (matches the originating event's timestamp)
- `session_end_time`: Session end timestamp
- `duration_seconds`: Session duration in seconds
- `apn`: Access Point Name used in the session
- `plmn_id`: Public Land Mobile Network identifier
- `tracking_area`: Tracking area where the session started
- `cell_id`: Cell ID where the session started
- `rat_type`: Radio access technology type (LTE)
- `bytes_uplink`: Uplink data volume, in bytes
- `bytes_downlink`: Downlink data volume, in bytes
- `bytes_total`: Total data volume, in bytes
- `charging_type`: Charging type (`prepaid`, `postpaid`)
- `service_class`: Service class derived from the APN (`data`, `voice`, `s

### Supported Event Types

- **attach** (~25%): Only successful attach events generate a CDR
- **handover** (~25%): X2 handover, S1 handover
- **paging** (~25%): MT call, MT SMS
- **service_request** (~25%): Data, voice, SMS

Event type is sampled uniformly across the four types. The success rate per event type varies depending on whether the event is generated during peak hours (7-9h, 12-13h, 17-20h) or off-peak hours, as defined in `SUCCESS_RATES` and `SUCCESS_RATES_PEAK` in `generator.py`.

## 🚀 Quick Start

# Start with Docker Container

To build the images:

```Shell
cd datasets_generator/
docker build -t generate:python .
```

To run the generator script.

```Shell
docker run -it -v raw_data:/app/data/raw --rm generate:python
```
### Standalone Script Installation

#### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) installed
- Git

1. **Move into the project folder:**
```bash
cd datasets_generator
```

2. **Install dependencies with uv:**
```bash
uv sync
```

This creates a virtual environment and installs the dependencies defined in `pyproject.toml` (pinned in `uv.lock`), so every run uses the exact same dependency versions.

#### Generate a dataset once

```bash
# Generate 10,000 events in JSON format
uv run python generator.py --mode batch --events 10000 --format json

# Generate 50,000 events in CSV format
uv run python generator.py --mode batch --events 50000 --format csv
```

#### Run in continuous mode (stream simulation)

```bash
# Generate 1,000 events every 60 seconds
uv run python generator.py --mode continuous --events 1000 --interval 60

# Stop with Ctrl+C
```

#### Additional options

```bash
# With a seed for reproducibility
uv run python generator.py --mode batch --events 10000 --seed 42

# Set the size of the subscriber (IMSI) pool
uv run python generator.py --mode batch --events 10000 --pool-size 500

# Specify the output directory
uv run python generator.py --mode batch --events 10000 --directory data/custom_output
```

Every run creates two subfolders inside the output directory: `events/` for the generated events and `cdrs/` for the CDRs derived from them.

### Usage Examples

```python
# Use the generator from Python code
from generator import ImsiPool, EventGenerator, CdrGenerator
import logging

logger = logging.getLogger(__name__)

# Create a subscriber pool and the generators
imsi_pool = ImsiPool(pool_size=200)
event_generator = EventGenerator(imsi_pool)
cdr_generator = CdrGenerator()

# Generate events and their derived CDRs
events = event_generator.generate_events(num_events=1000, logger=logger)
cdrs = cdr_generator.generate_cdrs(events, logger=logger)

# Save to file
from pathlib import Path
event_generator.save_to_json(events, Path("data/raw/events/my_events.json"), logger)
event_generator.save_to_json(cdrs, Path("data/raw/cdrs/my_cdrs.json"), logger)
```




