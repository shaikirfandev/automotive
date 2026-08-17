# Part 2: Automotive Libraries, Protocols & HIL Integration (Intermediate)

---

## 2.1 Custom Python Libraries for Robot Framework

In automotive testing, you interact with hardware (CAN interfaces, HIL benches, ECUs) through **custom Python libraries**.

### How Robot Framework Finds Libraries

```robot
*** Settings ***
# 1. Built-in or pip-installed
Library    Collections
Library    OperatingSystem

# 2. Custom library by module path
Library    ../../libraries/CanBusLibrary.py

# 3. Library with constructor arguments
Library    ../../libraries/UdsLibrary.py    channel=can0    timeout=5
```

### Writing a Custom Library

```python
# libraries/CanBusLibrary.py
"""
Robot Framework library for CAN bus communication.
Uses python-can under the hood.
"""
import can
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class CanBusLibrary:
    """Library for sending and receiving CAN messages in automotive tests."""

    def __init__(self):
        self._bus = None
        self._db = None  # DBC database

    @keyword("Open CAN Channel")
    def open_can_channel(self, channel="can0", bitrate=500000, interface="socketcan"):
        """Opens a CAN channel for communication.

        Arguments:
        - channel: CAN interface name (e.g., can0, vcan0)
        - bitrate: Bus speed in bps (default 500000)
        - interface: python-can interface type
        """
        self._bus = can.Bus(channel=channel, interface=interface, bitrate=int(bitrate))
        logger.info(f"CAN channel opened: {channel} @ {bitrate} bps")

    @keyword("Close CAN Channel")
    def close_can_channel(self):
        """Closes the active CAN channel."""
        if self._bus:
            self._bus.shutdown()
            logger.info("CAN channel closed")

    @keyword("Send CAN Message")
    def send_can_message(self, arbitration_id, data, is_extended=False):
        """Sends a raw CAN message.

        Arguments:
        - arbitration_id: CAN ID (hex string or integer)
        - data: Data bytes as hex string (e.g., '0102030405060708')
        - is_extended: Whether to use extended frame format
        """
        arb_id = int(str(arbitration_id), 0)
        data_bytes = bytes.fromhex(data)
        msg = can.Message(
            arbitration_id=arb_id,
            data=data_bytes,
            is_extended_id=bool(is_extended)
        )
        self._bus.send(msg)
        logger.info(f"Sent CAN message: ID=0x{arb_id:X}, Data={data}")

    @keyword("Receive CAN Message")
    def receive_can_message(self, timeout=2.0):
        """Receives a CAN message with timeout.

        Returns a dictionary with keys: id, data, timestamp, dlc.
        """
        msg = self._bus.recv(timeout=float(timeout))
        if msg is None:
            raise AssertionError(f"No CAN message received within {timeout}s")
        result = {
            "id": hex(msg.arbitration_id),
            "data": msg.data.hex(),
            "timestamp": msg.timestamp,
            "dlc": msg.dlc
        }
        logger.info(f"Received CAN: {result}")
        return result

    @keyword("Send CAN Signal")
    def send_can_signal(self, signal_name, value):
        """Sends a named CAN signal using DBC database encoding."""
        # In production, this would use cantools to encode signals from DBC
        logger.info(f"Sending signal {signal_name} = {value}")
        # Placeholder — see Section 2.2 for DBC integration

    @keyword("Read CAN Signal")
    def read_can_signal(self, signal_name):
        """Reads a named CAN signal using DBC database decoding."""
        logger.info(f"Reading signal {signal_name}")
        # Placeholder — see Section 2.2 for DBC integration
        return 0
```

---

## 2.2 CAN Bus Testing with DBC Files

### What Is a DBC File?

A DBC file defines the CAN database — messages, signals, encoding rules. It is the **most important artifact** in CAN-based automotive testing.

### DBC-Aware Library with cantools

