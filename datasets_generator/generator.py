import json
from datetime import datetime
import random
from enum import Enum
import argparse
from typing import Dict, List
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
    EventType.ATTACH: [
        "0_attach success"
    ],
    EventType.HANDOVER: [
        "0_handover success"
    ],
    EventType.PAGING: [
        "0_paging success"
    ],
    EventType.SERVICE_REQUEST: [
        "0_service request success"
    ]
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

ECGI = [2341012541, 2341019851, 2341012552, 2341019862, 2341012563, 2341019873] ## 3GPP TS 23.003 ECGI = PLMN Identity + ECI (28 bits eNodeB ID + Cell ID)
ENODEB_IDS = [1254, 1985, 1255, 1986, 1256, 1987] ## Remove
MME_IDS = [1, 2] ## 3GPP TS 23.003 MME ID = 20 bits (0x00000–0xFFFFE) but we will use a smaller range for simplicity
TRACKING_AREAS = [234101, 234102, 234103, 234104, 234105] ## 3GPP TS 23.003 TAI = MCC + MNC + TAC(16 bits (0x0000–0xFFFE))
APN = ['internet.mcc10.mnc234.gprs', 'mms.mcc10.mnc234.gprs', 'ims.mcc10.mnc234.gprs', 'vpn.mcc10.mnc234.gprs','fwa.mcc10.mnc234.gprs',
       'internet.mcc11.mnc234.gprs','internet.mcc12.mnc234.gprs','internet.mcc13.mnc234.gprs']

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
    apn : str
    plmn_id : str

    def to_dict(self, logger: logging.Logger) -> Dict:
        """Convierte el evento a diccionario."""
        return asdict(self)
    
