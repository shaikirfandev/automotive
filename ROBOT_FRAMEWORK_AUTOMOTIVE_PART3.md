# Part 3: ADAS Testing with Robot Framework (Intermediate–Advanced)

[← Previous: ROBOT_FRAMEWORK_AUTOMOTIVE_PART2.md](ROBOT_FRAMEWORK_AUTOMOTIVE_PART2.md) | [Next: ROBOT_FRAMEWORK_AUTOMOTIVE_PART4.md →](ROBOT_FRAMEWORK_AUTOMOTIVE_PART4.md)

---

## 3.1 ADAS Overview

Advanced Driver Assistance Systems (ADAS) combine sensing, perception, decision logic, and actuation supervision to reduce collision risk and improve driving comfort. In Robot Framework, ADAS testing typically verifies **ECU behavior**, **vehicle-level responses**, **timing**, **diagnostics**, and **safety requirements** across simulation, HIL, SIL, and vehicle-test environments.

### Core ADAS Functions

| Function | Full Name | Primary Goal | Typical Inputs | Typical Outputs | Key Risks |
|---|---|---|---|---|---|
| AEB | Autonomous Emergency Braking | Avoid or mitigate frontal collision | Radar, camera, ego speed, object classification | FCW, brake request, decel command | Late braking, false positives |
| LDW | Lane Departure Warning | Warn when unintentionally leaving lane | Camera lane model, steering angle, turn signal | Audible/visual warning | Missed departures |
| LKA | Lane Keep Assist | Provide steering support to stay in lane | Camera lane model, vehicle dynamics | Steering torque command | Overcorrection, oscillation |
| ACC | Adaptive Cruise Control | Maintain set speed and gap | Radar tracks, camera confirmation, ego dynamics | Longitudinal accel/brake | Harsh accel, unsafe gap |
| BSM | Blind Spot Monitoring | Warn about vehicle in blind zone | Radar side tracks, speed, turn signal | Lamp, warning escalation | Missed side target |
| TSR | Traffic Sign Recognition | Recognize signs like speed limits | Camera image, map/context | Detected sign, confidence | Misread sign |
| Parking Assist | Low-speed maneuver support | Ultrasonic, surround view, steering model | Steering/brake/stop prompts | Missed obstacle |
| Surround View | Bird's-eye composite vision | Camera stitching and rendering | 4+ cameras, calibration data | Composite view, overlays | Distortion, latency |

### ADAS Functional Stack

```text
+--------------------------------------------------------------+
|                     HMI / Driver Feedback                    |
|  warnings, icons, chimes, set-speed display, takeover alerts |
+--------------------------------------------------------------+
|                  Decision and Control Layer                  |
| AEB logic | ACC logic | lane logic | BSM logic | TSR outputs |
+--------------------------------------------------------------+
|               Perception / Fusion / Tracking                 |
| object detection | lane model | target tracking | sign class |
+--------------------------------------------------------------+
|                    Sensor and Vehicle Inputs                 |
| radar | camera | lidar | ultrasonic | IMU | wheels | steering|
+--------------------------------------------------------------+
|               Plant / Environment / Road Model              |
| roads | traffic | pedestrians | weather | reflectivity       |
+--------------------------------------------------------------+
```

### Typical ADAS Verification Objectives

1. Confirm the system **detects the correct target**.
2. Confirm the system **acts within timing limits**.
3. Confirm warnings/interventions occur only in **valid operating domains**.
4. Confirm safe degradation under **sensor faults or uncertainty**.
5. Confirm traceability to **ISO 26262 safety goals and technical requirements**.

---

## 3.2 ADAS Test Architecture

ADAS validation is rarely a single-tool activity. A practical architecture connects Robot Framework to scenario controllers, sensor simulators, HIL I/O, plant models, trace recorders, and result analytics.

### End-to-End Test Architecture

```text
+--------------------------- Robot Framework ---------------------------+
| Test suites | keywords | data-driven scenarios | requirement tags     |
+-------------------------------+--------------------------------------+
                                |
                                v
+------------------- Test Orchestration / Python Libraries ------------+
| Scenario loader | ECU control | CAN/LIN/Ethernet | fault injector    |
| KPI collector   | trace parser | camera/radar stim | report adapter   |
+-------------------------------+--------------------------------------+
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
+-----------------------+                   +---------------------------+
|   Sensor Simulation   |                   |        HIL Bench          |
| Radar targets         |                   | ADAS ECU                  |
| Camera scene replay   |                   | brake/steer interfaces    |
| Lidar point clouds    |                   | gateway / network         |
| Ultrasonic echoes     |                   | real-time I/O             |
+-----------+-----------+                   +-------------+-------------+
            |                                                 |
            v                                                 v
+-----------------------+                   +---------------------------+
|    Plant / Vehicle    |<----------------->| Measured outputs / traces |
| ego vehicle dynamics  |                   | actuation, states, DTCs   |
| road geometry         |                   | logs, timestamps, KPIs    |
| actors, weather       |                   +---------------------------+
+-----------------------+
```

### Sensor Simulation Roles

| Sensor | What is simulated | Common parameters | Why it matters |
|---|---|---|---|
| Radar | Range, velocity, RCS, angle | target distance, relative speed, reflectivity | Critical for AEB/ACC/BSM |
| Camera | Frames or rendered scenes | lane marks, lighting, signs, occlusion | Critical for LDW/LKA/TSR |
| Lidar | Point cloud / object returns | density, range, reflectivity, dropouts | Cross-check for object presence |
| Ultrasonic | Echo timing, close-range obstacles | near-field distance, angle, multipath | Parking and low-speed safety |

### HIL Setup Layers

| Layer | Example signals | Example tools/components |
|---|---|---|
| Vehicle network | wheel speed, yaw rate, brake pressure | CAN, CAN FD, Automotive Ethernet |
| Sensor stimulus | radar tracks, camera video, lidar frames | simulator, sensor playback engine |
| ECU control | ignition, drive mode, calibration set | power supply, automation API |
| Measurement | reaction time, object ID, lane quality | logger, trace recorder, KPI scripts |
| Fault insertion | frame freeze, bias, signal timeout | fault manager, network manipulator |

