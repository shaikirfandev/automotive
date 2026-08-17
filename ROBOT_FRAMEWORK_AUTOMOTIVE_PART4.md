# Part 4: Infotainment & Instrument Cluster Testing (Intermediate–Advanced)

[← Previous: Part 3](ROBOT_FRAMEWORK_AUTOMOTIVE_PART3.md) | [Next: Part 5 →](ROBOT_FRAMEWORK_AUTOMOTIVE_PART5.md)

---

## 4.1 Learning Objectives

By the end of this part, you should be able to:

- understand infotainment and instrument cluster system architecture
- design Robot Framework tests for media, navigation, Bluetooth, projection, voice, and OTA workflows
- combine UI, CAN, GPS, audio, and image-based verification in one automation strategy
- validate digital cluster tell-tales, gauge behavior, and warning priorities
- build reusable Python libraries for HMI, CAN, GPS simulation, audio capture, and visual comparison
- create robust intermediate-to-advanced test suites for automotive display systems

---

## 4.2 Infotainment System Architecture

Infotainment systems are highly integrated embedded platforms combining multimedia, connectivity, navigation, telephony, voice, projection, and vehicle settings.

### 4.2.1 Major Building Blocks

| Component | Purpose | Typical Interfaces | Common Test Focus |
|-----------|---------|--------------------|-------------------|
| **Head Unit / IVI ECU** | Main compute platform running HMI and apps | Ethernet, CAN, USB, Wi-Fi, Bluetooth, LVDS, HDMI, Audio I/O | boot, stability, responsiveness |
| **Center Display** | Main touchscreen display | MIPI, LVDS, eDP | rendering, touch accuracy, brightness |
| **Rear Displays** | Rear seat entertainment or auxiliary displays | HDMI, Ethernet, LVDS | media sync, content routing |
| **Amplifier / DSP** | Audio routing and enhancement | I2S, TDM, MOST, A2B, Ethernet | volume, balance, fade, distortion |
| **Telematics / Connectivity Module** | Cellular, Wi-Fi hotspot, OTA access | USB, PCIe, Ethernet | network attach, handover, update robustness |
| **Bluetooth/Wi-Fi Stack** | Wireless device connectivity | BT Classic, BLE, Wi-Fi | pairing, reconnect, throughput |
| **Projection Gateway** | CarPlay / Android Auto projection | USB, Wi-Fi, BT | launch, audio routing, control handoff |
| **Vehicle Interface Layer** | Bridges infotainment with vehicle signals | CAN, LIN, SOME/IP | speed lockouts, reverse camera trigger |

### 4.2.2 High-Level Infotainment Architecture

```text
+--------------------------------------------------------------+
|                       Vehicle Network                        |
|  CAN / LIN / FlexRay / Automotive Ethernet / SOME-IP         |
+---------------------------+----------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|                  Vehicle Interface / Gateway                 |
|   Signal mapping, diagnostics, state sync, feature gating    |
+---------------------------+----------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|                    Infotainment Head Unit                    |
|  +-------------------+   +--------------------------------+  |
|  | HMI / App Layer   |   | Service Layer                  |  |
|  | Media, Nav, Phone |   | BT, Wi-Fi, Voice, Projection   |  |
|  +-------------------+   +--------------------------------+  |
|  | OS / Middleware   |   | HAL / Device Drivers           |  |
|  | Linux / Android   |   | Touch, Audio, Display, USB     |  |
|  +-------------------+   +--------------------------------+  |
+--------+------------+-----------+------------+---------------+
         |            |           |            |
         v            v           v            v
     Touchscreen    USB ports   BT/Wi-Fi   Audio amp / speakers
         |
         v
   Human interaction
```

### 4.2.3 Connectivity Paths to Validate

| Interface | Typical Use Cases | Key Risks |
|-----------|-------------------|-----------|
| **Bluetooth** | pairing, HFP calls, PBAP contacts, A2DP music, AVRCP controls | reconnect failures, metadata lag |
| **Wi-Fi** | hotspot, wireless projection, OTA, map updates | handoff, throughput, captive portal issues |
| **USB** | media playback, phone projection, charging | enumeration errors, unsupported file systems |
| **Apple CarPlay** | projection, Siri, maps, calls, music | launch timing, audio focus conflicts |
| **Android Auto** | projection, Assistant, maps, notifications | permissions, connection stability |
| **Cloud/Streaming** | music streaming, online POI, voice backend | latency, poor network fallback |

### 4.2.4 Infotainment Test Layers

1. **Platform layer** — boot, service startup, logs, resource usage  
2. **Connectivity layer** — USB, BT, Wi-Fi, phone projection  
3. **Application layer** — media, navigation, phone, voice  
4. **Vehicle integration layer** — ignition, reverse, speed lockout, CAN-based states  
5. **UX layer** — touch, visual correctness, latency, audio quality

---

## 4.3 Instrument Cluster Architecture

Instrument clusters range from fully analog to fully digital systems, often with safety-critical rendering and strict timing requirements.

### 4.3.1 Cluster Types

| Cluster Type | Description | Examples | Testing Emphasis |
|--------------|-------------|----------|------------------|
| **Analog** | Physical gauges with stepper motors and discrete tell-tales | legacy speedometer/fuel/temp gauges | calibration, sweep, lamp checks |
| **Hybrid** | Analog gauges plus small TFT/MID | analog speed + digital trip display | consistency across domains |
| **Full Digital TFT** | Entire cluster rendered on display | configurable layouts, animations | graphics, performance, visual regression |
| **HUD** | Projected critical information in driver field of view | speed, nav arrows, ADAS alerts | visibility, latency, priority |