```python
# libraries/CanSignalLibrary.py
"""
CAN signal-level library using DBC files for encoding/decoding.
"""
import can
import cantools
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class CanSignalLibrary:

    def __init__(self):
        self._bus = None
        self._db = None

    @keyword("Load DBC File")
    def load_dbc_file(self, dbc_path):
        """Loads a DBC file for signal encoding/decoding."""
        self._db = cantools.database.load_file(dbc_path)
        logger.info(f"Loaded DBC: {dbc_path} ({len(self._db.messages)} messages)")

    @keyword("Open CAN Channel")
    def open_can_channel(self, channel="vcan0", interface="socketcan"):
        self._bus = can.Bus(channel=channel, interface=interface)

    @keyword("Close CAN Channel")
    def close_can_channel(self):
        if self._bus:
            self._bus.shutdown()

    @keyword("Send Signal")
    def send_signal(self, message_name, **signals):
        """Sends CAN signals by name.

        Example in Robot:
            Send Signal    VehicleDynamics    VehicleSpeed=100    EngineRPM=3000
        """
        msg_def = self._db.get_message_by_name(message_name)
        data = msg_def.encode(signals)
        msg = can.Message(arbitration_id=msg_def.frame_id, data=data)
        self._bus.send(msg)
        logger.info(f"Sent {message_name}: {signals}")

    @keyword("Read Signal Value")
    def read_signal_value(self, message_name, signal_name, timeout=2.0):
        """Reads a specific signal from the CAN bus.

        Waits for the matching message and decodes the signal.
        """
        msg_def = self._db.get_message_by_name(message_name)
        msg = self._bus.recv(timeout=float(timeout))
        if msg is None:
            raise AssertionError(f"No message received for {message_name}")
        if msg.arbitration_id != msg_def.frame_id:
            raise AssertionError(
                f"Expected ID 0x{msg_def.frame_id:X}, got 0x{msg.arbitration_id:X}"
            )
        decoded = msg_def.decode(msg.data)
        value = decoded.get(signal_name)
        logger.info(f"Read {signal_name} = {value}")
        return value
```

### Using in Robot Framework

```robot
*** Settings ***
Library    ../../libraries/CanSignalLibrary.py

Suite Setup       Setup CAN Environment
Suite Teardown    Close CAN Channel

*** Keywords ***
Setup CAN Environment
    Load DBC File       data/dbc_files/vehicle_dynamics.dbc
    Open CAN Channel    vcan0

*** Test Cases ***
TC-001: Verify Speed Signal Transmission
    Send Signal    VehicleDynamics    VehicleSpeed=100
    ${speed}=    Read Signal Value    VehicleDynamics    VehicleSpeed
    Should Be Equal As Numbers    ${speed}    100

TC-002: Verify Multiple Signals
    Send Signal    VehicleDynamics    VehicleSpeed=80    EngineRPM=2500
    ${speed}=    Read Signal Value    VehicleDynamics    VehicleSpeed
    ${rpm}=      Read Signal Value    VehicleDynamics    EngineRPM
    Should Be Equal As Numbers    ${speed}    80
    Should Be Equal As Numbers    ${rpm}      2500
```

---

## 2.3 UDS (Unified Diagnostic Services) Library

UDS (ISO 14229) is the standard protocol for ECU diagnostics.

### Custom UDS Library

