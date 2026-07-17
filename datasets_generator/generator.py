import json
from datetime import datetime
import random
from enum import Enum
import argparse
from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import time
import logging
import pandas as pd


class EventType(Enum):
    ATTACH = "attach"
    HANDOVER = "handover"
    PAGING = "paging"
    SERVICE_REQUEST = "service_request"

class ResultType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"

class Imsi(Enum):
    LOCAL = "23410"
    VISITOR_1 = "23411"
    VISITOR_2 = "23412"
    VISITOR_3 = "23413"

class RatType(Enum):
    FOUR_G = "LTE"

class ChargingType(Enum):
    PREPAID = "prepaid"
    POSTPAID = "postpaid"

class ServiceClass(Enum):
    DATA = "data"
    VOICE = "voice"
    SMS = "sms"
    STREAMING = "streaming"

SUCCESS_RATES = {
    EventType.ATTACH: 0.95,
    EventType.HANDOVER: 0.90,
    EventType.PAGING: 0.85,
    EventType.SERVICE_REQUEST: 0.92,
}

SUCCESS_RATES_PEAK = {
    EventType.ATTACH: 0.90,
    EventType.HANDOVER: 0.85,
    EventType.PAGING: 0.80,
    EventType.SERVICE_REQUEST: 0.87,
}

CAUSE_CODES_SUCCESS = {
    EventType.ATTACH: ["0_attach success"],
    EventType.HANDOVER: ["0_handover success"],
    EventType.PAGING: ["0_paging success"],
    EventType.SERVICE_REQUEST: ["0_service request success"]
}

'''
    EventType.ATTACH: These cause code are based on Standard: 3GPP TS 24.301 (Non-Access Stratum (NAS) protocol
    for Evolved Packet System (EPS))
    EventType.HANDOVER: These cause code are based on Standard: Standard: 3GPP TS 36.413 (S1 Application Protocol)
    EveentType.PAGING: These cause code are based on Standard: Standard: 3GPP TS 36.413 — Clause 9.2.1.15 — CN Domain and Paging message IEs
    EventType.SERVICE_REQUEST: These cause code are based on Standard: 3GPP TS 24.301 (Non-Access Stratum (NAS) protocol
'''
CAUSE_CODES_FAILURE = {
    EventType.ATTACH: [
        "17_Network failure",
        "2_IMSI unknown in HSS",
        "7_EPS services not allowed",
        "11_PLMN not allowed",
        "15_No suitable cells in tracking area",
        "22_Congestion"
    ],
    EventType.HANDOVER: [
        "6_ho-failure-in-target-EPC-eNB-or-target-system",
        "7_ho-target-not-allowed",
        "11_unknown-targetID",
        "12_no-radio-resources-available-in-target-cell",
        "226_failure-in-radio-interface-procedure"
    ],
    EventType.PAGING: [
        "5_delayTolerantAccess ",
        "1_highPriorityAccess",
        "0_emergency",
        "4_mo-Data"
    ],
    EventType.SERVICE_REQUEST: [
        "17_Network Failure",
        "22_Congestion",
        "7_EPS services not allowed",
        "9_UE identity cannot be derived by the network"
    ]
}

ECGI = [2341012541, 2341019851, 2341012552, 2341019862, 2341012563, 2341019873]  # 3GPP TS 23.003 ECGI = PLMN Identity + ECI
ENODEB_IDS = [1254, 1985, 1255, 1986, 1256, 1987]
MME_IDS = [1, 2]
TRACKING_AREAS = [234101, 234102, 234103, 234104, 234105]  # 3GPP TS 23.003 TAI = MCC + MNC + TAC
APN = ['internet.mcc10.mnc234.gprs', 'mms.mcc10.mnc234.gprs', 'ims.mcc10.mnc234.gprs', 'vpn.mcc10.mnc234.gprs', 'fwa.mcc10.mnc234.gprs',
       'internet.mcc11.mnc234.gprs', 'internet.mcc12.mnc234.gprs', 'internet.mcc13.mnc234.gprs']

CHARGING_TYPE_WEIGHTS = {ChargingType.PREPAID: 0.7, ChargingType.POSTPAID: 0.3}

