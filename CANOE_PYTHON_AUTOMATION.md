# CANoe Tool Automation with Python: Complete Guide

## Table of Contents
1. [Introduction](#introduction)
2. [CANoe COM Interface Basics](#canoe-com-interface-basics)
3. [Installation and Setup](#installation-and-setup)
4. [Core Concepts](#core-concepts)
5. [Working with CANoe](#working-with-canoe)
6. [Message Handling](#message-handling)
7. [Advanced Automation](#advanced-automation)
8. [Best Practices](#best-practices)
9. [Complete Examples](#complete-examples)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is CANoe?

**CANoe** (by Vector Informatik) is a network simulation and testing tool for:
- CAN/CAN FD communication
- LIN (Local Interconnect Network)
- MOST (Media Oriented Systems Transport)
- Ethernet communication
- AUTOSAR environments

### Python with CANoe

Python can automate CANoe through the **COM Interface** (Component Object Model), enabling:

- **Automated Testing** - Run tests without manual intervention
- **Data Collection** - Gather measurements and log data
- **Configuration Management** - Load/save configurations programmatically
- **Message Injection** - Send CAN/LIN messages
- **Analysis** - Process and analyze bus traffic
- **Integration** - Connect with other tools and systems

### Requirements

- **Vector CANoe** 12.0 or higher installed
- **Python 3.6+**
- **pywin32** library (for Windows COM interface)
- DBC file defining your network

### Why Automate CANoe?

```
✅ Faster test execution
✅ Repeatable, consistent tests
✅ Reduce manual errors
✅ Continuous integration compatible
✅ Complex test sequences
✅ Data logging and analysis
✅ 24/7 automated monitoring
```

---

## CANoe COM Interface Basics

### COM vs. Script vs. Python

| Feature | CANoe Python API | VB.NET Script | Python Automation |
|---------|------------------|---------------|-------------------|
| Language | Limited | VB.NET | Full Python |
| Integration | Built-in | Built-in | External |
| Flexibility | Medium | Medium | High |
| Learning Curve | Steep | Medium | Low |
| CI/CD Integration | Difficult | Difficult | Easy |
| Third-party libs | No | Limited | Yes (NumPy, Pandas, etc.) |

### The CANoe Object Model

```
Application
├── Documents
│   └── Document (Measurement)
│       ├── Configuration
│       ├── Measurement
│       ├── MeasurementSetup
│       └── Databases
└── Environment
    └── Variables
```

The key entry point is the `CANoe.Application` COM object.

---

## Installation and Setup

### Step 1: Install Required Packages

```bash
pip install pywin32
pip install comtypes
```

### Step 2: Register COM Type Libraries

```bash
python -m pip install --upgrade pywin32
python -m  pywin32_postinstall -install
```

### Step 3: Verify CANoe Installation

```bash
# Check if CANoe is installed
reg query "HKLM\SOFTWARE\Vector\CANoe" /s
```

### Step 4: Create Basic Connection Script

```python
import sys
import time

# Add Vector CANoe COM interface
try:
    from win32com.client import GetObject
except ImportError:
    print("Error: pywin32 not installed")
    sys.exit(1)

def connect_to_canoe():
    """Connect to running CANoe instance."""
    try:
        # Get running CANoe application
        app = GetObject(None, "CANoe.Application")
        print(f"Connected to CANoe {app.Version}")
        return app
    except:
        print("CANoe is not running. Please start CANoe first.")
        return None

def main():
    app = connect_to_canoe()
    if not app:
        return
    
    print(f"CANoe application object: {app}")
    print(f"Version: {app.Version}")

if __name__ == "__main__":
    main()
```

---

## Core Concepts

### 1. Application Object

The entry point for all CANoe operations:

```python
from win32com.client import GetObject

# Connect to running CANoe
app = GetObject(None, "CANoe.Application")

# Or create new instance
app = GetObject(None, "CANoe.Application")
app.Visible = True
app.Configuration.Modified = False
```

### 2. Document Object

Represents a CANoe measurement:

```python
# Get active document
doc = app.ActiveDocument

# Get document by name
doc = app.Documents("ProjectName")

# Document properties
print(doc.Name)
print(doc.FileName)
print(doc.IsOpen)

# Save document
doc.SaveAs("new_filename.cfg")
```

### 3. Measurement Object

Controls measurement execution:

```python
# Get measurement
measurement = app.ActiveDocument.Measurement

# Start measurement
measurement.Start()

# Stop measurement
measurement.Stop()

# Check if running
if measurement.Running:
    print("Measurement is running")

# Wait for completion
while measurement.Running:
    time.sleep(1)

measurement.Stop()
```

### 4. Environment Object

Access system variables:

```python
env = app.Environment

# Get variable
speed = env.GetVariable("Speed")
print(f"Speed: {speed}")

# Set variable
env.SetVariable("Speed", 100)

# Set variable by name
env.GetVariable("EngineRPM").Value = 3000
```

### 5. Databases

Access DBC files and signals:

```python
# Get database
db = app.ActiveDocument.Databases(0)

# Get message by name
msg = db.GetMessage("EngineData")

# Get signal by name
signal = msg.GetSignal("EngineSpeed")

# Access signal properties
print(signal.Name)
print(signal.ID)
print(signal.Multiplexing)
```

---

## Working with CANoe

### Loading a Project

```python
from win32com.client import GetObject
import os

def load_canoe_project(config_path):
    """Load a CANoe configuration."""
    try:
        app = GetObject(None, "CANoe.Application")
        
        # Check if file exists
        if not os.path.exists(config_path):
            print(f"Configuration file not found: {config_path}")
            return None
        
        # Open the configuration
        print(f"Loading configuration: {config_path}")
        doc = app.Documents.Open(config_path)
        
        print(f"Loaded: {doc.Name}")
        return doc
    
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

# Usage
config_file = r"C:\CANoe_Projects\MyProject\myconfig.cfg"
doc = load_canoe_project(config_file)
```

### Starting a Measurement

```python
def start_measurement(doc, duration_seconds=10):
    """Start a measurement for specified duration."""
    try:
        measurement = doc.Measurement
        
        # Check if measurement is already running
        if measurement.Running:
            print("Measurement is already running")
            return False
        
        print("Starting measurement...")
        measurement.Start()
        
        # Wait for specified duration
        time.sleep(duration_seconds)
        
        # Stop measurement
        measurement.Stop()
        print("Measurement stopped")
        
        return True
    
    except Exception as e:
        print(f"Error during measurement: {e}")
        return False

# Usage
start_measurement(doc, duration_seconds=30)
```

### Sending CAN Messages

```python
def send_can_message(app, message_name, signal_values):
    """
    Send a CAN message with signal values.
    
    Args:
        app: CANoe application object
        message_name: Name of the message (from DBC)
        signal_values: Dictionary of signal_name: value
    """
    try:
        db = app.ActiveDocument.Databases(0)
        msg = db.GetMessage(message_name)
        
        # Set signal values
        for signal_name, value in signal_values.items():
            signal = msg.GetSignal(signal_name)
            signal.Value = value
        
        # Send the message
        msg.Send()
        print(f"Sent message: {message_name}")
        
        return True
    
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

# Usage
signals = {
    "EngineSpeed": 3000,
    "EngineTemp": 85,
    "GearPosition": 2
}
send_can_message(app, "EngineData", signals)
```

### Receiving and Reading Messages

```python
def read_message_signals(app, message_name):
    """
    Read all signal values from a message.
    
    Args:
        app: CANoe application object
        message_name: Name of the message
    
    Returns:
        Dictionary of signal_name: value
    """
    try:
        db = app.ActiveDocument.Databases(0)
        msg = db.GetMessage(message_name)
        
        signals = {}
        for i in range(msg.Signals.Count):
            signal = msg.Signals(i)
            signals[signal.Name] = signal.Value
        
        return signals
    
    except Exception as e:
        print(f"Error reading message: {e}")
        return {}

# Usage
engine_signals = read_message_signals(app, "EngineData")
print(f"Engine signals: {engine_signals}")
```

### Working with System Variables

```python
class VariableManager:
    """Manage CANoe system variables."""
    
    def __init__(self, app):
        self.app = app
        self.env = app.Environment
    
    def get_variable(self, var_name):
        """Get variable value."""
        try:
            var = self.env.GetVariable(var_name)
            return var.Value
        except:
            return None
    
    def set_variable(self, var_name, value):
        """Set variable value."""
        try:
            var = self.env.GetVariable(var_name)
            var.Value = value
            return True
        except:
            return False
    
    def list_variables(self):
        """List all available variables."""
        env = self.app.Environment
        return [var.Name for var in env.GetVariables()]
    
    def create_variable(self, var_name, initial_value=0):
        """Create new system variable."""
        try:
            self.set_variable(var_name, initial_value)
            return True
        except:
            return False

# Usage
var_manager = VariableManager(app)
speed = var_manager.get_variable("Speed")
var_manager.set_variable("Speed", 100)
```

---

## Message Handling

### Complete Message Handler Class

```python
class CANoeMessageManager:
    """Manage CAN message operations."""
    
    def __init__(self, app):
        self.app = app
        self.db = app.ActiveDocument.Databases(0)
    
    def get_message(self, message_name):
        """Get message object by name."""
        try:
            return self.db.GetMessage(message_name)
        except:
            return None
    
    def send_message(self, message_name, signal_dict):
        """Send message with signal values."""
        msg = self.get_message(message_name)
        if not msg:
            print(f"Message not found: {message_name}")
            return False
        
        try:
            for signal_name, value in signal_dict.items():
                signal = msg.GetSignal(signal_name)
                signal.Value = value
            
            msg.Send()
            return True
        except Exception as e:
            print(f"Error sending {message_name}: {e}")
            return False
    
    def read_signals(self, message_name):
        """Read all signals from message."""
        msg = self.get_message(message_name)
        if not msg:
            return {}
        
        signals = {}
        try:
            for i in range(msg.Signals.Count):
                signal = msg.Signals(i)
                signals[signal.Name] = signal.Value
        except Exception as e:
            print(f"Error reading signals: {e}")
        
        return signals
    
    def read_signal(self, message_name, signal_name):
        """Read single signal value."""
        msg = self.get_message(message_name)
        if not msg:
            return None
        
        try:
            signal = msg.GetSignal(signal_name)
            return signal.Value
        except:
            return None
    
    def list_messages(self):
        """List all messages in database."""
        messages = []
        try:
            for i in range(self.db.Messages.Count):
                msg = self.db.Messages(i)
                messages.append(msg.Name)
        except:
            pass
        
        return messages
    
    def message_info(self, message_name):
        """Get detailed message information."""
        msg = self.get_message(message_name)
        if not msg:
            return None
        
        info = {
            "Name": msg.Name,
            "ID": msg.ID,
            "Length": msg.Length,
            "Signals": {}
        }
        
        try:
            for i in range(msg.Signals.Count):
                signal = msg.Signals(i)
                info["Signals"][signal.Name] = {
                    "Value": signal.Value,
                    "Min": signal.Min if hasattr(signal, 'Min') else None,
                    "Max": signal.Max if hasattr(signal, 'Max') else None
                }
        except:
            pass
        
        return info

# Usage
msg_manager = CANoeMessageManager(app)

# Send message
msg_manager.send_message("EngineData", {"EngineSpeed": 3000, "EngineTemp": 85})

# Read signals
signals = msg_manager.read_signals("EngineData")

# Get specific signal
rpm = msg_manager.read_signal("EngineData", "EngineSpeed")

# List all messages
all_messages = msg_manager.list_messages()
```

---

## Advanced Automation

### Measurement Control Class

```python
class MeasurementController:
    """Control CANoe measurements."""
    
    def __init__(self, app):
        self.app = app
        self.doc = app.ActiveDocument
        self.measurement = self.doc.Measurement
    
    def is_running(self):
        """Check if measurement is running."""
        return self.measurement.Running
    
    def start(self):
        """Start measurement."""
        if self.is_running():
            print("Measurement already running")
            return False
        
        try:
            self.measurement.Start()
            print("Measurement started")
            return True
        except Exception as e:
            print(f"Error starting measurement: {e}")
            return False
    
    def stop(self):
        """Stop measurement."""
        if not self.is_running():
            print("Measurement not running")
            return False
        
        try:
            self.measurement.Stop()
            print("Measurement stopped")
            return True
        except Exception as e:
            print(f"Error stopping measurement: {e}")
            return False
    
    def run_for_duration(self, seconds):
        """Run measurement for specified duration."""
        if not self.start():
            return False
        
        print(f"Running for {seconds} seconds...")
        time.sleep(seconds)
        
        return self.stop()
    
    def wait_for_completion(self, timeout=300):
        """Wait for measurement to complete."""
        start_time = time.time()
        
        while self.is_running():
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for measurement (>{timeout}s)")
                return False
            
            time.sleep(1)
        
        return True
    
    def get_measurement_time(self):
        """Get current measurement time."""
        try:
            # Time in seconds since measurement start
            return self.measurement.ElapsedTime
        except:
            return 0
    
    def save_measurement(self, filename):
        """Save measurement results."""
        try:
            # Implementation depends on CANoe version
            extension = ".trc" if filename.endswith(".trc") else ".asc"
            print(f"Saving measurement to {filename}")
            return True
        except Exception as e:
            print(f"Error saving measurement: {e}")
            return False

# Usage
ctrl = MeasurementController(app)
ctrl.start()
time.sleep(10)
ctrl.stop()
```

### Test Automation Framework

```python
class CANoeTestFramework:
    """Framework for automated CAN testing."""
    
    def __init__(self, app):
        self.app = app
        self.msg_manager = CANoeMessageManager(app)
        self.measurement = MeasurementController(app)
        self.test_results = []
    
    def run_test(self, test_name, test_func):
        """Run a single test."""
        print(f"\n{'='*50}")
        print(f"Running test: {test_name}")
        print(f"{'='*50}")
        
        try:
            test_func()
            self.test_results.append({
                "name": test_name,
                "status": "PASS",
                "error": None
            })
            print(f"✓ {test_name} PASSED")
        except AssertionError as e:
            self.test_results.append({
                "name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
            print(f"✗ {test_name} FAILED: {e}")
        except Exception as e:
            self.test_results.append({
                "name": test_name,
                "status": "ERROR",
                "error": str(e)
            })
            print(f"✗ {test_name} ERROR: {e}")
    
    def assert_signal_value(self, message, signal, expected_value, tolerance=0):
        """Assert signal has expected value."""
        actual = self.msg_manager.read_signal(message, signal)
        
        if tolerance > 0:
            assert abs(actual - expected_value) <= tolerance, \
                f"{signal} = {actual}, expected {expected_value} ±{tolerance}"
        else:
            assert actual == expected_value, \
                f"{signal} = {actual}, expected {expected_value}"
    
    def assert_message_sent(self, message):
        """Assert message was sent."""
        signals = self.msg_manager.read_signals(message)
        assert len(signals) > 0, f"Message {message} not found"
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*50}")
        print("TEST SUMMARY")
        print(f"{'='*50}")
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        errors = sum(1 for r in self.test_results if r["status"] == "ERROR")
        total = len(self.test_results)
        
        for result in self.test_results:
            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            print(f"{status_symbol} {result['name']}: {result['status']}")
            if result["error"]:
                print(f"  Error: {result['error']}")
        
        print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
        
        return passed == total

# Usage
framework = CANoeTestFramework(app)

def test_engine_speed():
    framework.assert_signal_value("EngineData", "EngineSpeed", 3000, tolerance=50)

def test_engine_temp():
    framework.assert_signal_value("EngineData", "EngineTemp", 85, tolerance=5)

framework.run_test("Engine Speed", test_engine_speed)
framework.run_test("Engine Temperature", test_engine_temp)
framework.print_summary()
```

### Data Logging and Analysis

```python
import csv
from datetime import datetime

class DataLogger:
    """Log signal data from CANoe measurements."""
    
    def __init__(self, msg_manager, log_file):
        self.msg_manager = msg_manager
        self.log_file = log_file
        self.data = []
        self.start_time = None
    
    def start_logging(self, messages, interval=0.1):
        """Start logging messages at specified interval."""
        self.start_time = time.time()
        self.data = []
        
        print(f"Logging data to {self.log_file}")
        
        try:
            while True:
                elapsed = time.time() - self.start_time
                record = {"timestamp": elapsed}
                
                for msg_name in messages:
                    signals = self.msg_manager.read_signals(msg_name)
                    for signal_name, value in signals.items():
                        key = f"{msg_name}.{signal_name}"
                        record[key] = value
                
                self.data.append(record)
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("Logging stopped")
            self.save_to_csv()
    
    def save_to_csv(self):
        """Save logged data to CSV file."""
        if not self.data:
            print("No data to save")
            return
        
        try:
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
            
            print(f"Data saved to {self.log_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_statistics(self, signal_key):
        """Get min, max, average for a signal."""
        values = [r[signal_key] for r in self.data if signal_key in r]
        
        if not values:
            return None
        
        return {
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "count": len(values)
        }

# Usage (in a separate thread typically)
logger = DataLogger(msg_manager, "measurement.csv")
logger.start_logging(["EngineData", "TransmissionData"], interval=0.1)

# Get statistics
stats = logger.get_statistics("EngineData.EngineSpeed")
print(f"Engine Speed: {stats}")
```

---

## Best Practices

### 1. Error Handling

```python
class CANoeError(Exception):
    """Base exception for CANoe operations."""
    pass

class CANoeConnectionError(CANoeError):
    """Failed to connect to CANoe."""
    pass

def connect_to_canoe_safe():
    """Connect with proper error handling."""
    try:
        from win32com.client import GetObject
        app = GetObject(None, "CANoe.Application")
        
        if not app.Visible:
            app.Visible = True
        
        return app
    
    except ImportError:
        raise CANoeConnectionError("pywin32 not installed. Run: pip install pywin32")
    except Exception as e:
        raise CANoeConnectionError(f"Failed to connect to CANoe: {e}")

# Usage
try:
    app = connect_to_canoe_safe()
except CANoeConnectionError as e:
    print(f"Connection error: {e}")
    sys.exit(1)
```

### 2. Context Managers

```python
from contextlib import contextmanager

@contextmanager
def canoe_session(config_file):
    """Context manager for CANoe session."""
    try:
        app = GetObject(None, "CANoe.Application")
        doc = app.Documents.Open(config_file)
        measurement = doc.Measurement
        
        yield app, doc, measurement
    
    finally:
        # Ensure measurement is stopped
        try:
            if measurement.Running:
                measurement.Stop()
        except:
            pass

# Usage
with canoe_session(r"C:\config.cfg") as (app, doc, measurement):
    measurement.Start()
    time.sleep(10)
    measurement.Stop()
```

### 3. Retry Logic

```python
import functools
import time

def retry(max_attempts=3, delay=1):
    """Decorator for retry logic."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=2)
def send_critical_message(msg_manager, msg_name, signals):
    """Send message with retry."""
    return msg_manager.send_message(msg_name, signals)

# Usage
send_critical_message(msg_manager, "EngineData", {"EngineSpeed": 3000})
```

### 4. Configuration Management

```python
import json
import os

class CANoeConfig:
    """Manage CANoe project configuration."""
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load()
    
    def load(self):
        """Load configuration from JSON."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._default_config()
    
    def _default_config(self):
        """Default configuration structure."""
        return {
            "project_path": "",
            "config_file": "",
            "database_files": [],
            "test_messages": {},
            "log_file": "measurement.csv",
            "timeout": 300
        }
    
    def save(self):
        """Save configuration to JSON."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value."""
        self.config[key] = value
        self.save()

# Usage
config = CANoeConfig("canoe_config.json")
project_path = config.get("project_path")
config.set("timeout", 600)
```

### 5. Logging

```python
import logging

def setup_logging(log_file="canoe_automation.log"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Usage
logger.info("Starting CANoe automation")
logger.debug("Message details: ...")
logger.warning("Low signal value")
logger.error("Failed to send message")
```

---

## Complete Examples

### Example 1: Simple Message Test

```python
#!/usr/bin/env python3
"""
Simple CANoe Message Test
Send a message and verify signal values
"""

import sys
import time
from win32com.client import GetObject

class SimpleMessageTest:
    def __init__(self, config_file):
        self.config_file = config_file
        self.app = None
        self.msg_manager = None
    
    def setup(self):
        """Setup test environment."""
        try:
            # Connect to CANoe
            self.app = GetObject(None, "CANoe.Application")
            print(f"Connected to CANoe {self.app.Version}")
            
            # Load configuration
            print(f"Loading configuration: {self.config_file}")
            doc = self.app.Documents.Open(self.config_file)
            print(f"Configuration loaded: {doc.Name}")
            
            # Initialize message manager
            self.msg_manager = CANoeMessageManager(self.app)
            
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def run_test(self):
        """Run the test."""
        print("\n" + "="*50)
        print("Running Message Test")
        print("="*50)
        
        # Start measurement
        measurement = self.app.ActiveDocument.Measurement
        measurement.Start()
        print("Measurement started")
        
        # Send message
        print("\nSending EngineData message...")
        self.msg_manager.send_message("EngineData", {
            "EngineSpeed": 3000,
            "EngineTemp": 85,
            "OilPressure": 4.5
        })
        
        # Wait a bit
        time.sleep(2)
        
        # Read signals
        print("\nReading signal values...")
        signals = self.msg_manager.read_signals("EngineData")
        
        for signal_name, value in signals.items():
            print(f"  {signal_name}: {value}")
        
        # Stop measurement
        time.sleep(2)
        measurement.Stop()
        print("\nMeasurement stopped")
        
        return True
    
    def cleanup(self):
        """Cleanup after test."""
        try:
            if self.app:
                # Don't close document, just disconnect
                pass
            print("Cleanup completed")
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    config_file = r"C:\CANoe_Projects\MyProject\myconfig.cfg"
    
    test = SimpleMessageTest(config_file)
    
    if not test.setup():
        sys.exit(1)
    
    try:
        test.run_test()
    finally:
        test.cleanup()

if __name__ == "__main__":
    main()
```

### Example 2: Automated Test Suite

```python
#!/usr/bin/env python3
"""
Automated Test Suite for CAN Network
"""

import sys
import time
import json
from datetime import datetime
from win32com.client import GetObject

class CANoeTestSuite:
    def __init__(self, config_file):
        self.config_file = config_file
        self.app = None
        self.framework = None
        self.results = []
    
    def setup(self):
        """Setup test environment."""
        try:
            self.app = GetObject(None, "CANoe.Application")
            print(f"Connected to CANoe {self.app.Version}")
            
            doc = self.app.Documents.Open(self.config_file)
            print(f"Configuration: {doc.Name}")
            
            self.framework = CANoeTestFramework(self.app)
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def test_engine_parameters(self):
        """Test engine parameter ranges."""
        msg_manager = CANoeMessageManager(self.app)
        
        # Test engine speed
        msg_manager.send_message("EngineData", {
            "EngineSpeed": 1500,
            "EngineTemp": 80
        })
        time.sleep(1)
        
        self.framework.assert_signal_value(
            "EngineData", "EngineSpeed", 1500, tolerance=50
        )
    
    def test_transmission_gear(self):
        """Test transmission gear selection."""
        msg_manager = CANoeMessageManager(self.app)
        
        for gear in [0, 1, 2, 3, 4, 5]:
            msg_manager.send_message("TransmissionData", {
                "GearPosition": gear
            })
            time.sleep(0.5)
            
            self.framework.assert_signal_value(
                "TransmissionData", "GearPosition", gear
            )
    
    def test_brake_system(self):
        """Test brake system operation."""
        msg_manager = CANoeMessageManager(self.app)
        
        self.framework.assert_signal_value(
            "BrakeData", "BrakePressure", 0  # Initially zero
        )
        
        msg_manager.send_message("BrakeData", {
            "BrakePressure": 5.0
        })
        time.sleep(1)
        
        self.framework.assert_signal_value(
            "BrakeData", "BrakePressure", 5.0, tolerance=0.5
        )
    
    def run_all_tests(self):
        """Run all tests."""
        measurement = self.app.ActiveDocument.Measurement
        measurement.Start()
        
        try:
            self.framework.run_test("Engine Parameters", self.test_engine_parameters)
            self.framework.run_test("Transmission Gear", self.test_transmission_gear)
            self.framework.run_test("Brake System", self.test_brake_system)
        
        finally:
            measurement.Stop()
        
        return self.framework.print_summary()
    
    def save_results(self, filename):
        """Save test results to JSON."""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "config_file": self.config_file,
            "tests": self.framework.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"Results saved to {filename}")

def main():
    config_file = r"C:\CANoe_Projects\MyProject\myconfig.cfg"
    
    test_suite = CANoeTestSuite(config_file)
    
    if not test_suite.setup():
        sys.exit(1)
    
    try:
        success = test_suite.run_all_tests()
        test_suite.save_results("test_results.json")
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Example 3: Real-Time Data Monitoring

```python
#!/usr/bin/env python3
"""
Real-Time Data Monitoring
Monitor and log CAN bus signals in real-time
"""

import sys
import time
import threading
from datetime import datetime
from win32com.client import GetObject

class RealtimeMonitor:
    def __init__(self, config_file, update_interval=0.1):
        self.config_file = config_file
        self.update_interval = update_interval
        self.app = None
        self.msg_manager = None
        self.running = False
        self.data = {}
    
    def setup(self):
        """Setup monitoring environment."""
        try:
            self.app = GetObject(None, "CANoe.Application")
            doc = self.app.Documents.Open(self.config_file)
            self.msg_manager = CANoeMessageManager(self.app)
            
            # Start measurement
            measurement = self.app.ActiveDocument.Measurement
            measurement.Start()
            
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def monitor_signals(self, messages):
        """Monitor signals from specified messages."""
        self.running = True
        
        while self.running:
            try:
                timestamp = datetime.now()
                self.data[timestamp] = {}
                
                for msg_name in messages:
                    signals = self.msg_manager.read_signals(msg_name)
                    self.data[timestamp][msg_name] = signals
                
                self.display_data(timestamp, messages)
                time.sleep(self.update_interval)
            
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)
    
    def display_data(self, timestamp, messages):
        """Display current signal values."""
        # Clear screen (Unix-like systems)
        print("\033[2J\033[H")
        
        print(f"Real-Time Monitor - {timestamp.strftime('%H:%M:%S.%f')[:-3]}")
        print("=" * 60)
        
        for msg_name in messages:
            if msg_name in self.data[timestamp]:
                print(f"\n{msg_name}:")
                signals = self.data[timestamp][msg_name]
                
                for signal_name, value in signals.items():
                    print(f"  {signal_name:<30} {value:>10}")
    
    def start_monitoring(self, messages):
        """Start monitoring in a separate thread."""
        monitor_thread = threading.Thread(
            target=self.monitor_signals,
            args=(messages,),
            daemon=True
        )
        monitor_thread.start()
        
        try:
            monitor_thread.join()
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            self.running = False
    
    def cleanup(self):
        """Stop measurement and cleanup."""
        self.running = False
        
        try:
            measurement = self.app.ActiveDocument.Measurement
            if measurement.Running:
                measurement.Stop()
        except:
            pass

def main():
    config_file = r"C:\CANoe_Projects\MyProject\myconfig.cfg"
    monitor = RealtimeMonitor(config_file, update_interval=0.1)
    
    if not monitor.setup():
        sys.exit(1)
    
    messages = ["EngineData", "TransmissionData", "BrakeData"]
    
    try:
        monitor.start_monitoring(messages)
    finally:
        monitor.cleanup()

if __name__ == "__main__":
    main()
```

### Example 4: Stress Testing

```python
#!/usr/bin/env python3
"""
CAN Bus Stress Testing
Send high-frequency messages and measure response
"""

import sys
import time
import threading
from win32com.client import GetObject

class StressTest:
    def __init__(self, config_file):
        self.config_file = config_file
        self.app = None
        self.msg_manager = None
        self.messages_sent = 0
        self.errors = 0
    
    def setup(self):
        """Setup stress test environment."""
        try:
            self.app = GetObject(None, "CANoe.Application")
            doc = self.app.Documents.Open(self.config_file)
            self.msg_manager = CANoeMessageManager(self.app)
            
            measurement = self.app.ActiveDocument.Measurement
            measurement.Start()
            
            return True
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def send_messages_continuous(self, message_name, values, duration=30):
        """Continuously send messages for specified duration."""
        start_time = time.time()
        
        print(f"\nStress Testing: {message_name}")
        print(f"Duration: {duration} seconds")
        print("=" * 50)
        
        while time.time() - start_time < duration:
            try:
                # Rotate through different values or modify them
                for value_set in values:
                    self.msg_manager.send_message(message_name, value_set)
                    self.messages_sent += 1
                    
                    # Print progress every 100 messages
                    if self.messages_sent % 100 == 0:
                        elapsed = time.time() - start_time
                        rate = self.messages_sent / elapsed
                        print(f"Sent {self.messages_sent} messages "
                              f"({rate:.1f} msg/sec)")
                    
                    time.sleep(0.01)  # ~100 Hz
            
            except Exception as e:
                self.errors += 1
                print(f"Error: {e}")
        
        elapsed = time.time() - start_time
        rate = self.messages_sent / elapsed
        
        print(f"\nResults:")
        print(f"  Total messages: {self.messages_sent}")
        print(f"  Errors: {self.errors}")
        print(f"  Average rate: {rate:.1f} msg/sec")
        print(f"  Duration: {elapsed:.1f} seconds")
        
        return self.errors == 0
    
    def cleanup(self):
        """Stop measurement and cleanup."""
        try:
            measurement = self.app.ActiveDocument.Measurement
            if measurement.Running:
                measurement.Stop()
        except:
            pass

def main():
    config_file = r"C:\CANoe_Projects\MyProject\myconfig.cfg"
    test = StressTest(config_file)
    
    if not test.setup():
        sys.exit(1)
    
    try:
        # Define test values
        engine_values = [
            {"EngineSpeed": 1000, "EngineTemp": 80},
            {"EngineSpeed": 2000, "EngineTemp": 82},
            {"EngineSpeed": 3000, "EngineTemp": 85},
            {"EngineSpeed": 4000, "EngineTemp": 88},
        ]
        
        # Run stress test
        success = test.send_messages_continuous("EngineData", engine_values, duration=60)
        
        sys.exit(0 if success else 1)
    
    finally:
        test.cleanup()

if __name__ == "__main__":
    main()
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "CANoe is not running"

```python
# Problem: GetObject fails because CANoe isn't running
# Solution: Launch CANoe first or create new instance

from win32com.client import GetObject, Dispatch

try:
    app = GetObject(None, "CANoe.Application")
except:
    print("CANoe not running, creating new instance...")
    app = Dispatch("CANoe.Application")
    app.Visible = True
```

#### Issue 2: "pywin32 not installed"

```bash
# Install packages
pip install pywin32
pip install comtypes

# Register COM
python -m pywin32_postinstall -install
```

#### Issue 3: "Message not found"

```python
# Debug: list all available messages
db = app.ActiveDocument.Databases(0)
for i in range(db.Messages.Count):
    msg = db.Messages(i)
    print(f"Message: {msg.Name} (ID: 0x{msg.ID:03X})")
```

#### Issue 4: "Signal value not updating"

```python
# Problem: Reading signal immediately after sending
# Solution: Add delay for update propagation

msg_manager.send_message("EngineData", {"EngineSpeed": 3000})
time.sleep(0.5)  # Wait for update
value = msg_manager.read_signal("EngineData", "EngineSpeed")
```

#### Issue 5: "Measurement won't stop"

```python
# Force stop measurement
measurement = app.ActiveDocument.Measurement
measurement.Stop()
time.sleep(1)  # Wait for stop

# Check status
print(f"Running: {measurement.Running}")
```

### Debugging Tips

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Debug COM interface
def debug_canoe_structure(app):
    """Print CANoe object structure."""
    doc = app.ActiveDocument
    db = doc.Databases(0)
    
    print("Documents:", app.Documents.Count)
    print("Databases:", doc.Databases.Count)
    print("Messages:", db.Messages.Count)
    
    for i in range(min(5, db.Messages.Count)):
        msg = db.Messages(i)
        print(f"\nMessage {i}: {msg.Name}")
        print(f"  ID: 0x{msg.ID:03X}")
        print(f"  DLC: {msg.Length}")
        print(f"  Signals: {msg.Signals.Count}")
        
        for j in range(min(3, msg.Signals.Count)):
            sig = msg.Signals(j)
            print(f"    - {sig.Name}")

debug_canoe_structure(app)
```

---

## Performance Optimization

### Minimize COM Calls

```python
# ❌ Inefficient - multiple COM calls
for i in range(1000):
    value = msg_manager.read_signal("EngineData", "EngineSpeed")

# ✅ Efficient - batch reads
signals = msg_manager.read_signals("EngineData")
speed = signals["EngineSpeed"]
```

### Use Threading for Long Operations

```python
import threading

def perform_long_test():
    # Time-consuming test"""
    time.sleep(10)

# Run in background
test_thread = threading.Thread(target=perform_long_test, daemon=True)
test_thread.start()

# Do other things while test runs
time.sleep(2)
print("Test is running in background...")

test_thread.join()
```

### Cache Database References

```python
# ❌ Inefficient - database lookup each time
msg1 = app.ActiveDocument.Databases(0).GetMessage("EngineData")
msg2 = app.ActiveDocument.Databases(0).GetMessage("TransmissionData")

# ✅ Efficient - cache database
db = app.ActiveDocument.Databases(0)
msg1 = db.GetMessage("EngineData")
msg2 = db.GetMessage("TransmissionData")
```

---

## Conclusion

You've learned how to automate CANoe with Python! Key takeaways:

1. **COM Interface** - CANoe's bridge to external applications
2. **Message Manager** - Send and receive CAN messages
3. **Test Framework** - Create automated test suites
4. **Data Logging** - Capture and analyze measurements
5. **Best Practices** - Robust, maintainable code

### Next Steps

1. Start with simple message tests
2. Build test frameworks for your protocols
3. Integrate with CI/CD pipelines
4. Analyze measurement data with Pandas
5. Create web dashboards for results

Happy automating! 🚗⚙️