```python
# libraries/UdsLibrary.py
"""
Robot Framework library for UDS (ISO 14229) diagnostic communication.
Uses udsoncan and python-can.
"""
import can
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
import isotp
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class UdsLibrary:

    def __init__(self):
        self._client = None
        self._bus = None

    @keyword("Connect To ECU")
    def connect_to_ecu(self, channel="vcan0", tx_id=0x7E0, rx_id=0x7E8):
        """Establishes a UDS connection to an ECU.

        Arguments:
        - channel: CAN channel
        - tx_id: Request CAN ID (hex)
        - rx_id: Response CAN ID (hex)
        """
        self._bus = can.Bus(channel=channel, interface="socketcan")
        tp_layer = isotp.CanStack(
            bus=self._bus,
            address=isotp.Address(
                addressing_mode=isotp.AddressingMode.Normal_11bits,
                txid=int(str(tx_id), 0),
                rxid=int(str(rx_id), 0)
            )
        )
        conn = PythonIsoTpConnection(tp_layer)
        self._client = Client(conn)
        self._client.open()
        logger.info(f"UDS connected: TX=0x{int(str(tx_id),0):X}, RX=0x{int(str(rx_id),0):X}")

    @keyword("Disconnect From ECU")
    def disconnect_from_ecu(self):
        if self._client:
            self._client.close()
        if self._bus:
            self._bus.shutdown()

    @keyword("Read DID")
    def read_did(self, did):
        """Reads a Data Identifier from the ECU.

        Arguments:
        - did: Data Identifier (hex string, e.g., F190)

        Returns the value as a hex string.
        """
        did_int = int(str(did), 16)
        response = self._client.read_data_by_identifier(did_int)
        value = response.service_data.values[did_int]
        logger.info(f"DID 0x{did_int:04X} = {value}")
        return value

    @keyword("Write DID")
    def write_did(self, did, value):
        """Writes a Data Identifier to the ECU."""
        did_int = int(str(did), 16)
        self._client.write_data_by_identifier(did_int, bytes.fromhex(str(value)))
        logger.info(f"Wrote DID 0x{did_int:04X} = {value}")

    @keyword("Change Diagnostic Session")
    def change_diagnostic_session(self, session):
        """Changes the UDS diagnostic session.

        Arguments:
        - session: default, programming, extended
        """
        session_map = {
            "default": 0x01,
            "programming": 0x02,
            "extended": 0x03
        }
        session_id = session_map.get(str(session).lower(), int(str(session), 0))
        self._client.change_session(session_id)
        logger.info(f"Session changed to: {session}")

    @keyword("Read DTCs")
    def read_dtcs(self):
        """Reads all active Diagnostic Trouble Codes from the ECU."""
        response = self._client.get_dtc_by_status_mask(0xFF)
        dtcs = []
        for dtc in response.service_data.dtcs:
            dtcs.append({
                "id": hex(dtc.id),
                "status": dtc.status.get_byte_as_int()
            })
        logger.info(f"Found {len(dtcs)} DTCs")
        return dtcs

    @keyword("Clear DTCs")
    def clear_dtcs(self):
        """Clears all DTCs from the ECU."""
        self._client.clear_dtc(0xFFFFFF)
        logger.info("DTCs cleared")

    @keyword("Tester Present")
    def tester_present(self):
        """Sends TesterPresent to keep the session alive."""
        self._client.tester_present()

    @keyword("ECU Reset")
    def ecu_reset(self, reset_type="hard"):
        """Resets the ECU.

        Arguments:
        - reset_type: hard, key_off_on, soft
        """
        type_map = {"hard": 0x01, "key_off_on": 0x02, "soft": 0x03}
        self._client.ecu_reset(type_map.get(reset_type, 0x01))
        logger.info(f"ECU reset: {reset_type}")
```

### UDS Tests in Robot Framework

```robot
*** Settings ***
Library    ../../libraries/UdsLibrary.py

Suite Setup       Connect To ECU    vcan0    0x7E0    0x7E8
Suite Teardown    Disconnect From ECU

*** Test Cases ***
TC-UDS-001: Read ECU Part Number
    [Tags]    uds    diagnostics    smoke
    Change Diagnostic Session    extended
    ${part_number}=    Read DID    F187
    Should Not Be Empty    ${part_number}
    Log    ECU Part Number: ${part_number}

TC-UDS-002: Read And Clear DTCs
    [Tags]    uds    dtc    functional
    ${dtcs}=    Read DTCs
    Log    Active DTCs: ${dtcs}
    Clear DTCs
    ${dtcs_after}=    Read DTCs
    Length Should Be    ${dtcs_after}    0

TC-UDS-003: ECU Reset And Recovery
    [Tags]    uds    reset    functional
    ECU Reset    hard
    Sleep    3s    Wait for ECU reboot
    Tester Present
    Change Diagnostic Session    default
    ${part_number}=    Read DID    F187
    Should Not Be Empty    ${part_number}

TC-UDS-004: Write And Verify VIN
    [Tags]    uds    vin    functional
    Change Diagnostic Session    extended
    # Security access would be needed in production
    Write DID    F190    574241585858585858585858585858585858
    ${vin}=    Read DID    F190
    Log    VIN: ${vin}
```

---

## 2.4 LIN Bus Library

LIN (Local Interconnect Network) is used for low-speed, cost-sensitive ECUs (seat control, window motors, mirrors).