# Deriva service_class del APN -> mantiene coherencia con el evento origen, no se samplea aparte.
SERVICE_CLASS_BY_APN_PREFIX = {
    "mms": ServiceClass.SMS,
    "ims": ServiceClass.VOICE,
    "internet": ServiceClass.DATA,
    "vpn": ServiceClass.DATA,
    "fwa": ServiceClass.STREAMING,
}

# Solo los eventos que efectivamente originan una sesión facturable generan CDR.
CDR_ELIGIBLE_EVENTS = {EventType.ATTACH}


@dataclass
class Event:
    event_id: str
    timestamp: str
    event_type: str
    result: str
    cause_code: str
    imsi: str
    cell_id: int
    enodeb_id: int
    mme_id: int
    tracking_area: int
    duration_ms: int
    rat_type: str
    apn: str
    plmn_id: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Cdr:
    cdr_id: str
    imsi: str
    session_start_time: str
    session_end_time: str
    duration_seconds: int
    apn: str
    plmn_id: str
    tracking_area: int
    cell_id: int
    rat_type: str
    bytes_uplink: int
    bytes_downlink: int
    bytes_total: int
    charging_type: str
    service_class: str

    def to_dict(self) -> Dict:
        return asdict(self)


class ImsiPool:
    """Mantiene un pool fijo de IMSIs con su categoria (LOCAL/VISITOR) asignada
    una sola vez, para que un mismo suscriptor sea consistente a lo largo de
    toda la corrida (mismo plmn_id, mismo tipo de APN elegible)."""

    def __init__(self, pool_size: int = 200):
        self.pool_size = pool_size
        self._pool: List[Tuple[str, str]] = self._build_pool()

    def _build_pool(self) -> List[Tuple[str, str]]:
        pool = []
        for _ in range(self.pool_size):
            plmn_id = random.choice(list(Imsi)).value
            imsi = f'IMSI_{plmn_id}{random.randint(1000000000, 9999999999)}'
            pool.append((imsi, plmn_id))
        return pool

    def sample(self) -> Tuple[str, str]:
        """Retorna (imsi, plmn_id) de un suscriptor existente en el pool."""
        return random.choice(self._pool)


