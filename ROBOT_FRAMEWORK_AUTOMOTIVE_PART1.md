# Part 1: Robot Framework Fundamentals (Beginner)

---

## 1.1 What Is Robot Framework?

Robot Framework is an **open-source, keyword-driven test automation framework** written in Python. It uses a tabular syntax that makes tests readable even by non-programmers.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Keyword-Driven** | Tests are written using human-readable keywords |
| **Extensible** | Custom libraries in Python, Java, or remote APIs |
| **Data-Driven** | Supports test templates for parameterized testing |
| **Rich Ecosystem** | 100+ external libraries available |
| **Built-in Reporting** | HTML reports and logs generated automatically |
| **Cross-Platform** | Works on Windows, Linux, macOS |

### Why Robot Framework for Automotive?

1. **Readable by non-coders** — Validation engineers, system engineers, and OEM stakeholders can understand tests
2. **Protocol-agnostic** — Easily integrates with CAN, LIN, Ethernet, UDS through Python libraries
3. **Layered architecture** — Separates test logic from implementation (keywords vs. libraries)
4. **CI/CD friendly** — Integrates with Jenkins, GitLab CI, GitHub Actions
5. **Free and open-source** — No license costs unlike commercial tools (CANoe, EXAM)

---

## 1.2 Installation & Environment Setup

### Step 1: Install Python

```bash
# Verify Python installation
python --version   # Should be 3.8+
pip --version
```

### Step 2: Install Robot Framework

```bash
pip install robotframework
# Verify
robot --version
```

### Step 3: Install an IDE

| IDE | Plugin |
|-----|--------|
| VS Code | *Robot Framework Language Server* extension |
| PyCharm | *Robot Framework Support* plugin |
| RIDE | Dedicated Robot Framework IDE (`pip install robotframework-ride`) |

### Step 4: Recommended Project Structure

```
automotive_test_project/
├── tests/
│   ├── adas/
│   │   ├── aeb_tests.robot
│   │   └── ldw_tests.robot
│   ├── infotainment/
│   │   ├── media_player_tests.robot
│   │   └── navigation_tests.robot
│   ├── cluster/
│   │   └── gauge_display_tests.robot
│   └── telematics/
│       └── ota_update_tests.robot
├── resources/
│   ├── keywords/
│   │   ├── can_keywords.resource
│   │   ├── uds_keywords.resource
│   │   └── common_keywords.resource
│   └── variables/
│       ├── can_signals.yaml
│       └── ecu_config.yaml
├── libraries/
│   ├── CanBusLibrary.py
│   ├── UdsLibrary.py
│   └── HilControlLibrary.py
├── data/
│   ├── test_vectors/
│   └── dbc_files/
├── results/
└── requirements.txt
```

---

## 1.3 Robot Framework Syntax Basics

### 1.3.1 Test Case File Structure

A `.robot` file has four main sections:

```robot
*** Settings ***
Library    Collections
Library    String
Resource   ../resources/keywords/common_keywords.resource
Variables  ../resources/variables/ecu_config.yaml

Suite Setup       Initialize Test Environment
Suite Teardown    Cleanup Test Environment

*** Variables ***
${ECU_NAME}        ADAS_Controller
${TIMEOUT}         10s
@{SPEED_VALUES}    0    30    60    100    120
&{CAN_CONFIG}      channel=can0    bitrate=500000

*** Test Cases ***
Verify ECU Is Responsive
    [Documentation]    Verify that the ADAS ECU responds to a diagnostic request.
    [Tags]    smoke    adas    priority-high
    Send Diagnostic Request    ${ECU_NAME}    TesterPresent
    Response Should Be Positive

Verify Speed Signal Range
    [Documentation]    Validate vehicle speed signal stays within 0-260 km/h.
    [Tags]    regression    adas
    [Template]    Verify Speed Signal Value
    FOR    ${speed}    IN    @{SPEED_VALUES}
        ${speed}
    END

*** Keywords ***
Verify Speed Signal Value
    [Arguments]    ${expected_speed}
    Send CAN Signal    VehicleSpeed    ${expected_speed}
    ${actual}=    Read CAN Signal    VehicleSpeed
    Should Be Equal As Numbers    ${actual}    ${expected_speed}

Initialize Test Environment
    Log    Setting up test environment
    Connect To ECU    ${ECU_NAME}

Cleanup Test Environment
    Log    Tearing down test environment
    Disconnect From ECU    ${ECU_NAME}
```

### 1.3.2 Variable Types