```python
# libraries/LinBusLibrary.py
"""
Robot Framework library for LIN bus communication.
"""
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class LinBusLibrary:

    def __init__(self):
        self._interface = None

    @keyword("Open LIN Channel")
    def open_lin_channel(self, channel, baudrate=19200):
        """Opens a LIN communication channel."""
        # Implementation depends on hardware (e.g., Peak PLIN, Vector VN)
        logger.info(f"LIN channel opened: {channel} @ {baudrate} baud")

    @keyword("Send LIN Frame")
    def send_lin_frame(self, frame_id, data):
        """Sends a LIN frame as master.

        Arguments:
        - frame_id: LIN protected identifier (0-63)
        - data: Data bytes as hex string
        """
        logger.info(f"LIN TX: ID={frame_id}, Data={data}")

    @keyword("Read LIN Response")
    def read_lin_response(self, frame_id, timeout=1.0):
        """Reads a LIN slave response.

        Arguments:
        - frame_id: Frame ID to poll
        - timeout: Timeout in seconds
        """
        logger.info(f"LIN RX: ID={frame_id}")
        return "00"

    @keyword("Close LIN Channel")
    def close_lin_channel(self):
        if self._interface:
            logger.info("LIN channel closed")
```

---

## 2.5 Automotive Ethernet / DoIP Library

Modern vehicles (especially ADAS and Infotainment) increasingly use Ethernet. DoIP (Diagnostics over IP, ISO 13400) is the diagnostic protocol over Ethernet.

```python
# libraries/DoipLibrary.py
"""
Robot Framework library for DoIP (Diagnostics over IP) communication.
"""
import socket
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class DoipLibrary:

    DOIP_PORT = 13400

    def __init__(self):
        self._socket = None

    @keyword("Connect DoIP")
    def connect_doip(self, ip_address, port=13400):
        """Establishes a DoIP TCP connection to the ECU."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(5)
        self._socket.connect((ip_address, int(port)))
        logger.info(f"DoIP connected to {ip_address}:{port}")

    @keyword("Send DoIP Vehicle Identification Request")
    def send_vehicle_id_request(self):
        """Sends a DoIP vehicle identification request (broadcast)."""
        # DoIP header: version=0x02, type=0x0001 (Vehicle ID Request)
        header = bytes([0x02, 0xFD, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00])
        self._socket.send(header)
        logger.info("Sent DoIP Vehicle ID Request")

    @keyword("Send DoIP Diagnostic Message")
    def send_diagnostic_message(self, source_addr, target_addr, uds_data):
        """Sends a UDS request over DoIP.

        Arguments:
        - source_addr: Tester logical address (hex)
        - target_addr: ECU logical address (hex)
        - uds_data: UDS payload as hex string
        """
        sa = int(str(source_addr), 16)
        ta = int(str(target_addr), 16)
        payload = sa.to_bytes(2, 'big') + ta.to_bytes(2, 'big') + bytes.fromhex(uds_data)
        payload_len = len(payload)
        header = bytes([0x02, 0xFD, 0x80, 0x01]) + payload_len.to_bytes(4, 'big')
        self._socket.send(header + payload)
        logger.info(f"DoIP TX: SA=0x{sa:04X}, TA=0x{ta:04X}, Data={uds_data}")

    @keyword("Receive DoIP Response")
    def receive_doip_response(self, timeout=5):
        """Receives a DoIP response."""
        self._socket.settimeout(float(timeout))
        data = self._socket.recv(4096)
        logger.info(f"DoIP RX: {data.hex()}")
        return data.hex()

    @keyword("Disconnect DoIP")
    def disconnect_doip(self):
        if self._socket:
            self._socket.close()
            logger.info("DoIP disconnected")
```

### DoIP Test Example

```robot
*** Settings ***
Library    ../../libraries/DoipLibrary.py

Suite Setup       Connect DoIP    192.168.1.100    13400
Suite Teardown    Disconnect DoIP

*** Test Cases ***
TC-DOIP-001: Vehicle Identification
    [Tags]    doip    ethernet    smoke
    Send DoIP Vehicle Identification Request
    ${response}=    Receive DoIP Response
    Should Not Be Empty    ${response}
    Log    Vehicle ID Response: ${response}

TC-DOIP-002: Diagnostic Session Over Ethernet
    [Tags]    doip    uds    functional
    # DiagnosticSessionControl - Extended Session (10 03)
    Send DoIP Diagnostic Message    0x0E80    0x1000    1003
    ${response}=    Receive DoIP Response
    Log    Session Response: ${response}
```

---