### 4.3.2 Cluster Architecture Overview

```text
+--------------------------------------------------+
|               Vehicle Sensors / ECUs             |
| Speed | RPM | Fuel | Engine | Doors | ADAS | ABS |
+-----------------------------+--------------------+
                              |
                              v
+--------------------------------------------------+
|              CAN / Ethernet Signal Inputs        |
+-----------------------------+--------------------+
                              |
                              v
+--------------------------------------------------+
|                 Cluster Control Unit             |
|  +------------------+  +----------------------+  |
|  | Signal Manager   |  | Warning Prioritizer   |  |
|  +------------------+  +----------------------+  |
|  | Gauge Logic      |  | Graphics Renderer     |  |
|  +------------------+  +----------------------+  |
|  | Diagnostics      |  | Safety Monitors       |  |
|  +------------------+  +----------------------+  |
+-----------------------------+--------------------+
                              |
                 +------------+-------------+
                 |                          |
                 v                          v
        TFT / LCD Cluster Display         HUD Output
```

### 4.3.3 Cluster Signals Commonly Tested

| Category | Example Signals |
|----------|-----------------|
| Speed / powertrain | vehicle speed, engine RPM, gear position, EV power meter |
| Fuel / energy | fuel level, SOC, range, charging state |
| Safety | seatbelt, ABS, airbag, brake, ESC, TPMS |
| Body | doors, trunk, hood, turn signals, high beam |
| ADAS | ACC status, lane assist, collision warning |
| Environment | outside temp, ice warning, low washer fluid |

### 4.3.4 Safety-Critical Concerns

- tell-tales must illuminate under correct conditions
- color usage must follow regulatory or OEM design rules
- warning priority arbitration must be correct
- cluster update latency from CAN signal to display must be bounded
- loss-of-signal behavior must be deterministic and diagnosable

---

## 4.4 Test Approach for Infotainment and Cluster

These systems usually require **multi-modal validation** rather than pure API checks.

### 4.4.1 Core Strategy

| Method | Used For | Example |
|--------|----------|---------|
| **UI automation** | menu navigation, touch interaction | open navigation app and set destination |
| **CAN validation** | cluster values, feature gating | verify speedometer after CAN speed injection |
| **Image comparison** | icons, layout, visual rendering | compare seatbelt icon against baseline |
| **Audio validation** | playback quality, mute/unmute, prompts | confirm audio prompt ducks media |
| **GPS simulation** | route and navigation testing | move simulated vehicle along path |
| **Log/service checks** | backend service stability | verify media service does not crash |
| **Performance measurement** | boot/app launch/response time | measure home screen readiness |

### 4.4.2 Practical Test Pyramid

```text
                 +----------------------+
                 | End-to-End HMI Tests |
                 | UI + CAN + Audio     |
                 +----------------------+
                 | Service / App Tests  |
                 | Media, Nav, Phone    |
                 +----------------------+
                 | Integration Checks   |
                 | Signals, APIs, HAL   |
                 +----------------------+
                 | Unit / Component      |
                 | Logic & libraries     |
                 +----------------------+
```

### 4.4.3 Example Project Structure

```text
automotive_test_project/
├── tests/
│   ├── infotainment/
│   │   ├── media_player.robot
│   │   ├── navigation.robot
│   │   ├── bluetooth_phone.robot
│   │   ├── carplay_android_auto.robot
│   │   ├── voice_assistant.robot
│   │   ├── ota_update.robot
│   │   └── performance.robot
│   └── cluster/
│       ├── gauges.robot
│       ├── telltales.robot
│       └── visual_validation.robot
├── libraries/
│   ├── HmiLibrary.py
│   ├── CanSignalLibrary.py
│   ├── DisplayVisionLibrary.py
│   ├── AudioValidationLibrary.py
│   └── GpsSimulatorLibrary.py
├── resources/
│   ├── keywords/
│   │   ├── infotainment_keywords.resource
│   │   └── cluster_keywords.resource
│   └── variables/
│       ├── devices.py
│       └── thresholds.py
└── baselines/
    ├── cluster/
    └── infotainment/
```

### 4.4.4 Cross-Domain Example Test

```robot
*** Settings ***
Library    ../libraries/HmiLibrary.py
Library    ../libraries/CanSignalLibrary.py
Library    ../libraries/DisplayVisionLibrary.py
Library    ../libraries/AudioValidationLibrary.py

*** Test Cases ***
Incoming Call Should Mute Media And Show Caller Popup
    Launch Media App
    Start Bluetooth Audio Playback
    Audio Output Level Should Be Above    -35

    Inject Phone Event    incoming_call    caller=Alice
    Wait Until Page Contains Element    incoming_call_banner    timeout=5s
    Audio Output Level Should Be Below    -55
    Screen Region Should Match Baseline
    ...    region=top_banner
    ...    baseline=baselines/infotainment/incoming_call_banner.png
```

---

## 4.5 Python Library Example: HMI and System Control