class EventGenerator:
    def __init__(self, imsi_pool: ImsiPool):
        self.event_counter = 0
        self.imsi_pool = imsi_pool

    def _choose_event(self) -> EventType:
        return random.choice(list(EventType))

    def _rate_success(self, event_type: EventType, is_peak_hour: bool) -> ResultType:
        if is_peak_hour:
            return ResultType.SUCCESS if random.random() < SUCCESS_RATES_PEAK[event_type] else ResultType.FAILURE
        return ResultType.SUCCESS if random.random() < SUCCESS_RATES[event_type] else ResultType.FAILURE

    def _choose_cc(self, event_type: EventType, result: ResultType) -> str:
        if result == ResultType.SUCCESS:
            return random.choice(CAUSE_CODES_SUCCESS[event_type])
        return random.choice(CAUSE_CODES_FAILURE[event_type])

    def _rat_type(self) -> str:
        return random.choice(list(RatType)).value

    def _cell_id(self) -> int:
        return random.choice(ECGI)

    def _enodeb_id(self) -> int:
        return random.choice(ENODEB_IDS)

    def _mme_id(self) -> int:
        return random.choice(MME_IDS)

    def _tracking_area(self) -> int:
        return random.choice(TRACKING_AREAS)

    def _duration_ms(self) -> int:
        return random.randint(1, 1000)

    def _is_peak_hour(self, hour: int) -> bool:
        return hour in [7, 8, 9, 12, 13, 17, 18, 19, 20]

    def _apn(self, plmn_id: str) -> str:
        if plmn_id == Imsi.LOCAL.value:
            return random.choice(APN)
        return random.choice(APN[5:])

    def generate_event(self, logger: logging.Logger) -> Event:
        try:
            self.event_counter += 1
            now = datetime.now()
            timestamp = now.isoformat()
            is_peak_hour = self._is_peak_hour(now.hour)

            event_type = self._choose_event()
            result = self._rate_success(event_type, is_peak_hour)

            imsi, plmn_id = self.imsi_pool.sample()
            event_id = f"event_{self.event_counter}"
            logger.info(f"Generated event: {event_id} (peak_hour={is_peak_hour})")

            event = Event(
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type.value,
                result=result.value,
                cause_code=self._choose_cc(event_type, result),
                imsi=imsi,
                cell_id=self._cell_id(),
                enodeb_id=self._enodeb_id(),
                mme_id=self._mme_id(),
                tracking_area=self._tracking_area(),
                duration_ms=self._duration_ms(),
                rat_type=self._rat_type(),
                apn=self._apn(plmn_id),
                plmn_id=plmn_id
            )
            return event
        except Exception as e:
            logger.error(f"Error generating event: {e}")
            return None

    def generate_events(self, num_events: int, logger: logging.Logger) -> List[Event]:
        logger.info(f"Generating {num_events} events...")
        events = [self.generate_event(logger) for _ in range(num_events)]
        events = [e for e in events if e is not None]
        logger.info(f"Generated {len(events)} events.")
        return events

    def save_to_json(self, records: List, filename: Path, logger: logging.Logger) -> None:
        try:
            logger.info(f"Saving {len(records)} records to {filename}...")
            records_dict = [r.to_dict() for r in records]
            with open(filename, 'w') as f:
                json.dump(records_dict, f, indent=4)
            logger.info(f"Saved {len(records)} records to {filename}.")
        except OSError as e:
            logger.error(f"Failed to save records to {filename}: {e}")

    def save_to_csv(self, records: List, filename: Path, logger: logging.Logger) -> None:
        try:
            logger.info(f"Saving {len(records)} records to {filename}...")
            records_dict = [r.to_dict() for r in records]
            df = pd.DataFrame(records_dict)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(records)} records to {filename}.")
        except OSError as e:
            logger.error(f"Failed to save records to {filename}: {e}")


class CdrGenerator:
    def __init__(self):
        self.cdr_counter = 0

    def _charging_type(self) -> str:
        return random.choices(
            population=list(CHARGING_TYPE_WEIGHTS.keys()),
            weights=list(CHARGING_TYPE_WEIGHTS.values()),
        )[0].value

    def _service_class(self, apn: str) -> str:
        for prefix, service in SERVICE_CLASS_BY_APN_PREFIX.items():
            if apn.startswith(prefix):
                return service.value
        return ServiceClass.DATA.value

    def _session_duration(self) -> int:
        return random.randint(30, 3600)

    def _bytes_volume(self, service_class: str) -> Tuple[int, int]:
        ranges = {
            ServiceClass.STREAMING.value: ((1_000_000, 20_000_000), (50_000_000, 800_000_000)),
            ServiceClass.VOICE.value: ((500_000, 5_000_000), (500_000, 5_000_000)),
            ServiceClass.SMS.value: ((1_000, 5_000), (1_000, 5_000)),
            ServiceClass.DATA.value: ((500_000, 10_000_000), (1_000_000, 100_000_000)),
        }
        (up_lo, up_hi), (down_lo, down_hi) = ranges.get(service_class, ranges[ServiceClass.DATA.value])
        return random.randint(up_lo, up_hi), random.randint(down_lo, down_hi)

    def generate_cdr(self, event: Event, logger: logging.Logger):
        """Genera un CDR solo si el evento fue ATTACH exitoso."""
        if event.result != ResultType.SUCCESS.value:
            return None
        if EventType(event.event_type) not in CDR_ELIGIBLE_EVENTS:
            return None

        self.cdr_counter += 1
        service_class = self._service_class(event.apn)
        bytes_up, bytes_down = self._bytes_volume(service_class)
        duration = self._session_duration()
        start_dt = datetime.fromisoformat(event.timestamp)
        end_dt = datetime.fromtimestamp(start_dt.timestamp() + duration)

        cdr = Cdr(
            cdr_id=f"cdr_{self.cdr_counter}",
            imsi=event.imsi,
            session_start_time=event.timestamp,
            session_end_time=end_dt.isoformat(),
            duration_seconds=duration,
            apn=event.apn,
            plmn_id=event.plmn_id,
            tracking_area=event.tracking_area,
            cell_id=event.cell_id,
            rat_type=event.rat_type,
            bytes_uplink=bytes_up,
            bytes_downlink=bytes_down,
            bytes_total=bytes_up + bytes_down,
            charging_type=self._charging_type(),
            service_class=service_class,
        )
        logger.info(f"Generated CDR {cdr.cdr_id} for IMSI {cdr.imsi} (from {event.event_id})")
        return cdr

    def generate_cdrs(self, events: List[Event], logger: logging.Logger) -> List[Cdr]:
        cdrs = [self.generate_cdr(e, logger) for e in events]
        return [c for c in cdrs if c is not None]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("event_generator.log"),
            logging.StreamHandler()
        ]
    )