### Robot Framework Suite Structure

```robot
*** Settings ***
Documentation    ADAS HIL smoke architecture example
Library          libraries/AdasBenchLibrary.py    bench_id=HIL_A01
Library          libraries/SensorFusionLibrary.py
Library          Collections
Suite Setup      Initialize ADAS Bench
Suite Teardown   Shutdown ADAS Bench
Test Setup       Start Measurement Session
Test Teardown    Stop Measurement Session

*** Variables ***
${SCENARIO_DIR}      ${CURDIR}/scenarios
${REACTION_LIMIT}    1.20

*** Keywords ***
Initialize ADAS Bench
    Power On ECU
    Connect Vehicle Networks
    Reset All Fault Injectors
    Set Default Vehicle State

Start Measurement Session
    Start Trace Capture
    Clear KPI Buffer

Stop Measurement Session
    Stop Trace Capture
    Export Measurement Artifacts
```

### Example Python Library for ADAS Bench Control

```python
# libraries/AdasBenchLibrary.py
from robot.api.deco import keyword, library
from robot.api import logger
import time


@library(scope='SUITE')
class AdasBenchLibrary:
    def __init__(self, bench_id="HIL_A01"):
        self.bench_id = bench_id
        self.powered = False
        self.measurement_active = False
        self.state = {
            "vehicle_speed_kph": 0.0,
            "gear": "P",
            "faults": []
        }

    @keyword("Power On ECU")
    def power_on_ecu(self):
        self.powered = True
        logger.info(f"ECU on bench {self.bench_id} powered on")

    @keyword("Shutdown ADAS Bench")
    def shutdown_adas_bench(self):
        self.measurement_active = False
        self.powered = False
        logger.info(f"Bench {self.bench_id} shut down")

    @keyword("Connect Vehicle Networks")
    def connect_vehicle_networks(self):
        if not self.powered:
            raise AssertionError("Bench must be powered before connecting networks")
        logger.info("CAN/Ethernet networks connected")

    @keyword("Reset All Fault Injectors")
    def reset_all_fault_injectors(self):
        self.state["faults"].clear()
        logger.info("All faults cleared")

    @keyword("Set Default Vehicle State")
    def set_default_vehicle_state(self):
        self.state["vehicle_speed_kph"] = 0.0
        self.state["gear"] = "D"
        logger.info("Vehicle state reset to defaults")

    @keyword("Start Trace Capture")
    def start_trace_capture(self):
        self.measurement_active = True
        logger.info("Trace capture started")

    @keyword("Stop Trace Capture")
    def stop_trace_capture(self):
        self.measurement_active = False
        logger.info("Trace capture stopped")

    @keyword("Clear KPI Buffer")
    def clear_kpi_buffer(self):
        logger.info("KPI buffer cleared")

    @keyword("Export Measurement Artifacts")
    def export_measurement_artifacts(self):
        logger.info("Artifacts exported: bus logs, trace, KPIs")

    @keyword("Set Ego Speed")
    def set_ego_speed(self, speed_kph):
        self.state["vehicle_speed_kph"] = float(speed_kph)
        logger.info(f"Ego speed set to {speed_kph} kph")

    @keyword("Wait Seconds")
    def wait_seconds(self, seconds):
        time.sleep(float(seconds))
```

---

## 3.3 AEB Complete Test Suite

AEB must identify imminent forward collisions and command timely warnings and braking. Test strategy should cover **stationary**, **moving**, and **crossing** targets, classification confidence, false positives, and degraded sensing.

### Representative AEB Scenario Matrix

| Scenario ID | Target Type | Ego Speed | Target Motion | Expected Behavior |
|---|---|---:|---|---|
| AEB-VEH-001 | Stopped vehicle | 50 kph | stationary | FCW then autonomous braking |
| AEB-VEH-002 | Slower lead vehicle | 80 kph | -30 kph relative | Controlled decel, no collision |
| AEB-PED-001 | Adult pedestrian crossing | 35 kph | lateral crossing | Brake intervention before impact |
| AEB-PED-002 | Pedestrian emerges from occlusion | 25 kph | crossing | Warning and mitigation if unavoidable |
| AEB-CYC-001 | Cyclist in lane | 45 kph | same direction | Detect cyclist and brake if TTC low |
| AEB-CYC-002 | Cyclist cut-in | 55 kph | lateral cut-in | Brake if cut-in violates safety margin |

### AEB Logic Timing View

```text
Object detected ---> TTC computed ---> Warning threshold ---> Brake threshold ---> Decel ramps ---> Stop / mitigate
       |                 |                    |                    |                  |
       |                 |                    |                    |                  +--> verify decel profile
       |                 |                    |                    +--> verify brake request timestamp
       |                 |                    +--> verify FCW/HMI output
       |                 +--> verify correct target selection
       +--> verify detection confidence and classification
```

### Robot Framework AEB Suite

```robot
*** Settings ***
Documentation    AEB regression suite for pedestrian, cyclist, and vehicle scenarios
Library          libraries/AdasBenchLibrary.py
Library          libraries/AebScenarioLibrary.py
Library          Collections
Test Setup       Prepare AEB Scenario
Test Teardown    Finalize AEB Scenario

*** Variables ***
${MAX_REACTION_TIME_S}         1.00
${MIN_DECEL_MPS2}              3.50
${NO_COLLISION_ALLOWED}        ${TRUE}

*** Keywords ***
Prepare AEB Scenario
    Reset AEB KPIs
    Ensure AEB Enabled
    Clear All DTCs

Finalize AEB Scenario
    Store AEB Metrics
    Verify No Unexpected Faults

Run And Verify AEB Scenario
    [Arguments]    ${scenario_name}    ${reaction_limit}=${MAX_REACTION_TIME_S}
    Load AEB Scenario    ${scenario_name}
    Start Scenario Replay
    Wait Until Scenario Complete    timeout=20s
    ${metrics}=    Get AEB Metrics
    Log    ${metrics}
    Should Be True    ${metrics}[collision_avoided] == ${NO_COLLISION_ALLOWED}
    Should Be True    ${metrics}[reaction_time_s] <= ${reaction_limit}
    Should Be True    ${metrics}[peak_decel_mps2] >= ${MIN_DECEL_MPS2}
```