class EventGenerator:
    def __init__(self):
        self.event_counter = 0

    def _choose_event(self) -> EventType:
        """Returns a random EventType."""
        return random.choice(list(EventType))

    def _rate_success(self, event_type: EventType, is_peak_hour: bool, logger: logging.Logger) -> ResultType:
        """Returns SUCCESS or FAILURE based on the event type's success rate."""
        if is_peak_hour:
            return ResultType.SUCCESS if random.random() < SUCCESS_RATES_PEAK[event_type] else ResultType.FAILURE
        return ResultType.SUCCESS if random.random() < SUCCESS_RATES[event_type] else ResultType.FAILURE

    def _choose_cc(self, event_type: EventType, result: ResultType) -> str:
        """Returns a random cause code matching the event type and result."""
        if result == ResultType.SUCCESS:
            return random.choice(CAUSE_CODES_SUCCESS[event_type])
        return random.choice(CAUSE_CODES_FAILURE[event_type])

    def _range_imsi(self) -> str:
        """Returns a random IMSI string."""
        self.plmn_id = random.choice(list(Imsi)).value
        return f'IMSI_{self.plmn_id}{random.randint(1000000000, 9999999999)}'

    def _rat_type(self) -> str:
        """Returns a random RAT type string."""
        return random.choice(list(RatType)).value

    def _cell_id(self) -> int:
        """Returns a random cell ID."""
        return random.choice(ECGI)

    def _enodeb_id(self) -> int:
        """Returns a random eNodeB ID."""
        return random.choice(ENODEB_IDS)

    def _mme_id(self) -> int:
        """Returns a random MME ID."""
        return random.choice(MME_IDS)

    def _tracking_area(self) -> int:
        """Returns a random tracking area code."""
        return random.choice(TRACKING_AREAS)

    def _duration_ms(self) -> int:
        """Returns a random duration in milliseconds."""
        return random.randint(1, 1000)

    def _is_peak_hour(self, hour: int) -> bool:
        """Returns True if the given hour is considered a peak traffic hour."""
        return hour in [7, 8, 9, 12, 13, 17, 18, 19, 20]
    def _apn(self) -> str:
        """Returns a random APN string."""
        if self.plmn_id == Imsi.LOCAL.value:
            return random.choice(APN)
        else:
            return random.choice(APN[5:])

    def generate_event(self, logger: logging.Logger) -> Event:
        """Generates a single random Event."""
        try:
            self.event_counter += 1
            now = datetime.now()
            timestamp = now.isoformat()
            is_peak_hour = self._is_peak_hour(now.hour)
            
            event_type = self._choose_event()
            result = self._rate_success(event_type, is_peak_hour, logger)

            event_id = f"event_{self.event_counter}"
            logger.info(f"Generated event: {event_id} (peak_hour={is_peak_hour})")

            event = Event(
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type.value,
                result=result.value,
                cause_code=self._choose_cc(event_type, result),
                imsi=self._range_imsi(),
                cell_id=self._cell_id(),
                enodeb_id=self._enodeb_id(),
                mme_id=self._mme_id(),
                tracking_area=self._tracking_area(),
                duration_ms=self._duration_ms(),
                rat_type=self._rat_type(),
                apn=self._apn(),
                plmn_id=self.plmn_id
            )
            return event
        except Exception as e:
            logger.error(f"Error generating event: {e}")
            return None

    def generate_events(self, num_events: int, logger: logging.Logger) -> List[Event]:
        """Generates a list of random Events."""
        logger.info(f"Generating {num_events} events...")
        events = [self.generate_event(logger) for _ in range(num_events)]
        logger.info(f"Generated {len(events)} events.")
        return events

    def continuous_generation(self, num_events: int, interval: int, logger: logging.Logger, output_dir: Path = Path("./")) -> None:
        """Continuously generates batches of events at a fixed interval until interrupted."""
        batch_num = 0
        try:    
            while True:
                batch_num += 1
                timestamp = datetime.now()
                logger.info(f"Generating batch {batch_num}...")
                events = self.generate_events(num_events, logger)
                logger.info(f"Generated batch {batch_num} with {num_events} events.")
                filename = f"events_{timestamp.strftime('%Y%m%d_%H%M%S')}_batch{batch_num:04d}.json"
                filepath = output_dir / filename
                
                self.save_to_json(events, filepath, logger)
                logger.info(f"Saved batch {batch_num} with {num_events} events to {filepath}")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\nStopping event generation...")

    def save_to_json(self, events: List[Event], filename: Path, logger: logging.Logger) -> None:
        """Saves a list of events to a JSON file."""
        try:
            logger.info(f"Saving {len(events)} events to {filename}...")
            events_dict = [event.to_dict(logger) for event in events]
            with open(filename, 'w') as f:
                json.dump(events_dict, f, indent=4) 
            logger.info(f"Saved {len(events)} events to {filename}.")
        except OSError as e:
            logger.error(f"Failed to save events to {filename}: {e}")

    def save_to_csv(self, events: List[Event], filename: Path, logger: logging.Logger) -> None:
        """Saves a list of events to a CSV file."""
        try:
            logger.info(f"Saving {len(events)} events to {filename}...")
            events_dict = [event.to_dict(logger) for event in events]
            df = pd.DataFrame(events_dict)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(events)} events to {filename}.")
        except OSError as e:
            logger.error(f"Failed to save events to {filename}: {e}")

def setup_logging() -> None:
    """Configures logging to output to both a file and the console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("event_generator.log"),
            logging.StreamHandler()
        ]
    )   

def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting event generation...")

    parser = argparse.ArgumentParser(description="Generate events for SGSN-MME")
    parser.add_argument("--mode", choices=["batch", "continuous"], default="batch", help="Mode to generate events")
    parser.add_argument("--events", type=int, default=1000, help="Number of events to generate")
    parser.add_argument("--interval", type=int, default=60, help="Interval between batches in seconds")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("--directory", type=str, default="data/raw", help="Directory to save events")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility (any integer)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        logger.info(f"Random seed set to {args.seed}")

    generator = EventGenerator()
    output_dir = Path(args.directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.mode == "batch":
        logger.info(f"Generating {args.events} events in batch mode...")
        events = generator.generate_events(args.events, logger)
        if args.format == "json":
            filename = output_dir / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            generator.save_to_json(events, filename, logger)
        else:
            filename = output_dir / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            generator.save_to_csv(events, filename, logger)
    else:
        logger.info("Generating events in continuous mode...")
        generator.continuous_generation(args.events, args.interval, logger, output_dir)

if __name__ == "__main__":
    main()