def run_batch(generator: EventGenerator, cdr_generator: CdrGenerator, num_events: int,
              fmt: str, output_dir: Path, cdr_dir: Path, logger: logging.Logger) -> None:
    events = generator.generate_events(num_events, logger)
    cdrs = cdr_generator.generate_cdrs(events, logger)
    logger.info(f"Generated {len(cdrs)} CDRs from {len(events)} events.")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    events_filename = output_dir / f"events_{timestamp}.{fmt}"
    cdrs_filename = cdr_dir / f"cdrs_{timestamp}.{fmt}"

    if fmt == "json":
        generator.save_to_json(events, events_filename, logger)
        generator.save_to_json(cdrs, cdrs_filename, logger)
    else:
        generator.save_to_csv(events, events_filename, logger)
        generator.save_to_csv(cdrs, cdrs_filename, logger)


def run_continuous(generator: EventGenerator, cdr_generator: CdrGenerator, num_events: int,
                    interval: int, fmt: str, output_dir: Path, cdr_dir: Path, logger: logging.Logger) -> None:
    batch_num = 0
    try:
        while True:
            batch_num += 1
            logger.info(f"Generating batch {batch_num}...")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            events = generator.generate_events(num_events, logger)
            cdrs = cdr_generator.generate_cdrs(events, logger)
            logger.info(f"Batch {batch_num}: {len(events)} events, {len(cdrs)} CDRs.")

            events_filename = output_dir / f"events_{timestamp}_batch{batch_num:04d}.{fmt}"
            cdrs_filename = cdr_dir / f"cdrs_{timestamp}_batch{batch_num:04d}.{fmt}"

            if fmt == "json":
                generator.save_to_json(events, events_filename, logger)
                generator.save_to_json(cdrs, cdrs_filename, logger)
            else:
                generator.save_to_csv(events, events_filename, logger)
                generator.save_to_csv(cdrs, cdrs_filename, logger)

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("\nStopping event generation...")


def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting event and CDR generation...")

    parser = argparse.ArgumentParser(description="Generate events and CDRs for SGSN-MME")
    parser.add_argument("--mode", choices=["batch", "continuous"], default="batch", help="Mode to generate events")
    parser.add_argument("--events", type=int, default=1000, help="Number of events to generate per batch")
    parser.add_argument("--interval", type=int, default=60, help="Interval between batches in seconds")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("--directory", type=str, default="data/raw", help="Directory to save events")
    parser.add_argument("--pool-size", type=int, default=200, help="Number of unique IMSIs in the subscriber pool")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility (any integer)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        logger.info(f"Random seed set to {args.seed}")

    imsi_pool = ImsiPool(pool_size=args.pool_size)
    generator = EventGenerator(imsi_pool)
    cdr_generator = CdrGenerator()

    output_dir = Path(args.directory)
    events_dir = output_dir / "events"
    cdr_dir = output_dir / "cdrs"
    events_dir.mkdir(parents=True, exist_ok=True)
    cdr_dir.mkdir(parents=True, exist_ok=True)

    if args.mode == "batch":
        run_batch(generator, cdr_generator, args.events, args.format, events_dir, cdr_dir, logger)
    else:
        run_continuous(generator, cdr_generator, args.events, args.interval, args.format, events_dir, cdr_dir, logger)


if __name__ == "__main__":
    main()