### AEB Test Cases

```robot
*** Test Cases ***
AEB Should Brake For Stopped Vehicle At Urban Speed
    [Documentation]    Ego approaches stationary vehicle at 50 kph.
    [Tags]    AEB    vehicle    regression    ASIL-C
    Set Ego Speed    50
    Configure Target Vehicle    distance_m=45    relative_speed_kph=0    lane=ego
    Run And Verify AEB Scenario    aeb_stopped_vehicle_50kph

AEB Should Mitigate Pedestrian Crossing From Right
    [Documentation]    Pedestrian enters lane with critical TTC.
    [Tags]    AEB    pedestrian    safety    ASIL-D
    Set Ego Speed    35
    Configure Pedestrian Target    side=right    crossing_speed_kph=6    trigger_distance_m=22
    Run And Verify AEB Scenario    aeb_pedestrian_crossing_right    reaction_limit=0.85

AEB Should Detect Cyclist Moving In Same Lane
    [Documentation]    Cyclist ahead in ego lane at lower speed.
    [Tags]    AEB    cyclist    fusion    ASIL-C
    Set Ego Speed    45
    Configure Cyclist Target    distance_m=35    speed_kph=15    lane=ego
    Run And Verify AEB Scenario    aeb_cyclist_same_lane

AEB Should Not Trigger For Overhead Sign Structure
    [Documentation]    Prevent false positive on non-collision object above road.
    [Tags]    AEB    false-positive    non-regression
    Load AEB Scenario    aeb_overhead_sign_non_target
    Start Scenario Replay
    Wait Until Scenario Complete    timeout=15s
    ${metrics}=    Get AEB Metrics
    Should Be Equal As Integers    ${metrics}[brake_events]    0
    Should Be Equal As Integers    ${metrics}[fcw_events]      0
```

### Python Library for AEB Metrics

```python
# libraries/AebScenarioLibrary.py
from robot.api.deco import keyword, library
from robot.api import logger


@library(scope='TEST')
class AebScenarioLibrary:
    def __init__(self):
        self.current = None
        self.metrics = {}

    @keyword("Reset AEB KPIs")
    def reset_aeb_kpis(self):
        self.metrics = {
            "collision_avoided": True,
            "reaction_time_s": 0.78,
            "peak_decel_mps2": 5.1,
            "brake_events": 1,
            "fcw_events": 1,
        }

    @keyword("Ensure AEB Enabled")
    def ensure_aeb_enabled(self):
        logger.info("AEB enabled and ready")

    @keyword("Clear All DTCs")
    def clear_all_dtcs(self):
        logger.info("DTCs cleared")

    @keyword("Load AEB Scenario")
    def load_aeb_scenario(self, scenario_name):
        self.current = scenario_name
        logger.info(f"Scenario loaded: {scenario_name}")

    @keyword("Start Scenario Replay")
    def start_scenario_replay(self):
        logger.info(f"Scenario replay started for {self.current}")

    @keyword("Wait Until Scenario Complete")
    def wait_until_scenario_complete(self, timeout="20s"):
        logger.info(f"Scenario complete within {timeout}")

    @keyword("Configure Target Vehicle")
    def configure_target_vehicle(self, **kwargs):
        logger.info(f"Vehicle target config: {kwargs}")

    @keyword("Configure Pedestrian Target")
    def configure_pedestrian_target(self, **kwargs):
        logger.info(f"Pedestrian target config: {kwargs}")

    @keyword("Configure Cyclist Target")
    def configure_cyclist_target(self, **kwargs):
        logger.info(f"Cyclist target config: {kwargs}")

    @keyword("Get AEB Metrics")
    def get_aeb_metrics(self):
        if self.current == "aeb_overhead_sign_non_target":
            return {
                "collision_avoided": True,
                "reaction_time_s": 999,
                "peak_decel_mps2": 0.0,
                "brake_events": 0,
                "fcw_events": 0,
            }
        return self.metrics

    @keyword("Store AEB Metrics")
    def store_aeb_metrics(self):
        logger.info(f"Stored AEB metrics for {self.current}")

    @keyword("Verify No Unexpected Faults")
    def verify_no_unexpected_faults(self):
        logger.info("No unexpected AEB faults found")
```

### AEB Edge Conditions to Add

- low-friction road with increased stopping distance
- stationary vehicle after curve exit
- partial overlap target
- night scenario with low camera confidence
- radar ghost target rejection
- AEB inhibit when driver aggressively steers around obstacle

---

## 3.4 LDW and LKA Testing

LDW focuses on **warning**, while LKA adds **lateral correction**. Testing must account for lane marking quality, curvature, speed gates, turn signal state, hands-on detection, and road edge interpretation.

### LDW/LKA Variables of Interest

| Parameter | Example Values | Why it matters |
|---|---|---|
| Lane marking type | solid, dashed, worn, yellow, temporary | Perception robustness |
| Curvature radius | 250 m, 500 m, 1200 m | Affects preview and controller gain |
| Speed threshold | 55 kph, 65 kph | LDW/LKA often disabled below threshold |
| Driver turn signal | on/off | Intentional lane change suppression |
| Road edge | guardrail, shoulder, curb | Avoid false lane assumptions |
| Camera confidence | high/medium/low | Warning strategy or graceful degradation |

### Lane-Centric Test Model

```text
          left lane             ego lane                right lane
   ---------------------------------------------------------------
   dashed line         ego vehicle path         solid line / edge
            \            ^
             \           |
              \---- lane departure trajectory ---->

Checks:
1. Was lane crossing detected?
2. Was warning suppressed if indicator active?
3. Did assist torque remain within limit?
4. Did vehicle settle without oscillation?
```

### Robot Framework LDW/LKA Suite

```robot
*** Settings ***
Documentation    LDW and LKA functional verification
Library          libraries/LaneAssistLibrary.py
Library          Collections

*** Keywords ***
Run Lane Scenario And Collect
    [Arguments]    ${scenario}
    Load Lane Scenario    ${scenario}
    Start Lane Scenario
    Wait For Lane Scenario Completion    20s
    ${result}=    Get Lane Assist Result
    RETURN    ${result}
```

