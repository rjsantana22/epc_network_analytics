# Datasets Generator Script

## Description

This project uses an events generator script, that emulated the behavior of mobile network since Packet core, on base at **SGSN-MME**.

Script build datasets which are used for analytics the signalling events in mobile networks. With data engineer process could become this events in ready-data for analytics or BI dashboard.

**Use Case:** Monitored and analyzed the performance of mobile network, allows cath in anomalean, buils KPIs and improve the user experience.

## 📊 Metric and KPIs

### KPIs
- **Attach Success Rate (ASR):** % success of attach procedures 
- **Handover Success Rate (HOSR):** % success of handovers
- **Paging Success Rate:** Average Answers time of paging
- **Service Request Success Rate:** % de success service requests


### Dimensional Analytics
- Temporal distribution (hourly, dayly, weekly)
- Performance by cell/eNodeB
- Analytic by cause.
- Detección de anomalías
- Comparative by peakk hour vs normal behavior.

### Structure of synthetic data

**Control plane:**
Each events include the following fields:

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

- `event_id`: Id unique of event.
- `timestamp`: timestamp with format ISO.
- `event_type`: type of event (attach, handover, paging, service_request).
- `result`: result (success, failure).
- `cause_code`: cause code of result.
- `imsi`: identicator mobile subscriber International.
- `cell_id`: ID of cell (ECGI).
- `enodeb_id`: ID of eNodeB.
- `mme_id`: ID of MME.
- `tracking_area`: Tracking Area (TAI).
- `duration_ms`: duration in miliseconds.
- `rat_type`: Type of Radio access Tecnology
- `apn`: Access Point Name
- `plmn_id`: ID of Mobile Public Network.



## Tech Stack

- **Language:** Python 3.10+
- **Container:** Docker

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