```python
# libraries/HmiLibrary.py
import time
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class HmiLibrary:
    def __init__(self):
        self.current_screen = "home"
        self._app_launch_times = {}

    @keyword("Launch App")
    def launch_app(self, app_name):
        start = time.time()
        logger.info(f"Launching app: {app_name}")
        # Replace with ADB/Appium/serial/socket control in real bench
        time.sleep(0.5)
        self.current_screen = app_name.lower()
        self._app_launch_times[app_name] = time.time() - start

    @keyword("Current Screen Should Be")
    def current_screen_should_be(self, expected):
        if self.current_screen != expected.lower():
            raise AssertionError(
                f"Expected screen '{expected}', got '{self.current_screen}'"
            )

    @keyword("Tap Coordinates")
    def tap_coordinates(self, x, y):
        logger.info(f"Tap at ({x}, {y})")

    @keyword("Swipe")
    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        logger.info(f"Swipe from ({x1},{y1}) to ({x2},{y2}) in {duration_ms}ms")

    @keyword("Get Last App Launch Time")
    def get_last_app_launch_time(self, app_name):
        if app_name not in self._app_launch_times:
            raise AssertionError(f"No launch time stored for app: {app_name}")
        return self._app_launch_times[app_name]

    @keyword("Wait For UI Idle")
    def wait_for_ui_idle(self, timeout=5.0):
        logger.info(f"Waiting for UI idle for up to {timeout}s")
        time.sleep(0.2)
```

---

## 4.6 Python Library Example: CAN Signal Validation

```python
# libraries/CanSignalLibrary.py
import time
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class CanSignalLibrary:
    def __init__(self):
        self.signals = {}
        self.last_update = {}

    @keyword("Set CAN Signal")
    def set_can_signal(self, signal_name, value):
        self.signals[signal_name] = value
        self.last_update[signal_name] = time.time()
        logger.info(f"Set CAN signal {signal_name}={value}")

    @keyword("Read CAN Signal")
    def read_can_signal(self, signal_name):
        if signal_name not in self.signals:
            raise AssertionError(f"Signal not available: {signal_name}")
        return self.signals[signal_name]

    @keyword("CAN Signal Should Equal")
    def can_signal_should_equal(self, signal_name, expected):
        actual = self.read_can_signal(signal_name)
        if str(actual) != str(expected):
            raise AssertionError(
                f"Signal {signal_name} expected {expected}, got {actual}"
            )

    @keyword("Wait For CAN Signal")
    def wait_for_can_signal(self, signal_name, expected, timeout=5.0, poll=0.1):
        end_time = time.time() + float(timeout)
        while time.time() < end_time:
            if str(self.signals.get(signal_name)) == str(expected):
                logger.info(f"Signal {signal_name} reached expected value: {expected}")
                return
            time.sleep(float(poll))
        raise AssertionError(f"Signal {signal_name} did not become {expected}")
```

---

## 4.7 Media Player Testing

Media testing includes source detection, playback continuity, metadata display, transport controls, audio routing, and focus management.

### 4.7.1 Media Sources

| Source | Example Checks |
|--------|----------------|
| **USB** | filesystem scan, supported codec, resume playback, album art |
| **Bluetooth A2DP** | start/stop, reconnect, metadata, AVRCP next/prev |
| **Streaming apps** | login persistence, buffering, network loss recovery |
| **Radio / DAB / SiriusXM** | seek, station info, preset storage |
| **Projection media** | CarPlay/Android Auto media handoff |

### 4.7.2 Typical Media Test Matrix

| Scenario | Expected Result |
|----------|-----------------|
| Insert USB with mixed media | supported files indexed, unsupported skipped gracefully |
| Start playback then ignition cycle | resume per product rule |
| Bluetooth disconnect during playback | playback stops or source fallback occurs |
| Steering wheel next-track button | track changes and metadata refreshes |
| Incoming phone call during playback | media ducks or mutes |

### 4.7.3 Robot Framework Example: USB Media Playback

```robot
*** Settings ***
Library    ../libraries/HmiLibrary.py
Library    ../libraries/DisplayVisionLibrary.py

*** Variables ***
${USB_SOURCE}       USB1
${EXPECTED_TRACK}   Midnight Highway

*** Test Cases ***
Verify USB Audio Playback And Track Metadata
    Launch App    Media
    Select Media Source    ${USB_SOURCE}
    Play Track By Name    ${EXPECTED_TRACK}
    Wait For UI Idle

    Track Title Should Be Visible    ${EXPECTED_TRACK}
    Playback State Should Be    Playing
    Album Art Region Should Match Baseline
    ...    baselines/infotainment/album_art_midnight_highway.png
```

### 4.7.4 Robot Framework Example: Bluetooth Audio + AVRCP

```robot
*** Test Cases ***
Verify Bluetooth Audio Controls
    Pair Phone Over Bluetooth    Pixel_8_Pro
    Connect A2DP Device          Pixel_8_Pro
    Start Audio On Phone         Playlist_A
    Playback State Should Be     Playing

    Press Steering Wheel Button  NEXT_TRACK
    Track Title Should Change Within    3s

    Press Steering Wheel Button  PAUSE
    Playback State Should Be     Paused
```

### 4.7.5 Reusable Resource Keywords

```robot
*** Keywords ***
Select Media Source
    [Arguments]    ${source}
    Tap Text    Sources
    Tap Text    ${source}

Play Track By Name
    [Arguments]    ${track}
    Tap Text    Browse
    Tap Text    ${track}
    Tap Text    Play

Playback State Should Be
    [Arguments]    ${expected}
    ${actual}=    Get Playback State
    Should Be Equal    ${actual}    ${expected}
```

### 4.7.6 Media Risks Often Missed