## 2.6 HIL (Hardware-in-the-Loop) Integration

### HIL Architecture with Robot Framework

```
┌─────────────────────────────────────────────────────────┐
│                    Test PC                               │
│  ┌──────────────┐   ┌──────────────┐                    │
│  │ Robot Tests   │──▶│ Python Libs  │                    │
│  │ (.robot)      │   │ (CAN/UDS/HIL)│                    │
│  └──────────────┘   └──────┬───────┘                    │
│                            │                             │
├────────────────────────────┼─────────────────────────────┤
│                            │ CAN / Ethernet / Serial     │
│                    ┌───────▼────────┐                    │
│                    │  HIL Simulator  │                    │
│                    │  (dSPACE/NI/   │                    │
│                    │   ETAS/Vector)  │                    │
│                    └───────┬────────┘                    │
│                            │                             │
│                    ┌───────▼────────┐                    │
│                    │   ECU Under    │                    │
│                    │     Test       │                    │
│                    └────────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### HIL Control Library

```python
# libraries/HilControlLibrary.py
"""
Robot Framework library for HIL bench control.
Abstracts common HIL operations across vendors.
"""
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class HilControlLibrary:

    def __init__(self):
        self._hil = None

    @keyword("Connect To HIL Bench")
    def connect_to_hil_bench(self, bench_ip, bench_type="dspace"):
        """Connects to the HIL bench.

        Arguments:
        - bench_ip: IP address of the HIL simulator
        - bench_type: dspace, ni, etas, vector
        """
        logger.info(f"Connected to {bench_type} HIL bench at {bench_ip}")

    @keyword("Disconnect From HIL Bench")
    def disconnect_from_hil_bench(self):
        logger.info("Disconnected from HIL bench")

    @keyword("Set Plant Model Variable")
    def set_plant_model_variable(self, variable_path, value):
        """Sets a variable in the plant model simulation.

        Example:
            Set Plant Model Variable    Vehicle.Speed    100
            Set Plant Model Variable    Sensor.Radar.FrontObject.Distance    50
        """
        logger.info(f"HIL set: {variable_path} = {value}")

    @keyword("Get Plant Model Variable")
    def get_plant_model_variable(self, variable_path):
        """Gets a variable value from the plant model."""
        logger.info(f"HIL get: {variable_path}")
        return 0

    @keyword("Simulate Ignition On")
    def simulate_ignition_on(self):
        """Simulates turning the ignition key to ON."""
        logger.info("Ignition ON simulated")

    @keyword("Simulate Ignition Off")
    def simulate_ignition_off(self):
        """Simulates turning the ignition key to OFF."""
        logger.info("Ignition OFF simulated")

    @keyword("Power On ECU")
    def power_on_ecu(self):
        """Powers on the ECU under test via HIL relay."""
        logger.info("ECU powered ON")

    @keyword("Power Off ECU")
    def power_off_ecu(self):
        """Powers off the ECU under test."""
        logger.info("ECU powered OFF")

    @keyword("Set Battery Voltage")
    def set_battery_voltage(self, voltage):
        """Sets the simulated battery voltage.

        Arguments:
        - voltage: Voltage in volts (e.g., 12.0, 9.0, 16.0)
        """
        logger.info(f"Battery voltage set to {voltage}V")

    @keyword("Inject Fault")
    def inject_fault(self, fault_type, target):
        """Injects a fault for testing ECU fault handling.

        Arguments:
        - fault_type: open_circuit, short_to_ground, short_to_battery, signal_stuck
        - target: Signal or component name
        """
        logger.info(f"Fault injected: {fault_type} on {target}")

    @keyword("Remove Fault")
    def remove_fault(self, target):
        """Removes a previously injected fault."""
        logger.info(f"Fault removed on {target}")

    @keyword("Start Scenario")
    def start_scenario(self, scenario_file):
        """Starts a pre-recorded driving scenario.

        Arguments:
        - scenario_file: Path to scenario file (.mat, .mdf, etc.)
        """
        logger.info(f"Scenario started: {scenario_file}")

    @keyword("Stop Scenario")
    def stop_scenario(self):
        """Stops the currently running scenario."""
        logger.info("Scenario stopped")