```robot
*** Test Cases ***
LDW Should Warn On Unsignaled Departure Over Dashed Line
    [Tags]    LDW    lane    ASIL-B
    Set Ego Speed    72
    Set Turn Signal State    off
    Set Lane Marking Quality    left=good    right=good
    ${result}=    Run Lane Scenario And Collect    ldw_dashed_departure
    Should Be True    ${result}[warning_issued]
    Should Be True    ${result}[time_to_line_crossing_s] < 1.5

LDW Should Not Warn During Intended Lane Change
    [Tags]    LDW    suppression    regression
    Set Ego Speed    80
    Set Turn Signal State    left
    ${result}=    Run Lane Scenario And Collect    ldw_intended_lane_change
    Should Be False    ${result}[warning_issued]

LKA Should Apply Corrective Torque On Gentle Curve
    [Tags]    LKA    curvature    control    ASIL-C
    Set Ego Speed    90
    Set Lane Curvature Radius    600
    Set Driver Hands On Wheel    ${TRUE}
    ${result}=    Run Lane Scenario And Collect    lka_curve_drift
    Should Be True    ${result}[assist_active]
    Should Be True    ${result}[max_torque_nm] <= 3.0
    Should Be True    ${result}[lateral_error_m] <= 0.30

LKA Should Degrade Gracefully With Poor Right Lane Marking
    [Tags]    LKA    degraded-mode    camera
    Set Ego Speed    85
    Set Lane Marking Quality    left=good    right=poor
    ${result}=    Run Lane Scenario And Collect    lka_right_marking_degraded
    Should Contain    ${result}[mode]    degraded
    Should Be True    ${result}[warning_or_takeover_request]
```

### Example Python Library

```python
# libraries/LaneAssistLibrary.py
from robot.api.deco import keyword, library


@library(scope='TEST')
class LaneAssistLibrary:
    def __init__(self):
        self.state = {
            "scenario": None,
            "speed": 0.0,
            "turn_signal": "off",
            "curvature_radius": 9999,
            "lane_quality": {"left": "good", "right": "good"},
            "hands_on": True,
        }

    @keyword("Set Turn Signal State")
    def set_turn_signal_state(self, state):
        self.state["turn_signal"] = state

    @keyword("Set Lane Marking Quality")
    def set_lane_marking_quality(self, left="good", right="good"):
        self.state["lane_quality"] = {"left": left, "right": right}

    @keyword("Set Lane Curvature Radius")
    def set_lane_curvature_radius(self, radius):
        self.state["curvature_radius"] = float(radius)

    @keyword("Set Driver Hands On Wheel")
    def set_driver_hands_on_wheel(self, state):
        self.state["hands_on"] = bool(state)

    @keyword("Load Lane Scenario")
    def load_lane_scenario(self, scenario):
        self.state["scenario"] = scenario

    @keyword("Start Lane Scenario")
    def start_lane_scenario(self):
        pass

    @keyword("Wait For Lane Scenario Completion")
    def wait_for_lane_scenario_completion(self, timeout="20s"):
        pass

    @keyword("Get Lane Assist Result")
    def get_lane_assist_result(self):
        scenario = self.state["scenario"]
        if scenario == "ldw_intended_lane_change":
            return {"warning_issued": False}
        if scenario == "lka_right_marking_degraded":
            return {
                "assist_active": False,
                "mode": "degraded_camera_confidence",
                "warning_or_takeover_request": True,
            }
        return {
            "warning_issued": True,
            "time_to_line_crossing_s": 1.1,
            "assist_active": True,
            "max_torque_nm": 2.4,
            "lateral_error_m": 0.18,
            "mode": "normal",
            "warning_or_takeover_request": False,
        }
```

---

## 3.5 ACC Testing

ACC controls longitudinal motion to maintain driver-set speed and time gap. Validation must cover **steady follow**, **target selection**, **cut-in**, **cut-out**, **stop-and-go**, and transitions between **speed control** and **distance control**.

### ACC Scenario Matrix

| Scenario | Description | Main KPI |
|---|---|---|
| steady_follow | Ego follows lead at set gap | time gap error |
| lead_brake | Lead decelerates moderately/hard | jerk, min TTC |
| cut_in | New vehicle enters lane ahead | target acquisition time |
| cut_out | Lead leaves lane exposing farther target | target handover stability |
| free_road_resume | Lead disappears | acceleration profile |
| stop_and_go | Queue traffic | restart timing |

### ACC State Machine

```text
                +----------------+
                | Speed Control  |
                +--------+-------+
                         |
              target detected in lane
                         v
                +----------------+
                | Gap Control    |
                +---+--------+---+
                    |        |
           target lost   target too close / braking
                    |        |
                    v        v
         +----------------+  +------------------+
         | Resume Speed   |  | Emergency Handover|
         +----------------+  +------------------+
```

### Robot Framework ACC Suite

```robot
*** Settings ***
Documentation    ACC follow distance and target transition tests
Library          libraries/AccLibrary.py
Library          Collections

*** Variables ***
${TARGET_GAP_S}          1.8
${MAX_GAP_ERROR_S}       0.3
${MAX_JERK_MPS3}         2.5

*** Test Cases ***
ACC Should Maintain Selected Time Gap Behind Lead Vehicle
    [Tags]    ACC    follow    regression    ASIL-B
    Enable ACC
    Set ACC Cruise Speed    110
    Set ACC Time Gap        ${TARGET_GAP_S}
    Configure Lead Vehicle  speed_kph=95    initial_distance_m=48
    Start ACC Scenario      acc_steady_follow
    Wait For ACC Completion
    ${kpi}=    Get ACC KPIs
    Should Be True    abs(${kpi}[gap_error_s]) <= ${MAX_GAP_ERROR_S}
    Should Be True    ${kpi}[max_jerk_mps3] <= ${MAX_JERK_MPS3}

ACC Should React Safely To Aggressive Cut In
    [Tags]    ACC    cut-in    safety    ASIL-C
    Enable ACC
    Set ACC Cruise Speed    100
    Set ACC Time Gap        2.0
    Configure Cut In Actor  entry_distance_m=18    actor_speed_kph=80
    Start ACC Scenario      acc_cut_in_aggressive
    Wait For ACC Completion
    ${kpi}=    Get ACC KPIs
    Should Be True    ${kpi}[min_time_gap_s] >= 0.9
    Should Be True    ${kpi}[target_switch_count] == 1
    Should Be True    ${kpi}[brake_request_detected]

ACC Should Transition Smoothly After Lead Vehicle Cut Out
    [Tags]    ACC    cut-out    comfort
    Enable ACC
    Set ACC Cruise Speed    120
    Configure Lead Vehicle  speed_kph=100    initial_distance_m=55
    Configure Forward Target Behind Lead    speed_kph=108    distance_m=85
    Start ACC Scenario      acc_cut_out_dual_target
    Wait For ACC Completion
    ${kpi}=    Get ACC KPIs
    Should Be True    ${kpi}[target_switch_count] == 1
    Should Be True    ${kpi}[overshoot_kph] <= 3.0
```