- metadata not updated after rapid track changes
- album art stale after source switch
- media continues during emergency prompt when it should duck
- USB indexing timeout with large file trees
- unsupported codec crashes parser instead of graceful skip

---

## 4.8 Navigation / Maps Testing

Navigation validation often depends on **GPS simulation**, map database state, online/offline behavior, route engine correctness, and HMI rendering.

### 4.8.1 Core Navigation Areas

| Area | What to Test |
|------|--------------|
| Route calculation | shortest/fastest route, toll avoidance, recalculation |
| Map rendering | zoom, orientation, day/night theme, lane guidance |
| Search / POI | exact, partial, fuzzy, categories |
| GPS behavior | cold start, tunnel loss, drift, jump recovery |
| Guidance output | arrows, voice prompts, ETA, distance remaining |
| Vehicle integration | cluster turn arrows, HUD guidance, speed-limit signs |

### 4.8.2 GPS Simulation Architecture

```text
+------------------+      +------------------------+
| GPS Simulator    | ---> | Infotainment Nav Stack |
| NMEA / mock API  |      | Position + route logic |
+------------------+      +-----------+------------+
                                       |
                            +----------+----------+
                            | HMI / Cluster / HUD |
                            +---------------------+
```

### 4.8.3 Python Example: GPS Simulator Library

```python
# libraries/GpsSimulatorLibrary.py
import time
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class GpsSimulatorLibrary:
    def __init__(self):
        self.position = {"lat": 0.0, "lon": 0.0}
        self.route_active = False

    @keyword("Set GPS Position")
    def set_gps_position(self, lat, lon):
        self.position = {"lat": float(lat), "lon": float(lon)}
        logger.info(f"GPS set to {self.position}")

    @keyword("Drive GPS Path")
    def drive_gps_path(self, *coordinates, interval=0.5):
        for point in coordinates:
            lat, lon = point.split(",")
            self.set_gps_position(lat, lon)
            time.sleep(float(interval))

    @keyword("Start Simulated Route")
    def start_simulated_route(self):
        self.route_active = True
        logger.info("Simulated route started")
```

### 4.8.4 Robot Framework Example: Route Calculation

```robot
*** Settings ***
Library    ../libraries/HmiLibrary.py
Library    ../libraries/GpsSimulatorLibrary.py

*** Test Cases ***
Verify Navigation Route Calculation And Guidance
    Launch App    Navigation
    Set GPS Position    48.137154    11.576124

    Search POI And Start Guidance    Airport Munich
    Route Summary Should Be Visible
    ETA Should Be Greater Than Minutes    5

    Drive GPS Path
    ...    48.137200,11.576150
    ...    48.140000,11.590000
    ...    48.150000,11.610000

    Next Maneuver Instruction Should Be Visible
    Remaining Distance Should Decrease
```

### 4.8.5 Navigation Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| GPS unavailable at startup | app shows acquiring-position state |
| Driver deviates from route | recalculation within allowed time |
| No network for online POI | offline fallback or clear message |
| Wrong-way movement | route re-evaluation and instruction update |
| Tunnel loss | dead reckoning or position hold per design |

---

## 4.9 Phone / Bluetooth Testing

Phone connectivity validation is one of the highest-value infotainment areas because it spans pairing, profiles, contacts, calls, media, and persistence.

### 4.9.1 Bluetooth Profiles Commonly Involved

| Profile | Function |
|---------|----------|
| **HFP** | Hands-free calls |
| **PBAP** | Phonebook access |
| **A2DP** | Stereo audio streaming |
| **AVRCP** | Remote control / metadata |
| **MAP** | Message access (if supported) |
| **BLE** | companion app / low-power features |

### 4.9.2 Pairing and Call Flow to Cover

```text
Phone Discovery -> Pairing Request -> PIN/Consent -> Profile Authorization
        -> PBAP Sync -> Recent Calls / Contacts Visible -> Call Audio Route
```

### 4.9.3 Robot Framework Example: Pairing + Contact Sync

```robot
*** Test Cases ***
Verify Phone Pairing And Contacts Download
    Open Bluetooth Settings
    Start Device Discovery
    Pair Phone Over Bluetooth    iPhone_15
    Pairing Should Complete Within    30s

    Grant Phonebook Permission On Phone    iPhone_15
    Wait Until Keyword Succeeds    1 min    5s    Contacts Count Should Be Above    50
    Contact Should Exist    Alice Cooper
```

### 4.9.4 Robot Framework Example: Call Management

```robot
*** Test Cases ***
Verify Incoming Call Answer And End Flow
    Ensure Phone Connected For HFP    Pixel_8_Pro
    Simulate Incoming Call On Phone   caller=Bob

    Incoming Call Popup Should Be Visible
    Caller Name Should Be Visible     Bob
    Answer Call From HMI
    Call State Should Be              Active
    Audio Route Should Be             Vehicle_Speakers

    End Call From Steering Wheel
    Call State Should Be              Idle
```

### 4.9.5 Bluetooth Reconnect Areas

- reconnect after ignition off/on
- reconnect priority when multiple known phones exist
- handling of previously denied PBAP access
- seamless switch from HFP call audio back to A2DP media
- metadata correctness after reconnect without app restart

---

## 4.10 Apple CarPlay / Android Auto Testing

Projection platforms introduce external-device dependence and multiple transport layers.

### 4.10.1 Projection Stack