```

---

## 2.7 Serial / UART Communication

Many ECUs expose debug consoles or bootloaders via serial interfaces.

```robot
*** Settings ***
Library    SerialLibrary    # pip install robotframework-seriallibrary

*** Test Cases ***
TC-SERIAL-001: Read ECU Boot Log
    [Tags]    serial    debug
    Open Serial Port    /dev/ttyUSB0    baudrate=115200
    ${boot_log}=    Read Until    Login:    timeout=30
    Should Contain    ${boot_log}    Boot complete
    Close Serial Port
```

---

## 2.8 SSH for Linux-Based ECUs

Modern Infotainment and ADAS ECUs often run Linux (Yocto, Android Automotive).

```robot
*** Settings ***
Library    SSHLibrary    # pip install robotframework-sshlibrary

Suite Setup       Open SSH Connection
Suite Teardown    Close All Connections

*** Keywords ***
Open SSH Connection
    Open Connection    192.168.1.10
    Login    root    password123

*** Test Cases ***
TC-SSH-001: Check ECU Linux Kernel Version
    [Tags]    ssh    infotainment    smoke
    ${output}=    Execute Command    uname -r
    Should Match Regexp    ${output}    ^5\\.

TC-SSH-002: Check ADAS Application Is Running
    [Tags]    ssh    adas    process
    ${output}=    Execute Command    ps aux | grep adas_controller
    Should Contain    ${output}    adas_controller

TC-SSH-003: Check Available Disk Space
    [Tags]    ssh    health
    ${output}=    Execute Command    df -h /
    Log    Disk usage: ${output}
```

---

## 2.9 REST API Testing for Connected Vehicles

Telematics and cloud-connected features expose REST APIs.

```robot
*** Settings ***
Library    RequestsLibrary    # pip install robotframework-requests
Library    Collections

*** Variables ***
${BASE_URL}    https://api.vehicle-cloud.example.com/v1
&{HEADERS}     Content-Type=application/json    Authorization=******

*** Test Cases ***
TC-API-001: Get Vehicle Status
    [Tags]    api    telematics    smoke
    Create Session    cloud    ${BASE_URL}    headers=&{HEADERS}
    ${resp}=    GET On Session    cloud    /vehicles/VIN123/status
    Status Should Be    200    ${resp}
    Dictionary Should Contain Key    ${resp.json()}    batteryLevel

TC-API-002: Send Remote Lock Command
    [Tags]    api    telematics    remote-control
    Create Session    cloud    ${BASE_URL}    headers=&{HEADERS}
    ${body}=    Create Dictionary    command=lock    pin=1234
    ${resp}=    POST On Session    cloud    /vehicles/VIN123/commands    json=${body}
    Status Should Be    202    ${resp}
```

---

## 2.10 Summary: Protocol-to-Library Mapping

| Protocol | Python Package | Robot Library |
|----------|---------------|---------------|
| CAN | `python-can`, `cantools` | Custom `CanSignalLibrary` |
| UDS (ISO 14229) | `udsoncan`, `python-isotp` | Custom `UdsLibrary` |
| DoIP (ISO 13400) | Custom / `doipclient` | Custom `DoipLibrary` |
| LIN | Vendor SDK | Custom `LinBusLibrary` |
| Ethernet | `socket`, `scapy` | Custom or `RequestsLibrary` |
| Serial/UART | `pyserial` | `SerialLibrary` |
| SSH | `paramiko` | `SSHLibrary` |
| REST API | `requests` | `RequestsLibrary` |
| MQTT | `paho-mqtt` | Custom `MqttLibrary` |
| SOME/IP | `someip` | Custom |

---

## 2.11 Exercises — Intermediate Level

1. **Write a CAN library** that opens a virtual CAN channel (`vcan0`) and sends/receives raw messages.
2. **Integrate a DBC file** — use `cantools` to encode/decode signals by name.
3. **Create a UDS test suite** that reads 3 different DIDs and validates their format.
4. **Write a keyword** `Wait For Signal Value` that retries reading a CAN signal until it matches or times out.
5. **Build an HIL keyword layer** with Setup/Teardown that powers the ECU on and off.
6. **Test a REST API** — create a mock vehicle API and write Robot tests to validate endpoints.

---

*Next: [Part 3 — ADAS Testing with Robot Framework →](ROBOT_FRAMEWORK_AUTOMOTIVE_PART3.md)*