### Example Python ACC Library

```python
# libraries/AccLibrary.py
from robot.api.deco import keyword, library


@library(scope='TEST')
class AccLibrary:
    def __init__(self):
        self.kpi = {}

    @keyword("Enable ACC")
    def enable_acc(self):
        pass

    @keyword("Set ACC Cruise Speed")
    def set_acc_cruise_speed(self, speed_kph):
        pass

    @keyword("Set ACC Time Gap")
    def set_acc_time_gap(self, gap_s):
        pass

    @keyword("Configure Lead Vehicle")
    def configure_lead_vehicle(self, **kwargs):
        pass

    @keyword("Configure Cut In Actor")
    def configure_cut_in_actor(self, **kwargs):
        pass

    @keyword("Configure Forward Target Behind Lead")
    def configure_forward_target_behind_lead(self, **kwargs):
        pass

    @keyword("Start ACC Scenario")
    def start_acc_scenario(self, scenario):
        if scenario == "acc_cut_in_aggressive":
            self.kpi = {
                "gap_error_s": 0.0,
                "max_jerk_mps3": 2.4,
                "min_time_gap_s": 1.1,
                "target_switch_count": 1,
                "brake_request_detected": True,
                "overshoot_kph": 0.0,
            }
        elif scenario == "acc_cut_out_dual_target":
            self.kpi = {
                "gap_error_s": 0.1,
                "max_jerk_mps3": 1.8,
                "min_time_gap_s": 1.7,
                "target_switch_count": 1,
                "brake_request_detected": False,
                "overshoot_kph": 2.0,
            }
        else:
            self.kpi = {
                "gap_error_s": 0.15,
                "max_jerk_mps3": 1.3,
                "min_time_gap_s": 1.8,
                "target_switch_count": 0,
                "brake_request_detected": False,
                "overshoot_kph": 0.0,
            }

    @keyword("Wait For ACC Completion")
    def wait_for_acc_completion(self):
        pass

    @keyword("Get ACC KPIs")
    def get_acc_kpis(self):
        return self.kpi
```

---

## 3.6 BSM Testing

Blind Spot Monitoring detects vehicles in adjacent lanes and warns the driver, often escalating when the turn signal indicates intended lane change.

### Blind Spot Zones

```text
                    Rear bumper reference
                           |
                           v
        left blind zone    | ego vehicle |    right blind zone
     <---------------------+-------------+--------------------->
        typical coverage: adjacent lane, rear quarter, side zone
```

### BSM Test Conditions

| Condition | Why test it |
|---|---|
| Adjacent vehicle constant speed | basic detection |
| Fast overtaking vehicle | update rate and target persistence |
| Motorcycle narrow profile | difficult RCS/classification case |
| Vehicle in next-next lane | avoid false positive |
| Turn signal active | warning escalation |
| Trailer attached | altered blind zone geometry |

### Robot Framework BSM Cases

```robot
*** Settings ***
Library    libraries/BsmLibrary.py

*** Test Cases ***
BSM Should Illuminate Warning For Vehicle In Left Blind Spot
    [Tags]    BSM    functional
    Configure Blind Spot Target    side=left    rel_speed_kph=5    longitudinal_offset_m=-3
    Start BSM Scenario    bsm_left_constant
    ${result}=    Get BSM Result
    Should Be True    ${result}[left_warning]
    Should Be False   ${result}[right_warning]

BSM Should Escalate When Driver Signals Into Occupied Lane
    [Tags]    BSM    HMI    safety
    Configure Blind Spot Target    side=right    rel_speed_kph=0    longitudinal_offset_m=0
    Set Turn Signal State          right
    Start BSM Scenario             bsm_right_lane_change_attempt
    ${result}=    Get BSM Result
    Should Be True    ${result}[right_warning]
    Should Be True    ${result}[escalated_alert]
```

### Example Python Library

```python
# libraries/BsmLibrary.py
from robot.api.deco import keyword, library


@library(scope='TEST')
class BsmLibrary:
    def __init__(self):
        self.result = {}

    @keyword("Configure Blind Spot Target")
    def configure_blind_spot_target(self, **kwargs):
        self.result = {"left_warning": False, "right_warning": False, "escalated_alert": False}
        if kwargs.get("side") == "left":
            self.result["left_warning"] = True
        if kwargs.get("side") == "right":
            self.result["right_warning"] = True

    @keyword("Start BSM Scenario")
    def start_bsm_scenario(self, scenario):
        if scenario == "bsm_right_lane_change_attempt":
            self.result["escalated_alert"] = True

    @keyword("Get BSM Result")
    def get_bsm_result(self):
        return self.result
```

---

## 3.7 Traffic Sign Recognition Testing

TSR depends heavily on camera performance, image quality, sign occlusion, regional variants, and temporal filtering. The system must not only detect signs but also publish a stable and correct interpretation.

### TSR Scenario Categories

| Category | Examples |
|---|---|
| Speed limit recognition | 30, 50, 80, 120 kph |
| Conditional signs | school zone, rain-only, truck-only |
| End-of-restriction | speed limit cancel, no-passing end |
| Confusers | billboard, sticker, partial sign |
| Degradation | glare, night, blur, dirty lens |

### Robot Framework TSR Example