```text
+-------------------------+        +----------------------------+
| Smartphone              |        | Vehicle Head Unit          |
| CarPlay / Android Auto  |<------>| USB / Wi-Fi / BT transport |
| Apps / Voice / Maps     |        | Projection renderer / HMI  |
+-------------------------+        +----------------------------+
```

### 4.10.2 Core Validation Topics

| Area | CarPlay / Android Auto Checks |
|------|-------------------------------|
| Launch | projection starts automatically on supported device |
| Permissions | location, contacts, notifications, microphone |
| Audio focus | music, call, nav prompt arbitration |
| Controls | home, back, assistant, steering wheel buttons |
| Stability | cable disconnect, weak Wi-Fi, phone app crash |
| UX | scaling, aspect ratio, touch mapping, split-screen |

### 4.10.3 Robot Example: Projection Launch

```robot
*** Test Cases ***
Verify Apple CarPlay Launch Over USB
    Connect Phone Via USB    iPhone_15
    Accept Projection Consent If Prompted
    Wait Until Page Contains Element    carplay_home    timeout=20s
    Projection Mode Should Be            CarPlay
    Audio Source Should Be               CarPlay

Verify Android Auto Wireless Reconnect
    Enable WiFi And Bluetooth On Phone    Pixel_8_Pro
    Wait Until Projection Starts          AndroidAuto    30s
    Projection Mode Should Be             AndroidAuto
```

### 4.10.4 Failure Modes to Intentionally Test

- device unlocked vs locked behavior
- first-time consent flow interrupted midway
- plugging unsupported cable/accessory
- switching from USB projection to native BT audio
- projection unavailable while vehicle in restricted state

---

## 4.11 Voice Assistant Testing

Voice features may be native, cloud-assisted, or delegated through CarPlay/Android Auto assistants.

### 4.11.1 Voice Test Dimensions

| Dimension | Example Validation |
|-----------|--------------------|
| Wake word / push-to-talk | activation reliability |
| Speech recognition | command transcription accuracy |
| Intent handling | navigation, phone, media commands |
| Audio behavior | prompt playback, barge-in, ducking |
| Connectivity | offline fallback messaging |
| Multi-language | locale and accent behavior |

### 4.11.2 Robot Framework Example: Voice Navigation Command

```robot
*** Test Cases ***
Verify Native Voice Destination Search
    Launch Voice Assistant
    Inject Microphone Audio File    audio_samples/navigate_to_airport.wav
    Recognized Transcript Should Be    Navigate to airport
    Voice Intent Should Be             navigation.search
    Search Results Should Contain      Airport
```

### 4.11.3 Voice Assistant Pitfalls

- speech recognized correctly but wrong app intent invoked
- assistant prompt overlaps media without proper ducking
- microphone muted state not shown clearly to driver
- poor network path causes indefinite spinner instead of timeout message

---

## 4.12 Cluster Display Testing

Cluster display validation is mostly about **signal-to-visual correctness**, timing, formatting, and state transitions.

### 4.12.1 Gauge and Display Areas

| Element | Validation Examples |
|---------|---------------------|
| Speedometer | zero offset, scaling, update latency, units |
| Tachometer | RPM mapping, redline behavior, smoothing |
| Fuel gauge | step behavior, low fuel threshold, reserve icon |
| Temperature gauge | nominal band, overheat warning |
| Gear indicator | P/R/N/D/S state transitions |
| Odometer / trip | persistence and formatting |

### 4.12.2 Signal-to-Display Test Flow

```text
Inject CAN Signal -> Cluster logic updates internal state -> Renderer updates gauge/icon
                 -> Capture display -> OCR / image compare / HMI query -> Assert result
```

### 4.12.3 Robot Framework Example: Speedometer via CAN

```robot
*** Settings ***
Library    ../libraries/CanSignalLibrary.py
Library    ../libraries/DisplayVisionLibrary.py

*** Test Cases ***
Verify Speedometer Display Tracks CAN Speed
    Set CAN Signal    VEH_SPEED_KPH    0
    Speedometer Value Should Be    0

    Set CAN Signal    VEH_SPEED_KPH    30
    Wait Until Keyword Succeeds    5s    200ms    Speedometer Value Should Be    30

    Set CAN Signal    VEH_SPEED_KPH    120
    Wait Until Keyword Succeeds    5s    200ms    Speedometer Value Should Be    120
```

### 4.12.4 Robot Framework Example: Fuel Warning

```robot
*** Test Cases ***
Verify Low Fuel Telltale Activation
    Set CAN Signal    FUEL_LEVEL_PERCENT    18
    Low Fuel Warning Should Be Hidden

    Set CAN Signal    FUEL_LEVEL_PERCENT    9
    Wait Until Keyword Succeeds    3s    200ms    Low Fuel Warning Should Be Visible
    Warning Color Should Be    amber
```

### 4.12.5 Boundary Cases

- signal missing / timeout state
- invalid signal range from network fault
- unit switch mph/kph during driving
- display suppression during startup self-test
- warning icon present but text popup suppressed due to priority logic

---

## 4.13 Cluster Tell-tale / Warning Light Testing

Tell-tale testing requires both **condition validation** and **priority validation**.

### 4.13.1 Common Tell-tales

| Tell-tale | Color | Typical Trigger |
|-----------|-------|-----------------|
| Seatbelt | red | driver belt unlatched |
| Check engine / MIL | amber | emission-related fault |
| ABS | amber | ABS fault active |
| Brake | red | parking brake / brake failure |
| Airbag | red | SRS fault |
| Battery | red | charging system fault |
| TPMS | amber | tire pressure low |
| High beam | blue | high beam on |
| Turn indicators | green | left/right turn active |
| Coolant temp | red | overheat |