| Type | Syntax | Example |
|------|--------|---------|
| Scalar | `${var}` | `${ECU_NAME}    ADAS_ECU` |
| List | `@{var}` | `@{SPEEDS}    0    50    100` |
| Dictionary | `&{var}` | `&{CONFIG}    key1=val1    key2=val2` |
| Environment | `%{var}` | `%{HOME}` accesses OS env variable |

### 1.3.3 Built-in Keywords (Most Used)

```robot
# Logging
Log    This is a message
Log To Console    Visible on terminal

# Assertions
Should Be Equal    ${actual}    ${expected}
Should Be Equal As Numbers    ${actual}    100
Should Be True    ${speed} > 0 and ${speed} < 260
Should Contain    ${response}    Positive

# Conditionals
IF    ${speed} > 120
    Log    Overspeed detected
ELSE IF    ${speed} > 80
    Log    Highway speed
ELSE
    Log    City speed
END

# Loops
FOR    ${i}    IN RANGE    10
    Log    Iteration ${i}
END

# Wait / Retry
Wait Until Keyword Succeeds    3x    1s    Check ECU Response

# Variable Assignment
${result}=    Evaluate    100 + 50
${length}=    Get Length    ${my_list}
```

---

## 1.4 Resource Files and Keyword Abstraction

### Why Use Resource Files?

Resource files (`.resource`) let you define **reusable keywords** shared across test suites.

```robot
# resources/keywords/can_keywords.resource
*** Settings ***
Library    ../../libraries/CanBusLibrary.py

*** Keywords ***
Send CAN Signal
    [Arguments]    ${signal_name}    ${value}
    [Documentation]    Sends a CAN signal with the given value.
    ${result}=    Can Bus Send    ${signal_name}    ${value}
    Should Be True    ${result}    Failed to send signal ${signal_name}

Read CAN Signal
    [Arguments]    ${signal_name}
    [Documentation]    Reads the current value of a CAN signal.
    ${value}=    Can Bus Read    ${signal_name}
    RETURN    ${value}

Wait For CAN Signal Value
    [Arguments]    ${signal_name}    ${expected_value}    ${timeout}=5s
    Wait Until Keyword Succeeds    ${timeout}    500ms
    ...    Verify Signal Value    ${signal_name}    ${expected_value}

Verify Signal Value
    [Arguments]    ${signal_name}    ${expected_value}
    ${actual}=    Read CAN Signal    ${signal_name}
    Should Be Equal As Numbers    ${actual}    ${expected_value}
```

---

## 1.5 Writing Your First Automotive Test

### Example: Simple CAN Signal Validation

```robot
*** Settings ***
Library     ../../libraries/CanBusLibrary.py
Resource    ../../resources/keywords/can_keywords.resource

Suite Setup       Open CAN Channel    can0    500000
Suite Teardown    Close CAN Channel

*** Variables ***
${SIGNAL_VEHICLE_SPEED}     VehicleSpeed
${SIGNAL_ENGINE_RPM}        EngineRPM

*** Test Cases ***
TC-001: Verify Vehicle Speed Default Value
    [Documentation]    After ignition ON, vehicle speed should be 0.
    [Tags]    smoke    can    cluster
    Simulate Ignition On
    ${speed}=    Read CAN Signal    ${SIGNAL_VEHICLE_SPEED}
    Should Be Equal As Numbers    ${speed}    0

TC-002: Verify Engine RPM Updates
    [Documentation]    When engine RPM signal is sent, the value should be readable.
    [Tags]    regression    can
    Send CAN Signal    ${SIGNAL_ENGINE_RPM}    3000
    Wait For CAN Signal Value    ${SIGNAL_ENGINE_RPM}    3000

TC-003: Verify Speed Limit Warning
    [Documentation]    Speed above 120 km/h should trigger a warning signal.
    [Tags]    functional    adas
    Send CAN Signal    ${SIGNAL_VEHICLE_SPEED}    130
    Sleep    1s
    ${warning}=    Read CAN Signal    SpeedLimitWarning
    Should Be Equal As Numbers    ${warning}    1
```

---

## 1.6 Running Tests and Understanding Reports

### Running Tests

```bash
# Run all tests
robot tests/

# Run a specific file
robot tests/adas/aeb_tests.robot

# Run by tag
robot --include smoke tests/
robot --exclude wip tests/

# Run with variables
robot --variable ECU_NAME:Cluster_ECU tests/

# Output to specific directory
robot --outputdir results/ tests/

# Run with log level
robot --loglevel DEBUG tests/
```

### Understanding Output Files