```robot
*** Settings ***
Library    libraries/TsrLibrary.py

*** Test Cases ***
TSR Should Recognize Eighty Kph Speed Sign
    [Tags]    TSR    camera    perception
    Load Camera Scene         tsr_speed_80_daylight
    Start TSR Analysis
    ${sign}=    Get Recognized Sign
    Should Be Equal           ${sign}[type]          speed_limit
    Should Be Equal As Integers    ${sign}[value]    80
    Should Be True            ${sign}[confidence] >= 0.90

TSR Should Reject Billboard That Resembles Speed Sign
    [Tags]    TSR    false-positive
    Load Camera Scene         tsr_billboard_false_positive
    Start TSR Analysis
    ${sign}=    Get Recognized Sign
    Should Be Equal           ${sign}[type]          none
```

### Python Library Sketch

```python
# libraries/TsrLibrary.py
from robot.api.deco import keyword, library


@library(scope='TEST')
class TsrLibrary:
    def __init__(self):
        self.scene = None

    @keyword("Load Camera Scene")
    def load_camera_scene(self, scene):
        self.scene = scene

    @keyword("Start TSR Analysis")
    def start_tsr_analysis(self):
        pass

    @keyword("Get Recognized Sign")
    def get_recognized_sign(self):
        if self.scene == "tsr_speed_80_daylight":
            return {"type": "speed_limit", "value": 80, "confidence": 0.97}
        return {"type": "none", "value": 0, "confidence": 0.12}
```

### Important TSR Checks

- correct sign class and value
- stable output over multiple frames
- no stale sign after leaving sign zone
- regional sign-set handling
- fallback behavior when confidence drops

---

## 3.8 Sensor Fusion Validation

Fusion combines complementary sensor strengths:

- **radar**: strong range and relative velocity
- **camera**: classification, lane/sign context
- **lidar**: geometric precision when available

### Fusion Architecture

```text
Radar tracks -----------+
                         \
Camera detections -------+--> Association --> Track fusion --> Object list --> ADAS function
                          /
Lidar clusters ----------+

Checks:
- track association correctness
- object continuity
- classification stability
- timestamp alignment
```

### Fusion Validation Objectives

| Check | Description |
|---|---|
| Association | radar target and camera object represent same actor |
| Latency alignment | timestamps within acceptable skew |
| Classification carry-over | object remains vehicle/pedestrian/cyclist correctly |
| Dropout resilience | one sensor lost but track persists safely |
| Conflict handling | contradictory detections handled conservatively |

### Robot Framework Fusion Example

```robot
*** Settings ***
Library    libraries/SensorFusionLibrary.py

*** Test Cases ***
Fusion Should Correlate Radar And Camera Vehicle Track
    [Tags]    fusion    radar    camera
    Inject Radar Track     id=201    range_m=42.0    rel_speed_mps=-8.0    azimuth_deg=1.2
    Inject Camera Object   id=cam_17    cls=vehicle    x_m=41.5    y_m=0.9
    Run Fusion Cycle
    ${track}=    Get Fused Track    fused_id=1
    Should Be Equal As Integers    ${track}[source_count]    2
    Should Be Equal                ${track}[classification]  vehicle
    Should Be True                 ${track}[tracking_stable]

Fusion Should Keep Track During Temporary Camera Loss
    [Tags]    fusion    dropout    robustness
    Inject Radar Track     id=330    range_m=28.0    rel_speed_mps=-2.0    azimuth_deg=-0.3
    Inject Camera Object   id=cam_99    cls=pedestrian    x_m=27.7    y_m=-0.2
    Run Fusion Cycle
    Remove Camera Object   cam_99
    Run Fusion Cycle
    ${track}=    Get Fused Track    fused_id=1
    Should Be True    ${track}[predicted_from_radar]
    Should Be True    ${track}[age_ms] <= 300
```

### Python Library Example

```python
# libraries/SensorFusionLibrary.py
from robot.api.deco import keyword, library


@library(scope='TEST')
class SensorFusionLibrary:
    def __init__(self):
        self.radar = []
        self.camera = []
        self.track = None

    @keyword("Inject Radar Track")
    def inject_radar_track(self, **kwargs):
        self.radar.append(kwargs)

    @keyword("Inject Camera Object")
    def inject_camera_object(self, **kwargs):
        self.camera.append(kwargs)

    @keyword("Run Fusion Cycle")
    def run_fusion_cycle(self):
        if self.radar and self.camera:
            cls = self.camera[-1].get("cls", "unknown")
            self.track = {
                "source_count": 2,
                "classification": cls,
                "tracking_stable": True,
                "predicted_from_radar": False,
                "age_ms": 80,
            }
        elif self.radar:
            self.track = {
                "source_count": 1,
                "classification": "pedestrian",
                "tracking_stable": True,
                "predicted_from_radar": True,
                "age_ms": 180,
            }

    @keyword("Remove Camera Object")
    def remove_camera_object(self, obj_id):
        self.camera = [obj for obj in self.camera if obj.get("id") != obj_id]

    @keyword("Get Fused Track")
    def get_fused_track(self, fused_id=1):
        return self.track
```

---

## 3.9 Fault Injection Testing for ADAS

Fault injection proves the system behaves safely under degraded inputs and faults. This is mandatory for robust release confidence and often required by safety work products.

### Fault Categories

| Fault | Example | Expected system response |
|---|---|---|
| Sensor timeout | radar frame missing 500 ms | degrade or disable dependent feature |
| Frozen image | camera repeats old frame | detect stale data, set fault |
| Signal bias | radar range offset +8 m | plausibility failure or fusion mismatch |
| Increased noise | lane model jitter | confidence drop, takeover request |
| Complete loss | lidar disconnected | continue with remaining sensors if safe |
| Network corruption | invalid CRC / malformed payload | discard frame, log DTC |

### Fault Injection Architecture

```text
Robot Test --> Fault Manager --> Inject fault at sensor/network layer --> ECU behavior
                                 |                                   \
                                 +--> timing control                  +--> logs / DTC / degraded mode
```

### Robot Framework Fault Injection Suite