### 4.13.2 Warning Priority Model Example

| Priority | Example | Expected UX |
|----------|---------|-------------|
| **P1** | brake failure, engine overheat | immediate prominent display, chime |
| **P2** | low fuel, TPMS, washer low | visible icon and message |
| **P3** | information reminders | passive display only |

### 4.13.3 Warning Arbitration Diagram

```text
Input Conditions --> Warning Manager --> Priority Sort --> Display Decision
     |                   |                   |                  |
 seatbelt open        active list         P1 > P2 > P3      icon/text/chime
 low fuel
 ABS fault
```

### 4.13.4 Robot Framework Example: Multiple Warning Priorities

```robot
*** Test Cases ***
Verify Higher Priority Warning Dominates Center Message Area
    Set CAN Signal    LOW_FUEL_ACTIVE       1
    Set CAN Signal    SEATBELT_UNLATCHED    1

    Warning Icon Should Be Visible          LOW_FUEL
    Warning Icon Should Be Visible          SEATBELT
    Center Warning Message Should Be        Fasten seat belt
    Active Warning Priority Should Be       P1
```

### 4.13.5 Example Coverage Checklist

- lamp on/off logic for every tell-tale
- color correctness
- blinking frequency where applicable
- startup bulb check behavior
- interaction with chimes and popup messages
- simultaneous warnings and priority handling
- warning clear conditions and hysteresis

---

## 4.14 Image / Visual Comparison Testing

Visual checks are essential when the actual system under test is a display.

### 4.14.1 When to Use Visual Comparison

| Use Case | Why Visual Comparison Helps |
|----------|-----------------------------|
| icon appearance | exact shape/color matter |
| layout validation | positions and overlap matter |
| theme checks | night/day contrast, brightness palettes |
| animation checkpoints | key frames or end states |
| HUD / cluster arrows | rendered shape is the requirement |

### 4.14.2 OpenCV-Based Python Library Example

```python
# libraries/DisplayVisionLibrary.py
import cv2
from robot.api.deco import keyword, library


@library(scope='SUITE')
class DisplayVisionLibrary:
    @keyword("Images Should Match Above Threshold")
    def images_should_match_above_threshold(self, actual_path, baseline_path, threshold=0.95):
        actual = cv2.imread(actual_path)
        baseline = cv2.imread(baseline_path)
        if actual is None or baseline is None:
            raise AssertionError("Could not read one or both images")

        if actual.shape != baseline.shape:
            raise AssertionError(
                f"Image shape mismatch: {actual.shape} vs {baseline.shape}"
            )

        result = cv2.matchTemplate(actual, baseline, cv2.TM_CCOEFF_NORMED)
        score = float(result.max())
        if score < float(threshold):
            raise AssertionError(
                f"Image similarity below threshold: {score:.4f} < {threshold}"
            )
        return score
```

### 4.14.3 Robot Framework Example: Cluster Icon Comparison

```robot
*** Test Cases ***
Verify Seatbelt Icon Rendering
    Capture Screen Region    seatbelt_icon    output/seatbelt_icon.png
    ${score}=    Images Should Match Above Threshold
    ...    output/seatbelt_icon.png
    ...    baselines/cluster/seatbelt_icon.png
    ...    threshold=0.97
    Log    Seatbelt icon match score: ${score}
```

### 4.14.4 Sikuli-Based Example Concept

```robot
*** Settings ***
Library    SikuliLibrary

*** Test Cases ***
Verify Navigation Home Button Visible
    Add Image Path    baselines/infotainment
    Wait Until Screen Contain    nav_home_button.png    10
    Click    nav_home_button.png
```

### 4.14.5 Best Practices for Visual Testing

- use fixed capture resolution and brightness when possible
- mask dynamic regions such as clocks and signal strength
- define different thresholds for exact icons vs full-screen scenes
- store baselines by variant, locale, theme, and display resolution
- prefer region-based comparison over full-screen comparison for robustness

---

## 4.15 Touch / HMI Interaction Testing

Touch-heavy infotainment systems require robust gesture testing.

### 4.15.1 HMI Actions Commonly Automated

| Action | Example |
|--------|---------|
| Tap | open app, press control |
| Long press | context menu, drag initiate |
| Swipe | page scroll, carousel, map pan |
| Pinch/zoom | map zoom |
| Drag | reorder favorites, slider control |
| Multi-step gesture | projection app switch, split pane resize |

### 4.15.2 Robot Framework Example: Gesture Validation

```robot
*** Test Cases ***
Verify Map Can Be Zoomed And Panned
    Launch App    Navigation
    Perform Pinch Out On Region    map_canvas
    Map Zoom Level Should Increase

    Swipe On Region    map_canvas    start=80,50    end=20,50
    Map Center Should Change
```

### 4.15.3 Python Gesture Helper Example

```python
# libraries/TouchLibrary.py
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='TEST')
class TouchLibrary:
    @keyword("Perform Gesture")
    def perform_gesture(self, gesture_name, region=None, **kwargs):
        logger.info(f"Gesture={gesture_name}, region={region}, args={kwargs}")

    @keyword("Swipe On Region")
    def swipe_on_region(self, region, start, end, duration_ms=300):
        logger.info(
            f"Swipe on {region}: start={start}, end={end}, duration={duration_ms}ms"
        )
```