| File | Purpose |
|------|---------|
| `output.xml` | Machine-readable raw results |
| `log.html` | Detailed execution log with keyword-level details |
| `report.html` | Summary report with pass/fail statistics |

### Re-processing Results

```bash
# Merge multiple outputs
rebot --merge output1.xml output2.xml

# Filter results
rebot --include smoke output.xml
```

---

## 1.7 Data-Driven Testing with Templates

Data-driven testing is critical in automotive — you often validate the same behavior across many signal values.

```robot
*** Settings ***
Library     ../../libraries/CanBusLibrary.py
Resource    ../../resources/keywords/can_keywords.resource

*** Test Cases ***
Verify Vehicle Speed Signal Accuracy
    [Documentation]    Validate speed signal for multiple values.
    [Tags]    data-driven    can
    [Template]    Validate Speed Signal
    # Input Speed    Expected Display
    0                0
    30               30
    60               60
    100              100
    120              120
    200              200
    255              255

*** Keywords ***
Validate Speed Signal
    [Arguments]    ${input_speed}    ${expected_display}
    Send CAN Signal    VehicleSpeed    ${input_speed}
    Sleep    500ms
    ${displayed}=    Read CAN Signal    VehicleSpeed_Display
    Should Be Equal As Numbers    ${displayed}    ${expected_display}
```

---

## 1.8 Tags and Test Organization

### Tagging Strategy for Automotive Projects

```robot
*** Test Cases ***
TC-ADAS-AEB-001: Emergency Braking at 30 kmph
    [Tags]    adas    aeb    safety    iso26262-ASIL-D    sprint-12    priority-critical
    ...
```

| Tag Category | Examples | Purpose |
|-------------|----------|---------|
| Domain | `adas`, `cluster`, `infotainment`, `telematics` | Filter by subsystem |
| Feature | `aeb`, `ldw`, `media`, `navigation`, `ota` | Filter by feature |
| Priority | `priority-critical`, `priority-high`, `priority-medium` | Release decisions |
| Safety | `iso26262-ASIL-D`, `iso26262-ASIL-B` | Traceability |
| Test Type | `smoke`, `regression`, `functional`, `performance` | Test suite selection |
| Sprint | `sprint-12`, `sprint-13` | Agile tracking |

### Running by Tags

```bash
# Run only ADAS smoke tests
robot --include adasANDsmoke tests/

# Run everything except WIP
robot --exclude wip tests/

# Run critical priority tests
robot --include priority-critical tests/
```

---

## 1.9 Listeners and Hooks

Robot Framework supports **listeners** that execute code during test events.

### Built-in Hooks

```robot
*** Settings ***
Suite Setup       Global Setup
Suite Teardown    Global Teardown
Test Setup        Per Test Setup
Test Teardown     Per Test Teardown

*** Keywords ***
Global Setup
    Log    Initializing HIL bench
    Connect To HIL Bench
    Power On ECU

Global Teardown
    Power Off ECU
    Disconnect From HIL Bench

Per Test Setup
    Log    Starting test: ${TEST NAME}
    Reset ECU To Default State

Per Test Teardown
    Run Keyword If Test Failed    Capture ECU Diagnostic Snapshot
    Log    Finished test: ${TEST NAME} — Status: ${TEST STATUS}
```

### Custom Listener (Python)

```python
# listeners/automotive_listener.py
class AutomotiveListener:
    ROBOT_LISTENER_API_VERSION = 3

    def start_test(self, data, result):
        print(f"[AUTOMOTIVE] Starting: {data.name}")

    def end_test(self, data, result):
        if result.status == "FAIL":
            print(f"[AUTOMOTIVE] FAILED: {data.name} — {result.message}")
            # Could trigger: save CAN trace, capture screenshot, dump DTC
```

```bash
robot --listener listeners/automotive_listener.py tests/
```

---

## 1.10 Exercises — Beginner Level

1. **Install Robot Framework** and run `robot --version`.
2. **Create a test file** `hello_automotive.robot` with a test case that logs "Hello, Automotive Testing!".
3. **Create a resource file** with a keyword `Log Vehicle Info` that takes `${make}` and `${model}` arguments.
4. **Write a data-driven test** that validates 5 different CAN signal values using `[Template]`.
5. **Use tags** to categorize 3 test cases as `smoke`, `regression`, and `functional`, then run only `smoke` tests.
6. **Examine the report** — open `report.html` and `log.html` to understand the output structure.

---

*Next: [Part 2 — Automotive Libraries, Protocols & HIL Integration →](ROBOT_FRAMEWORK_AUTOMOTIVE_PART2.md)*