```robot
*** Settings ***
Library    libraries/FaultInjectionLibrary.py

*** Test Cases ***
AEB Should Disable Autonomous Braking On Radar Timeout If No Redundant Confirmation
    [Tags]    fault    AEB    radar    safety
    Activate Fault         sensor=radar_front    fault_type=timeout    start_ms=1500    duration_ms=800
    Start Scenario With Fault    aeb_vehicle_target_with_radar_loss
    ${result}=    Get Fault Response
    Should Be Equal    ${result}[function_mode]    degraded
    Should Be True     ${result}[dtc_logged]
    Should Be False    ${result}[unsafe_brake_command]

LKA Should Request Driver Takeover On Camera Quality Collapse
    [Tags]    fault    LKA    camera
    Activate Fault         sensor=front_camera    fault_type=confidence_drop    start_ms=1000    duration_ms=5000
    Start Scenario With Fault    lka_camera_dropout_curve
    ${result}=    Get Fault Response
    Should Contain        ${result}[hmi_message]    Take Over
    Should Be Equal       ${result}[function_mode]  limited
```

### Python Library Example

```python
# libraries/FaultInjectionLibrary.py
from robot.api.deco import keyword, library


@library(scope='TEST')
class FaultInjectionLibrary:
    def __init__(self):
        self.active_fault = None
        self.result = {}

    @keyword("Activate Fault")
    def activate_fault(self, **kwargs):
        self.active_fault = kwargs

    @keyword("Start Scenario With Fault")
    def start_scenario_with_fault(self, scenario):
        if self.active_fault and self.active_fault.get("sensor") == "radar_front":
            self.result = {
                "function_mode": "degraded",
                "dtc_logged": True,
                "unsafe_brake_command": False,
                "hmi_message": "AEB limited",
            }
        else:
            self.result = {
                "function_mode": "limited",
                "dtc_logged": True,
                "unsafe_brake_command": False,
                "hmi_message": "Take Over Immediately",
            }

    @keyword("Get Fault Response")
    def get_fault_response(self):
        return self.result
```

### Fault Injection Checklist

- verify DTC set and clear behavior
- verify function disable/degrade threshold
- verify no hazardous unintended actuation
- verify driver notification timing
- verify recovery after fault removal

---

## 3.10 ISO 26262 Traceability

ADAS tests should map cleanly from **hazard analysis** to **safety goals**, **technical safety requirements**, and finally **test cases**.

### Example Traceability Chain

```text
Hazard: Rear-end collision due to missed lead vehicle braking
   -> Safety Goal: Prevent or mitigate frontal collision
      -> TSR-AEB-014: AEB shall command braking when TTC < threshold and target valid
         -> SWR-AEB-067: brake request issued within 800 ms after confirmation
            -> RF Test: AEB Should Brake For Stopped Vehicle At Urban Speed
```

### ASIL-Oriented Traceability Table

| Requirement ID | Description | ASIL | Test Case | Evidence |
|---|---|---|---|---|
| TSR-AEB-014 | AEB shall brake for valid forward collision threat | D | AEB Should Brake For Stopped Vehicle At Urban Speed | trace, KPI export |
| TSR-AEB-021 | AEB shall avoid braking for overhead non-target | C | AEB Should Not Trigger For Overhead Sign Structure | event log |
| TSR-LKA-009 | LKA shall maintain lane with bounded torque | C | LKA Should Apply Corrective Torque On Gentle Curve | control trace |
| TSR-ACC-011 | ACC shall maintain selected time gap | B | ACC Should Maintain Selected Time Gap Behind Lead Vehicle | KPI summary |
| TSR-BSM-006 | BSM shall warn for occupied blind zone | B | BSM Should Illuminate Warning For Vehicle In Left Blind Spot | HMI log |
| TSR-TSR-004 | TSR shall detect posted speed limit under nominal conditions | QM/B | TSR Should Recognize Eighty Kph Speed Sign | frame annotation |

### Requirement Tagging in Robot Framework

```robot
*** Test Cases ***
AEB Should Brake For Stopped Vehicle At Urban Speed
    [Tags]    req:TSR-AEB-014    req:SWR-AEB-067    asil:D    feature:AEB
    # test steps...

LKA Should Apply Corrective Torque On Gentle Curve
    [Tags]    req:TSR-LKA-009    asil:C    feature:LKA
    # test steps...
```

### Traceability Extraction Pattern

A CI parser can extract Robot tags and produce a requirement coverage matrix.

```python
# scripts/extract_traceability.py
from pathlib import Path
import re

REQ_RE = re.compile(r"req:([A-Z0-9\-]+)")
ASIL_RE = re.compile(r"asil:([A-Z]+)")


def scan_robot_file(path: Path):
    rows = []
    current_test = None
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped and not line.startswith(" ") and not stripped.startswith("***"):
            current_test = stripped
        if "[Tags]" in stripped and current_test:
            reqs = REQ_RE.findall(stripped)
            asil = ASIL_RE.findall(stripped)
            for req in reqs:
                rows.append({"test_case": current_test, "requirement": req, "asil": ",".join(asil)})
    return rows
```

---

## 3.11 Performance Metrics

ADAS validation is not complete without measurable KPIs. Robot Framework can both assert thresholds and export structured metrics.

### Key Metrics

| Metric | Definition | Example Use |
|---|---|---|
| Reaction time | time from valid threat appearance to warning/brake | AEB timing |
| Detection rate | true detections / valid opportunities | pedestrian recognition |
| False positive rate | false activations / exposure time or scenarios | AEB overhead sign case |
| False negative rate | missed detections / valid opportunities | BSM missed motorcycle |
| Lateral error | deviation from lane center | LKA controller quality |
| Time gap error | actual minus requested ACC gap | ACC following behavior |
| Jerk | rate of acceleration change | comfort and stability |
| Track age | duration fused object persists | fusion robustness |

### KPI Collection Table

| Function | Must-have KPI | Typical threshold example |
|---|---|---|
| AEB | reaction time | <= 0.8 s for reference scenario |
| AEB | false positive count | 0 in nominal false-target suite |
| LDW | warning timing | before line crossing margin consumed |
| LKA | max lateral error | <= 0.30 m on defined curve |
| ACC | time gap error | <= ±0.3 s steady-state |
| BSM | detection availability | >= 99% blind-zone occupancy cases |
| TSR | sign detection rate | >= 95% nominal daylight |
| Fusion | association accuracy | >= 98% on curated dataset |