### 4.15.4 HMI Automation Challenges

- soft keyboard overlays interfere with target elements
- animations cause tap-too-early issues
- hitboxes differ by display scaling or localization
- touch rejected while vehicle state changes or safety overlay active

---

## 4.16 Audio Testing

Audio validation is often ignored because it is harder to automate, but it is crucial for IVI quality.

### 4.16.1 Audio Test Areas

| Area | Example Checks |
|------|----------------|
| Playback presence | audio is actually output |
| Routing | speakers vs phone vs Bluetooth device |
| Ducking | nav prompt reduces music volume |
| Volume scaling | user volume steps correspond to expected dB range |
| Balance/fade | output distribution matches setting |
| Prompt mixing | chimes and TTS coexist correctly |

### 4.16.2 Python Audio Validation Example

```python
# libraries/AudioValidationLibrary.py
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='SUITE')
class AudioValidationLibrary:
    def __init__(self):
        self.last_level_db = -40.0
        self.current_route = "Vehicle_Speakers"

    @keyword("Audio Output Level Should Be Above")
    def audio_output_level_should_be_above(self, threshold_db):
        if float(self.last_level_db) <= float(threshold_db):
            raise AssertionError(
                f"Audio level {self.last_level_db} dB not above {threshold_db} dB"
            )
        logger.info(f"Audio level OK: {self.last_level_db} dB")

    @keyword("Audio Route Should Be")
    def audio_route_should_be(self, expected_route):
        if self.current_route != expected_route:
            raise AssertionError(
                f"Expected route {expected_route}, got {self.current_route}"
            )
```

### 4.16.3 Combined Media + Nav Prompt Example

```robot
*** Test Cases ***
Verify Navigation Prompt Ducks Media
    Start Audio Playback On Source    Bluetooth
    Audio Output Level Should Be Above    -35

    Trigger Navigation Prompt    Turn left in 100 meters
    Media Ducking Should Occur Within     1s
    Prompt Audio Should Be Audible
```

---

## 4.17 OTA Update Testing for Infotainment

Infotainment ECUs commonly receive feature updates, map packages, security patches, and app updates over the air.

### 4.17.1 OTA Flow

```text
Update Check -> Download -> Integrity Verification -> User Consent / Scheduling
            -> Install -> Reboot -> Post-Install Health Checks -> Rollback if Needed
```

### 4.17.2 OTA Validation Matrix

| Stage | Checks |
|-------|--------|
| Discovery | update visible only for applicable variant/version |
| Download | pause/resume, poor network behavior, checksum |
| Install | power-state restrictions, progress UI, timeout handling |
| Reboot | correct reboot path, no boot loops |
| Post-check | version change, settings retained, apps functional |
| Recovery | rollback or safe failure on corrupted package |

### 4.17.3 Robot Framework Example: OTA Smoke

```robot
*** Test Cases ***
Verify Infotainment OTA Update Success Path
    Connect To Test WiFi
    Trigger OTA Manifest Check
    Update Should Be Available    version=2026.08.1

    Start OTA Download
    Wait Until OTA State Is    Downloaded    timeout=20 min
    Schedule OTA Installation Now

    Wait For Reboot Completion    timeout=10 min
    Infotainment Version Should Be    2026.08.1
    Launch App    Media
    Current Screen Should Be    media
```

### 4.17.4 Negative OTA Scenarios

- network drop at 90% download
- insufficient storage
- battery/ignition state not meeting install criteria
- corrupted package signature
- user cancellation during deferred install window

---

## 4.18 Performance Testing

Performance matters greatly because drivers notice boot delays, laggy maps, and touch latency immediately.

### 4.18.1 Metrics to Capture

| Metric | Example Requirement |
|--------|---------------------|
| Cold boot to home screen | < 20 s |
| Reverse camera availability | < 2 s after reverse engaged |
| Media app launch | < 3 s |
| Nav route calculation | < 5 s for standard route |
| Touch response latency | < 150 ms |
| Cluster signal-to-display latency | < 200 ms |

### 4.18.2 Robot Framework Example: App Launch Timing

```robot
*** Test Cases ***
Verify Media App Launch Time
    Launch App    Media
    ${launch_time}=    Get Last App Launch Time    Media
    Should Be True    ${launch_time} < 3.0
```

### 4.18.3 Robot Framework Example: Cluster Latency

```robot
*** Test Cases ***
Verify Speed Signal To Display Latency
    ${t0}=    Get Time    epoch
    Set CAN Signal    VEH_SPEED_KPH    80
    Wait Until Keyword Succeeds    2s    50ms    Speedometer Value Should Be    80
    ${t1}=    Get Time    epoch
    ${latency}=    Evaluate    ${t1} - ${t0}
    Should Be True    ${latency} < 0.2
```

### 4.18.4 Performance Test Advice

- measure on controlled hardware and thermal conditions
- separate cold boot, warm boot, and resume-from-sleep
- capture percentile values, not just one sample
- correlate failures with logs, CPU/memory, and service restarts

---

## 4.19 Integrated End-to-End Example Suite