### Robot KPI Validation Example

```robot
*** Keywords ***
Verify ADAS KPI Thresholds
    [Arguments]    ${kpi}
    Should Be True    ${kpi}[reaction_time_s] <= 0.80
    Should Be True    ${kpi}[false_positive_rate] <= 0.01
    Should Be True    ${kpi}[detection_rate] >= 0.95
```

### Example KPI Export Object

```python
kpi_summary = {
    "feature": "AEB",
    "scenario": "pedestrian_crossing_right",
    "reaction_time_s": 0.73,
    "false_positive_rate": 0.0,
    "detection_rate": 1.0,
    "peak_decel_mps2": 5.4,
    "requirement_ids": ["TSR-AEB-014", "SWR-AEB-067"],
    "asil": "D",
}
```

---

## 3.12 Integrated Example: Multi-Feature ADAS Regression Suite

```robot
*** Settings ***
Documentation    Example top-level ADAS regression launcher
Resource         resources/common_adas_keywords.robot
Library          libraries/AdasBenchLibrary.py
Library          libraries/AebScenarioLibrary.py
Library          libraries/LaneAssistLibrary.py
Library          libraries/AccLibrary.py
Library          libraries/BsmLibrary.py
Library          libraries/TsrLibrary.py
Library          libraries/SensorFusionLibrary.py
Library          libraries/FaultInjectionLibrary.py
Suite Setup      Initialize ADAS Bench
Suite Teardown   Shutdown ADAS Bench

*** Test Cases ***
ADAS Smoke - AEB Vehicle
    [Tags]    smoke    AEB    req:TSR-AEB-014    asil:D
    Set Ego Speed    50
    Configure Target Vehicle    distance_m=45    relative_speed_kph=0    lane=ego
    Run And Verify AEB Scenario    aeb_stopped_vehicle_50kph

ADAS Smoke - LKA Curve Support
    [Tags]    smoke    LKA    req:TSR-LKA-009    asil:C
    Set Ego Speed    90
    Set Lane Curvature Radius    600
    ${result}=    Run Lane Scenario And Collect    lka_curve_drift
    Should Be True    ${result}[assist_active]

ADAS Smoke - ACC Steady Follow
    [Tags]    smoke    ACC    req:TSR-ACC-011    asil:B
    Enable ACC
    Set ACC Cruise Speed    110
    Set ACC Time Gap        1.8
    Configure Lead Vehicle  speed_kph=95    initial_distance_m=48
    Start ACC Scenario      acc_steady_follow
    Wait For ACC Completion
    ${kpi}=    Get ACC KPIs
    Should Be True    abs(${kpi}[gap_error_s]) <= 0.3
```

---

## 3.13 Best Practices for Realistic Automotive ADAS Testing

1. **Separate scenario definition from assertion logic.** Keep targets, roads, weather, and actor timing in reusable scenario data.
2. **Version-control calibration sets.** ADAS behavior often changes with calibration, not only software.
3. **Time-synchronize all sources.** ECU logs, bus traces, simulator timestamps, and video frames must share a reliable time base.
4. **Assert both action and non-action.** False-positive testing is as important as positive-trigger testing.
5. **Include degraded modes.** A safety feature that works only in nominal conditions is incomplete.
6. **Tag tests with requirements and ASIL levels.** This simplifies compliance reporting.
7. **Capture artifacts automatically.** Store traces, screenshots, sensor snippets, and KPI JSON per test.

---

## 3.14 Exercises

### Exercise 1 — AEB Late-Brake Analysis
Create a Robot test for a stopped-vehicle scenario at 70 kph. Add assertions for:
- FCW before brake request
- reaction time <= 0.75 s
- peak deceleration >= 6.0 m/s²
- no collision

### Exercise 2 — LDW Suppression Logic
Write two tests:
1. lane departure without turn signal -> warning expected
2. same departure with turn signal active -> warning suppressed

Add tags for a made-up requirement and ASIL level.

### Exercise 3 — ACC Cut-In Dataset
Create a data-driven ACC suite using a template and variables for:
- cut-in distance
- actor speed
- requested time gap
- minimum allowed time gap after cut-in

### Exercise 4 — BSM Motorcycle Case
Design a blind-spot test for a motorcycle approaching quickly in the adjacent lane. Add an escalation check when the driver enables the turn signal.

### Exercise 5 — TSR False Positive Campaign
Create a suite of scenes containing:
- billboard with circular red border
- sticker on truck rear
- partially occluded speed sign
- valid 60 kph sign

Assert the correct classification behavior for each.

### Exercise 6 — Fusion Fault Tolerance
Write a test where camera detections drop out for 250 ms while radar continues tracking. Verify fused track persistence and safe classification behavior.

### Exercise 7 — Traceability Export
Extend the Python traceability extractor so it scans all `*.robot` files in a directory and emits CSV rows:
`test_case,requirement,asil,file`

### Exercise 8 — KPI Dashboard Design
Define a KPI table for AEB, LKA, ACC, and TSR with columns:
- feature
- scenario
- measured value
- threshold
- pass/fail
- requirement ID

Then describe how Robot Framework would populate it in CI.

---

## 3.15 Summary

In this part, you saw how Robot Framework can validate ADAS features across **scenario orchestration**, **sensor stimulation**, **fusion**, **fault handling**, and **safety traceability**. The main pattern is consistent: configure the environment, run a reproducible scenario, collect objective KPIs, and assert both functional and safety expectations.

In the next part, continue with more advanced automotive automation topics in [ROBOT_FRAMEWORK_AUTOMOTIVE_PART4.md](ROBOT_FRAMEWORK_AUTOMOTIVE_PART4.md).

---

[← Previous: ROBOT_FRAMEWORK_AUTOMOTIVE_PART2.md](ROBOT_FRAMEWORK_AUTOMOTIVE_PART2.md) | [Next: ROBOT_FRAMEWORK_AUTOMOTIVE_PART4.md →](ROBOT_FRAMEWORK_AUTOMOTIVE_PART4.md)