```robot
*** Settings ***
Library    ../libraries/HmiLibrary.py
Library    ../libraries/CanSignalLibrary.py
Library    ../libraries/GpsSimulatorLibrary.py
Library    ../libraries/DisplayVisionLibrary.py
Library    ../libraries/AudioValidationLibrary.py
Suite Setup       Prepare Infotainment Bench
Suite Teardown    Cleanup Bench

*** Test Cases ***
Navigation Prompt Should Appear In Cluster During Active Route
    Launch App    Navigation
    Set GPS Position    52.5200    13.4050
    Search POI And Start Guidance    Central Station

    Drive GPS Path
    ...    52.5201,13.4053
    ...    52.5205,13.4060
    ...    52.5210,13.4070

    Cluster Turn Arrow Should Be Visible
    Cluster Distance To Turn Should Decrease
    Prompt Audio Should Be Audible

Speed Lockout Should Disable Video Playback UI
    Set CAN Signal    VEH_SPEED_KPH    0
    Launch App    Video
    Video Playback Control Should Be Enabled

    Set CAN Signal    VEH_SPEED_KPH    10
    Wait Until Keyword Succeeds    3s    200ms    Video Playback Control Should Be Disabled
    Safety Lockout Message Should Be Visible
```

---

## 4.20 Design Patterns for Stable Automotive HMI Tests

### 4.20.1 Keyword Layering

| Layer | Example |
|-------|---------|
| Test case | `Verify Incoming Call Answer And End Flow` |
| Business keyword | `Answer Call From HMI` |
| Technical keyword | `Tap Coordinates` / `Send CAN Signal` |
| Library implementation | Python methods using hardware or APIs |

### 4.20.2 Recommended Stability Practices

- use **state-based waits** instead of fixed sleeps
- keep **bench abstractions** separate from tests
- synchronize HMI assertions with backend signals where possible
- tag tests by **source** (`bt`, `usb`, `cluster`, `performance`, `ota`)
- baseline screenshots per variant, language, and screen size
- log CAN, HMI state, screenshots, and audio traces for each failure

### 4.20.3 Example Tags

```robot
*** Test Cases ***
Verify Seatbelt Warning Popup
    [Tags]    cluster    telltale    can    safety    priority-high
    Set CAN Signal    SEATBELT_UNLATCHED    1
    Seatbelt Warning Should Be Visible
```

---

## 4.21 Common Challenges and Mitigations

| Challenge | Why It Happens | Mitigation |
|-----------|----------------|------------|
| Flaky image comparison | brightness/theme drift | crop regions, mask dynamic content |
| Bluetooth instability | RF environment, phone OS variance | standardize phone setup, retry policy |
| Projection startup delay | permission dialogs, phone state | automate consent path, precondition checks |
| GPS inconsistency | simulator timing mismatch | deterministic route playback, timestamps |
| Cluster rendering lag | animation smoothing | define acceptable latency window |
| Touch miss | animation or bad coordinates | element anchors, wait for idle |

---

## 4.22 Exercises

### Exercise 1: USB Media Validation Suite
Create a Robot Framework suite that:
- detects a USB source
- starts playback of a selected MP3 file
- validates track title and artist
- verifies pause/resume controls
- captures album art and compares it with a baseline

**Stretch goal:** add unsupported-file validation.

### Exercise 2: Bluetooth Pairing Regression
Build tests for:
- first-time pairing
- reconnect after ignition cycle
- PBAP sync completion
- A2DP playback start
- steering wheel next-track control

**Stretch goal:** validate behavior with two paired phones.

### Exercise 3: Navigation with GPS Simulation
Implement a suite that:
- sets an initial GPS position
- searches for a POI
- starts guidance
- drives a simulated path
- verifies remaining distance decreases and next maneuver updates

**Stretch goal:** add route recalculation after forced deviation.

### Exercise 4: Cluster Gauge Validation
Write tests that inject CAN signals for:
- speed: 0, 30, 60, 120 km/h
- RPM: idle, 2000, 4000
- fuel: 100%, 50%, 10%, 5%

Verify gauge values and low-fuel tell-tale activation.

### Exercise 5: Warning Priority Arbitration
Create tests that activate multiple warnings together:
- low fuel + seatbelt
- ABS fault + door open
- engine overheat + low washer fluid

Verify icon presence, center message selection, and priority ordering.

### Exercise 6: Visual Regression Baseline Strategy
Define a baseline management plan covering:
- variant-specific cluster themes
- day/night modes
- multiple resolutions
- localization-sensitive text areas
- masked dynamic regions

### Exercise 7: OTA Update Smoke Path
Develop a smoke suite that:
- checks for update availability
- downloads the package
- verifies post-reboot version
- launches media and navigation to confirm sanity

**Stretch goal:** simulate download interruption and retry.

### Exercise 8: Performance Benchmarking
Measure and report:
- infotainment cold boot time
- media app launch time
- navigation route calculation time
- speed signal to cluster latency

Store the metrics in Robot logs and fail if thresholds are exceeded.

---

## 4.23 Summary

In this part, you learned how Robot Framework can be used for **infotainment and instrument cluster testing** by combining HMI automation, CAN validation, GPS simulation, audio checks, and visual comparison. These domains require layered automation that understands both **embedded system architecture** and **user-visible behavior**. With reusable Python libraries and robust Robot keywords, you can validate media, phone, navigation, projection, cluster gauges, tell-tales, OTA flows, and performance with production-style test design.

---

## 4.24 What Comes Next

Continue to **[Part 5](ROBOT_FRAMEWORK_AUTOMOTIVE_PART5.md)** for more advanced automotive automation topics in the series.

[← Previous: Part 3](ROBOT_FRAMEWORK_AUTOMOTIVE_PART3.md) | [Next: Part 5 →](ROBOT_FRAMEWORK_AUTOMOTIVE_PART5.md)
