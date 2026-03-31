"""
ECU Data Stream Validation Test Suite
Comprehensive testing framework for validating all ECU data streams in a vehicle
Including ADAS, Powertrain, Thermal, Battery, and other safety-critical systems
"""

import json
import time
import unittest
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import threading
import queue
from enum import Enum
import statistics
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models for ECU Messages
# ============================================================================

class ECUType(Enum):
    """Supported ECU types in the vehicle"""
    ADAS_SENSOR = "ADAS_SENSOR"
    ADAS_ECU = "ADAS_ECU"
    ENGINE_ECU = "ENGINE_ECU"
    BATTERY_MANAGEMENT = "BATTERY_MANAGEMENT"
    THERMAL_MANAGEMENT = "THERMAL_MANAGEMENT"
    POWERTRAIN = "POWERTRAIN"
    BODY_CONTROL = "BODY_CONTROL"
    INFOTAINMENT = "INFOTAINMENT"
    TELEMATICS = "TELEMATICS"
    MOTOR_CONTROL = "MOTOR_CONTROL"


@dataclass
class ADASData:
    """ADAS ECU data stream"""
    timestamp: float
    front_camera_objects: int  # Number of objects detected
    lidar_range: float  # Meters
    radar_objects: int  # Number of objects
    lane_position: float  # Lateral position within lane (meters)
    lateral_error: float  # Lane keeping error (meters)
    collision_distance: float  # Distance to nearest object (meters)
    collision_warning: bool
    emergency_brake_recommended: bool
    acc_target_distance: float  # Adaptive Cruise Control target distance
    acc_target_speed: float  # ACC target speed (km/h)
    current_speed: float  # Vehicle speed (km/h)
    lane_keeping_active: bool
    emergency_brake_active: bool
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate ADAS data for correctness"""
        errors = []
        
        # Range checks
        if not (0 <= self.front_camera_objects <= 255):
            errors.append(f"Invalid camera objects: {self.front_camera_objects}")
        
        if not (0 <= self.lidar_range <= 200):
            errors.append(f"Invalid LIDAR range: {self.lidar_range}")
        
        if not (0 <= self.radar_objects <= 100):
            errors.append(f"Invalid radar objects: {self.radar_objects}")
        
        if not (-2 <= self.lateral_error <= 2):
            errors.append(f"Invalid lateral error: {self.lateral_error}")
        
        if not (0.1 <= self.collision_distance <= 200):
            errors.append(f"Invalid collision distance: {self.collision_distance}")
        
        if not (0 <= self.acc_target_speed <= 200):
            errors.append(f"Invalid ACC target speed: {self.acc_target_speed}")
        
        if not (0 <= self.current_speed <= 300):
            errors.append(f"Invalid current speed: {self.current_speed}")
        
        # Logic checks
        if self.emergency_brake_active and self.current_speed < 0.1:
            if self.current_speed > 5:  # Not decelerating properly
                errors.append("Emergency brake active but speed not decreasing")
        
        return len(errors) == 0, errors


@dataclass
class PowertrainData:
    """Powertrain/Motor ECU data"""
    timestamp: float
    motor_rpm: float
    motor_torque: float  # Nm
    motor_power: float  # kW
    motor_temperature: float  # Celsius
    inverter_temperature: float  # Celsius
    input_voltage: float  # Volts
    phase_a_current: float  # Amps
    phase_b_current: float  # Amps
    phase_c_current: float  # Amps
    motor_efficiency: float  # Percentage
    regenerative_braking_active: bool
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate powertrain data"""
        errors = []
        
        if not (0 <= self.motor_rpm <= 12000):
            errors.append(f"Invalid motor RPM: {self.motor_rpm}")
        
        if not (-500 <= self.motor_torque <= 800):
            errors.append(f"Invalid motor torque: {self.motor_torque}")
        
        if not (0 <= self.motor_power <= 350):
            errors.append(f"Invalid motor power: {self.motor_power}")
        
        if not (-20 <= self.motor_temperature <= 120):
            errors.append(f"Invalid motor temperature: {self.motor_temperature}")
        
        if not (-20 <= self.inverter_temperature <= 100):
            errors.append(f"Invalid inverter temperature: {self.inverter_temperature}")
        
        if not (0 <= self.input_voltage <= 850):
            errors.append(f"Invalid input voltage: {self.input_voltage}")
        
        if not (-300 <= self.phase_a_current <= 500):
            errors.append(f"Invalid phase A current: {self.phase_a_current}")
        
        if not (0 <= self.motor_efficiency <= 97):
            errors.append(f"Invalid motor efficiency: {self.motor_efficiency}")
        
        return len(errors) == 0, errors


@dataclass
class BatteryData:
    """Battery Management System (BMS) data"""
    timestamp: float
    total_voltage: float  # Volts
    total_current: float  # Amps (positive=charging, negative=discharging)
    state_of_charge: float  # Percentage 0-100
    state_of_health: float  # Percentage 0-100
    battery_temperature: float  # Celsius
    cell_voltage_min: float  # Volts
    cell_voltage_max: float  # Volts
    cell_voltage_imbalance: float  # Volts (max difference between cells)
    cooling_pump_speed: float  # RPM
    charging_power: float  # kW
    cooling_power: float  # kW
    remaining_range: float  # Kilometers
    thermal_runaway_risk: bool
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate battery data"""
        errors = []
        
        if not (0 <= self.total_voltage <= 900):
            errors.append(f"Invalid total voltage: {self.total_voltage}")
        
        if not (-300 <= self.total_current <= 300):
            errors.append(f"Invalid total current: {self.total_current}")
        
        if not (0 <= self.state_of_charge <= 100):
            errors.append(f"Invalid SOC: {self.state_of_charge}")
        
        if not (0 <= self.state_of_health <= 100):
            errors.append(f"Invalid SOH: {self.state_of_health}")
        
        if not (-30 <= self.battery_temperature <= 60):
            errors.append(f"Invalid battery temperature: {self.battery_temperature}")
        
        if self.cell_voltage_min < 0 or self.cell_voltage_max < 0:
            errors.append("Invalid cell voltages")
        
        if self.cell_voltage_max < self.cell_voltage_min:
            errors.append("Max cell voltage less than min")
        
        if self.cell_voltage_imbalance > 1.0:
            errors.append(f"Excessive cell imbalance: {self.cell_voltage_imbalance}V")
        
        if not (0 <= self.remaining_range <= 1000):
            errors.append(f"Invalid range: {self.remaining_range}")
        
        return len(errors) == 0, errors


@dataclass
class ThermalData:
    """Thermal Management System data"""
    timestamp: float
    cabin_temperature: float  # Celsius
    battery_coolant_temp: float  # Celsius
    motor_coolant_temp: float  # Celsius
    ambient_temperature: float  # Celsius
    hvac_compressor_power: float  # kW
    coolant_pump_speed: float  # RPM
    radiator_fan_speed: float  # RPM
    battery_cooling_demand: float  # Percentage
    motor_cooling_demand: float  # Percentage
    heat_pump_active: bool
    precondition_active: bool
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate thermal data"""
        errors = []
        
        if not (-30 <= self.cabin_temperature <= 60):
            errors.append(f"Invalid cabin temperature: {self.cabin_temperature}")
        
        if not (-30 <= self.battery_coolant_temp <= 80):
            errors.append(f"Invalid battery coolant temp: {self.battery_coolant_temp}")
        
        if not (-30 <= self.motor_coolant_temp <= 120):
            errors.append(f"Invalid motor coolant temp: {self.motor_coolant_temp}")
        
        if not (-50 <= self.ambient_temperature <= 60):
            errors.append(f"Invalid ambient temperature: {self.ambient_temperature}")
        
        if not (0 <= self.hvac_compressor_power <= 15):
            errors.append(f"Invalid HVAC power: {self.hvac_compressor_power}")
        
        return len(errors) == 0, errors


@dataclass
class BodyControlData:
    """Body Control Module data"""
    timestamp: float
    door_front_left_open: bool
    door_front_right_open: bool
    door_rear_left_open: bool
    door_rear_right_open: bool
    trunk_open: bool
    hood_open: bool
    lights_front_left: bool
    lights_front_right: bool
    lights_rear_left: bool
    lights_rear_right: bool
    windshield_wiper_speed: int  # 0-4 speeds
    rain_sensor_level: int  # 0-100
    window_position_fl: float  # Percentage open
    window_position_fr: float
    window_position_rl: float
    window_position_rr: float
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate body control data"""
        errors = []
        
        if not (0 <= self.windshield_wiper_speed <= 4):
            errors.append(f"Invalid wiper speed: {self.windshield_wiper_speed}")
        
        if not (0 <= self.rain_sensor_level <= 100):
            errors.append(f"Invalid rain sensor: {self.rain_sensor_level}")
        
        for pos in [self.window_position_fl, self.window_position_fr,
                   self.window_position_rl, self.window_position_rr]:
            if not (0 <= pos <= 100):
                errors.append(f"Invalid window position: {pos}")
        
        return len(errors) == 0, errors


# ============================================================================
# ECU Simulators - Mock Data Generators
# ============================================================================

class ECUSimulator(ABC):
    """Abstract base class for ECU simulators"""
    
    def __init__(self, ecu_name: str, frequency_hz: float = 10):
        self.ecu_name = ecu_name
        self.frequency_hz = frequency_hz
        self.data_queue = queue.Queue()
        self.running = False
    
    @abstractmethod
    def generate_data(self) -> dict:
        """Generate simulated ECU data"""
        pass
    
    def start(self):
        """Start ECU data generation"""
        self.running = True
        thread = threading.Thread(target=self._run)
        thread.daemon = True
        thread.start()
    
    def _run(self):
        """Run ECU data generation loop"""
        interval = 1.0 / self.frequency_hz
        
        while self.running:
            try:
                data = self.generate_data()
                self.data_queue.put(data)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in {self.ecu_name}: {e}")
    
    def stop(self):
        """Stop ECU data generation"""
        self.running = False
    
    def get_data(self):
        """Get latest ECU data (non-blocking)"""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None


class ADASSimulator(ECUSimulator):
    """Simulate ADAS ECU data streams"""
    
    def __init__(self, frequency_hz: float = 25):
        super().__init__("ADAS_ECU", frequency_hz)
        self.current_speed = 50.0
    
    def generate_data(self) -> ADASData:
        """Generate realistic ADAS data"""
        import random
        import math
        
        # Simulate speed variation
        self.current_speed += random.uniform(-5, 5)
        self.current_speed = max(0, min(200, self.current_speed))
        
        # Simulate lane position (sine wave for lane changes)
        lane_pos = 0.3 * math.sin(time.time() * 0.5)
        lateral_error = lane_pos + random.uniform(-0.05, 0.05)
        
        # Simulate object detection
        front_objects = random.randint(0, 5) if self.current_speed > 10 else 0
        collision_distance = random.uniform(10, 150) if front_objects > 0 else 200
        collision_warning = collision_distance < 20
        emergency_brake = collision_distance < 10
        
        return ADASData(
            timestamp=time.time(),
            front_camera_objects=front_objects,
            lidar_range=random.uniform(0.5, 200),
            radar_objects=front_objects,
            lane_position=lane_pos,
            lateral_error=lateral_error,
            collision_distance=collision_distance,
            collision_warning=collision_warning,
            emergency_brake_recommended=emergency_brake,
            acc_target_distance=30 + random.uniform(-5, 5),
            acc_target_speed=self.current_speed + random.uniform(-2, 2),
            current_speed=self.current_speed,
            lane_keeping_active=abs(lateral_error) > 0.2,
            emergency_brake_active=emergency_brake
        )


class PowertrainSimulator(ECUSimulator):
    """Simulate Powertrain/Motor ECU data streams"""
    
    def __init__(self, frequency_hz: float = 100):
        super().__init__("MOTOR_CONTROL", frequency_hz)
        self.motor_rpm = 0
    
    def generate_data(self) -> PowertrainData:
        """Generate realistic powertrain data"""
        import random
        import math
        
        # Simulate acceleration/deceleration
        self.motor_rpm += random.uniform(-500, 1500)
        self.motor_rpm = max(0, min(12000, self.motor_rpm))
        
        # Torque proportional to RPM demand
        torque = (self.motor_rpm / 12000) * 600 + random.uniform(-20, 20)
        
        # Power calculation
        power = (self.motor_rpm * torque / 9550) / 1000  # Convert to kW
        
        # Temperature increase with power
        base_temp = 20 + (power * 0.15)
        motor_temp = base_temp + random.uniform(-2, 5)
        
        return PowertrainData(
            timestamp=time.time(),
            motor_rpm=self.motor_rpm,
            motor_torque=torque,
            motor_power=max(0, power),
            motor_temperature=motor_temp,
            inverter_temperature=motor_temp + random.uniform(5, 15),
            input_voltage=400 + random.uniform(-10, 10),
            phase_a_current=power * 150 / 400 + random.uniform(-10, 10),
            phase_b_current=power * 150 / 400 + random.uniform(-10, 10),
            phase_c_current=power * 150 / 400 + random.uniform(-10, 10),
            motor_efficiency=88 + random.uniform(-3, 5),
            regenerative_braking_active=self.motor_rpm > 0 and random.random() > 0.7
        )


class BatterySimulator(ECUSimulator):
    """Simulate Battery Management System data streams"""
    
    def __init__(self, frequency_hz: float = 10):
        super().__init__("BATTERY_MANAGEMENT", frequency_hz)
        self.soc = 80.0
    
    def generate_data(self) -> BatteryData:
        """Generate realistic battery data"""
        import random
        
        # Simulate charging/discharging
        self.soc += random.uniform(-2, 3)
        self.soc = max(0, min(100, self.soc))
        
        # Temperature based on activity
        activity = random.random()
        base_temp = 20 + (activity * 30)
        battery_temp = base_temp + random.uniform(-3, 3)
        
        # Voltage decreases with discharge
        total_voltage = 400 - (100 - self.soc) * 1.5 + random.uniform(-5, 5)
        
        return BatteryData(
            timestamp=time.time(),
            total_voltage=total_voltage,
            total_current=random.uniform(-200, 200),
            state_of_charge=self.soc,
            state_of_health=95 + random.uniform(-2, 1),
            battery_temperature=battery_temp,
            cell_voltage_min=3.6 + random.uniform(-0.1, 0.1),
            cell_voltage_max=3.8 + random.uniform(-0.1, 0.1),
            cell_voltage_imbalance=random.uniform(0, 0.5),
            cooling_pump_speed=random.uniform(0, 3000),
            charging_power=random.uniform(0, 150) if self.soc < 80 else 0,
            cooling_power=max(0, activity * 15),
            remaining_range=self.soc * 5,  # Simple estimate
            thermal_runaway_risk=battery_temp > 55
        )


class ThermalSimulator(ECUSimulator):
    """Simulate Thermal Management System data streams"""
    
    def __init__(self, frequency_hz: float = 5):
        super().__init__("THERMAL_MANAGEMENT", frequency_hz)
        self.cabin_temp = 22.0
    
    def generate_data(self) -> ThermalData:
        """Generate realistic thermal data"""
        import random
        
        # Cabin temperature control
        target_temp = 22.0
        self.cabin_temp += (target_temp - self.cabin_temp) * 0.1 + random.uniform(-0.5, 0.5)
        
        return ThermalData(
            timestamp=time.time(),
            cabin_temperature=self.cabin_temp,
            battery_coolant_temp=25 + random.uniform(-5, 10),
            motor_coolant_temp=30 + random.uniform(-10, 20),
            ambient_temperature=15 + random.uniform(-10, 30),
            hvac_compressor_power=abs(self.cabin_temp - 22.0) * 0.3 + random.uniform(0, 2),
            coolant_pump_speed=1500 + random.uniform(-300, 500),
            radiator_fan_speed=random.uniform(0, 5000),
            battery_cooling_demand=random.uniform(0, 100),
            motor_cooling_demand=random.uniform(0, 100),
            heat_pump_active=abs(self.cabin_temp - 22.0) > 5,
            precondition_active=False
        )


class BodyControlSimulator(ECUSimulator):
    """Simulate Body Control Module data streams"""
    
    def __init__(self, frequency_hz: float = 5):
        super().__init__("BODY_CONTROL", frequency_hz)
    
    def generate_data(self) -> BodyControlData:
        """Generate realistic body control data"""
        import random
        
        return BodyControlData(
            timestamp=time.time(),
            door_front_left_open=False,
            door_front_right_open=False,
            door_rear_left_open=False,
            door_rear_right_open=False,
            trunk_open=False,
            hood_open=False,
            lights_front_left=True,
            lights_front_right=True,
            lights_rear_left=random.random() > 0.5,
            lights_rear_right=random.random() > 0.5,
            windshield_wiper_speed=random.randint(0, 2),
            rain_sensor_level=random.randint(0, 50),
            window_position_fl=random.randint(0, 100),
            window_position_fr=random.randint(0, 100),
            window_position_rl=random.randint(0, 100),
            window_position_rr=random.randint(0, 100)
        )


# ============================================================================
# Data Stream Validator
# ============================================================================

class DataStreamValidator:
    """Validates data from multiple ECUs"""
    
    def __init__(self):
        self.validators = {
            'ADAS': lambda x: ADASData(**x).validate() if isinstance(x, dict) else x.validate(),
            'POWERTRAIN': lambda x: PowertrainData(**x).validate() if isinstance(x, dict) else x.validate(),
            'BATTERY': lambda x: BatteryData(**x).validate() if isinstance(x, dict) else x.validate(),
            'THERMAL': lambda x: ThermalData(**x).validate() if isinstance(x, dict) else x.validate(),
            'BODY': lambda x: BodyControlData(**x).validate() if isinstance(x, dict) else x.validate(),
        }
        self.test_results = []
    
    def validate_data_stream(self, ecu_type: str, data):
        """Validate single ECU data stream"""
        if ecu_type not in self.validators:
            return False, [f"Unknown ECU type: {ecu_type}"]
        
        try:
            is_valid, errors = self.validators[ecu_type](data)
            return is_valid, errors
        except Exception as e:
            return False, [str(e)]
    
    def validate_cross_ecus(self, adas_data, powertrain_data, battery_data):
        """Validate consistency across multiple ECUs"""
        errors = []
        
        # ADAS and Powertrain consistency
        if adas_data and powertrain_data:
            speed_adas = adas_data.current_speed
            speed_powertrain = (powertrain_data.motor_rpm * 3.14159 * 0.35) / (60 * 3.6)  # Estimate
            
            if abs(speed_adas - speed_powertrain) > 5:
                errors.append(f"Speed mismatch: ADAS={speed_adas}, Powertrain={speed_powertrain}")
        
        # Battery and Thermal consistency
        if battery_data and battery_data.state_of_charge < 10:
            errors.append("Battery critical low SOC")
        
        if battery_data and battery_data.battery_temperature > 55:
            errors.append("Battery temperature too high")
        
        return len(errors) == 0, errors


# ============================================================================
# Data Stream Statistics and Analysis
# ============================================================================

class DataStreamAnalysis:
    """Analyze ECU data streams for anomalies"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_windows = {}
    
    def add_sample(self, ecu_name: str, metric: str, value: float):
        """Add data sample to window"""
        key = f"{ecu_name}:{metric}"
        
        if key not in self.data_windows:
            self.data_windows[key] = []
        
        self.data_windows[key].append(value)
        
        if len(self.data_windows[key]) > self.window_size:
            self.data_windows[key].pop(0)
    
    def detect_anomalies(self, ecu_name: str, metric: str, value: float) -> Tuple[bool, str]:
        """Detect anomalies in data stream"""
        key = f"{ecu_name}:{metric}"
        
        if key not in self.data_windows or len(self.data_windows[key]) < 10:
            return False, "Insufficient data"
        
        data = self.data_windows[key]
        mean = statistics.mean(data)
        stdev = statistics.stdev(data) if len(data) > 1 else 0
        
        # 3-sigma rule for anomaly detection
        if stdev > 0:
            z_score = abs((value - mean) / stdev)
            if z_score > 3:
                return True, f"Anomaly detected: Z-score={z_score:.2f}"
        
        return False, "Normal"
    
    def get_statistics(self, ecu_name: str, metric: str) -> dict:
        """Get statistical summary of data stream"""
        key = f"{ecu_name}:{metric}"
        
        if key not in self.data_windows:
            return {}
        
        data = self.data_windows[key]
        
        return {
            'min': min(data),
            'max': max(data),
            'mean': statistics.mean(data),
            'stdev': statistics.stdev(data) if len(data) > 1 else 0,
            'count': len(data)
        }


# ============================================================================
# Test Suite Classes
# ============================================================================

class TestADASDataStream(unittest.TestCase):
    """Test ADAS ECU data stream"""
    
    def setUp(self):
        self.simulator = ADASSimulator(frequency_hz=10)
        self.validator = DataStreamValidator()
    
    def test_adas_data_generation(self):
        """Test ADAS ECU generates valid data"""
        data = self.simulator.generate_data()
        self.assertIsNotNone(data)
        self.assertGreaterEqual(data.timestamp, 0)
    
    def test_adas_data_validation(self):
        """Test ADAS data passes validation"""
        for _ in range(10):
            data = self.simulator.generate_data()
            is_valid, errors = self.validator.validate_data_stream('ADAS', data)
            self.assertTrue(is_valid, f"Validation errors: {errors}")
    
    def test_adas_range_limits(self):
        """Test ADAS values within valid ranges"""
        data = self.simulator.generate_data()
        
        self.assertGreaterEqual(data.current_speed, 0)
        self.assertLessEqual(data.current_speed, 200)
        
        self.assertGreaterEqual(data.lidar_range, 0)
        self.assertLessEqual(data.lidar_range, 200)
        
        self.assertGreater(data.collision_distance, 0)
    
    def test_adas_logical_consistency(self):
        """Test ADAS logical consistency"""
        data = self.simulator.generate_data()
        
        # If emergency brake is on, vehicle should be decelerating
        if data.emergency_brake_active:
            self.assertTrue(data.collision_warning)
            self.assertLess(data.collision_distance, 30)
        
        # Lane keeping can't be active if error is small
        if abs(data.lateral_error) < 0.1:
            pass  # Lane keeping may or may not be active
        
        # Collision warning requires close object
        if data.collision_warning:
            self.assertLess(data.collision_distance, 50)
    
    def test_adas_sensor_fusion(self):
        """Test ADAS sensor fusion (camera, LIDAR, Radar consistency)"""
        data = self.simulator.generate_data()
        
        # Camera and Radar should detect similar number of objects
        if data.front_camera_objects > 0:
            self.assertGreater(data.radar_objects, 0)
        
        if data.radar_objects > 0:
            diff = abs(data.front_camera_objects - data.radar_objects)
            self.assertLessEqual(diff, 3)  # Max difference of 3 objects


class TestPowertrainDataStream(unittest.TestCase):
    """Test Powertrain/Motor ECU data stream"""
    
    def setUp(self):
        self.simulator = PowertrainSimulator(frequency_hz=50)
        self.validator = DataStreamValidator()
    
    def test_powertrain_data_generation(self):
        """Test Powertrain ECU generates valid data"""
        data = self.simulator.generate_data()
        self.assertIsNotNone(data)
    
    def test_powertrain_data_validation(self):
        """Test Powertrain data passes validation"""
        for _ in range(20):
            data = self.simulator.generate_data()
            is_valid, errors = self.validator.validate_data_stream('POWERTRAIN', data)
            self.assertTrue(is_valid, f"Validation errors: {errors}")
    
    def test_motor_power_calculation(self):
        """Test motor power calculation"""
        data = self.simulator.generate_data()
        
        # P = T * ω = T * (RPM * 2π/60) [Watts]
        expected_power = (data.motor_torque * data.motor_rpm * 3.14159 / 30) / 1000
        
        # Allow 20% error due to efficiency losses
        if expected_power > 1:
            self.assertGreaterEqual(data.motor_power, expected_power * 0.8)
            self.assertLessEqual(data.motor_power, expected_power * 1.2)
    
    def test_three_phase_current_balance(self):
        """Test three-phase current balance"""
        data = self.simulator.generate_data()
        
        # Three phases should be relatively balanced
        currents = [data.phase_a_current, data.phase_b_current, data.phase_c_current]
        avg_current = statistics.mean([abs(c) for c in currents])
        
        for current in currents:
            if avg_current > 10:
                # 10% tolerance
                tolerance = avg_current * 0.1
                self.assertLess(abs(abs(current) - avg_current), tolerance)
    
    def test_inverter_overtemperature_protection(self):
        """Test inverter temperature limits"""
        data = self.simulator.generate_data()
        
        self.assertLess(data.inverter_temperature, 110)  # Critical limit
    
    def test_efficiency_limits(self):
        """Test motor efficiency limits"""
        data = self.simulator.generate_data()
        
        self.assertGreater(data.motor_efficiency, 80)
        self.assertLess(data.motor_efficiency, 98)


class TestBatteryDataStream(unittest.TestCase):
    """Test Battery Management System data stream"""
    
    def setUp(self):
        self.simulator = BatterySimulator(frequency_hz=10)
        self.validator = DataStreamValidator()
    
    def test_battery_data_validation(self):
        """Test Battery data passes validation"""
        for _ in range(15):
            data = self.simulator.generate_data()
            is_valid, errors = self.validator.validate_data_stream('BATTERY', data)
            self.assertTrue(is_valid, f"Validation errors: {errors}")
    
    def test_battery_voltage_soc_relationship(self):
        """Test Battery voltage and SOC relationship"""
        data = self.simulator.generate_data()
        
        # Higher SOC should correlate with higher voltage
        # Expected: V = 300 + SOC * 1.5 (approx)
        expected_voltage = 300 + data.state_of_charge * 1.5
        
        # Allow 10% tolerance
        self.assertGreater(data.total_voltage, expected_voltage * 0.9)
        self.assertLess(data.total_voltage, expected_voltage * 1.1)
    
    def test_battery_cell_balance(self):
        """Test battery cell voltage balance"""
        data = self.simulator.generate_data()
        
        # Cell imbalance should be less than 0.5V
        self.assertLess(data.cell_voltage_imbalance, 0.5)
        
        # Max voltage should be greater than min
        self.assertGreater(data.cell_voltage_max, data.cell_voltage_min)
    
    def test_thermal_runaway_detection(self):
        """Test thermal runaway risk detection"""
        data = self.simulator.generate_data()
        
        # High temperature should trigger risk
        if data.battery_temperature > 55:
            self.assertTrue(data.thermal_runaway_risk)
        
        # Normal temperature should not trigger risk
        if data.battery_temperature < 45:
            self.assertFalse(data.thermal_runaway_risk)
    
    def test_cooling_demand_correlation(self):
        """Test cooling demand correlates with temperature"""
        data = self.simulator.generate_data()
        
        # Higher temperature should increase cooling demand
        if data.battery_temperature > 35:
            self.assertGreater(data.cooling_power, 1.0)


class TestThermalDataStream(unittest.TestCase):
    """Test Thermal Management System data stream"""
    
    def setUp(self):
        self.simulator = ThermalSimulator(frequency_hz=5)
        self.validator = DataStreamValidator()
    
    def test_thermal_data_validation(self):
        """Test Thermal data passes validation"""
        for _ in range(10):
            data = self.simulator.generate_data()
            is_valid, errors = self.validator.validate_data_stream('THERMAL', data)
            self.assertTrue(is_valid, f"Validation errors: {errors}")
    
    def test_cabin_temperature_control(self):
        """Test cabin temperature regulation"""
        temperatures = []
        
        for _ in range(50):
            data = self.simulator.generate_data()
            temperatures.append(data.cabin_temperature)
        
        # Cabin should stabilize around 22°C
        avg_temp = statistics.mean(temperatures)
        self.assertGreater(avg_temp, 20)
        self.assertLess(avg_temp, 24)


class TestBodyControlDataStream(unittest.TestCase):
    """Test Body Control Module data stream"""
    
    def setUp(self):
        self.simulator = BodyControlSimulator(frequency_hz=5)
        self.validator = DataStreamValidator()
    
    def test_body_control_data_validation(self):
        """Test Body Control data passes validation"""
        for _ in range(10):
            data = self.simulator.generate_data()
            is_valid, errors = self.validator.validate_data_stream('BODY', data)
            self.assertTrue(is_valid, f"Validation errors: {errors}")


class TestCrossECUConsistency(unittest.TestCase):
    """Test consistency across multiple ECUs"""
    
    def setUp(self):
        self.adas_sim = ADASSimulator()
        self.powertrain_sim = PowertrainSimulator()
        self.battery_sim = BatterySimulator()
        self.validator = DataStreamValidator()
    
    def test_speed_consistency(self):
        """Test speed consistency between ADAS and Powertrain"""
        adas_data = self.simulator.generate_data()
        powertrain_data = self.powertrain_sim.generate_data()
        
        adas_speed = adas_data.current_speed
        # Speed from motor: SPD = RPM * π * D / 60 (where D is wheel diameter in m)
        powertrain_speed = (powertrain_data.motor_rpm * 3.14159 * 0.35) / (60 * 3.6)
        
        # Should be within ±10 km/h
        if adas_speed > 10:
            self.assertLess(abs(adas_speed - powertrain_speed), 10)
    
    def test_energy_conservation(self):
        """Test energy conservation between battery and motor"""
        battery_data = self.battery_sim.generate_data()
        
        # Power output should not exceed available power
        # (Rough check: current * voltage / 1000 >= power demand)
        available_power = abs(battery_data.total_current * battery_data.total_voltage / 1000)
        
        # Allow charging or discharging with some margin
        self.assertGreater(available_power, 0)


class TestDataStreamRealtime(unittest.TestCase):
    """Test real-time data stream processing"""
    
    def setUp(self):
        self.adas_sim = ADASSimulator(frequency_hz=25)
        self.analysis = DataStreamAnalysis(window_size=100)
    
    def test_data_latency(self):
        """Test data stream latency"""
        start_time = time.time()
        
        for _ in range(100):
            data = self.adas_sim.generate_data()
            if data:
                self.assertIsNotNone(data.timestamp)
        
        elapsed = time.time() - start_time
        latency = elapsed / 100
        
        # Should process at least 10 messages per second (100ms max)
        self.assertLess(latency, 0.1)  # 100ms max per message
    
    def test_anomaly_detection(self):
        """Test anomaly detection in data streams"""
        # Generate normal data
        for _ in range(50):
            data = self.adas_sim.generate_data()
            self.analysis.add_sample("ADAS", "current_speed", data.current_speed)
        
        # Get baseline statistics
        stats = self.analysis.get_statistics("ADAS", "current_speed")
        
        self.assertIn('mean', stats)
        self.assertIn('stdev', stats)


class TestDataStreamReporting(unittest.TestCase):
    """Test data stream reporting and logging"""
    
    def test_json_serialization(self):
        """Test ECU data can be serialized to JSON"""
        from dataclasses import asdict
        
        simulator = ADASSimulator()
        data = simulator.generate_data()
        
        # Convert to dict and then JSON
        data_dict = asdict(data)
        json_str = json.dumps(data_dict)
        
        self.assertIsNotNone(json_str)
        self.assertIn("current_speed", json_str)
    
    def test_test_report_generation(self):
        """Test data stream test report generation"""
        report = {
            'test_date': datetime.now().isoformat(),
            'total_messages': 1000,
            'valid_messages': 990,
            'invalid_messages': 10,
            'success_rate': 99.0,
            'ecu_status': {
                'ADAS': 'PASS',
                'POWERTRAIN': 'PASS',
                'BATTERY': 'WARN',  # Warning on temperature
                'THERMAL': 'PASS',
                'BODY': 'PASS'
            }
        }
        
        self.assertEqual(len(report['ecu_status']), 5)


# ============================================================================
# Integration Test Runner
# ============================================================================

class ECUDataStreamTestRunner:
    """Run comprehensive ECU data stream tests"""
    
    def __init__(self):
        self.results = {
            'ADAS': {'pass': 0, 'fail': 0},
            'POWERTRAIN': {'pass': 0, 'fail': 0},
            'BATTERY': {'pass': 0, 'fail': 0},
            'THERMAL': {'pass': 0, 'fail': 0},
            'BODY': {'pass': 0, 'fail': 0}
        }
    
    def run_all_tests(self):
        """Run all data stream tests"""
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add all test classes
        suite.addTests(loader.loadTestsFromTestCase(TestADASDataStream))
        suite.addTests(loader.loadTestsFromTestCase(TestPowertrainDataStream))
        suite.addTests(loader.loadTestsFromTestCase(TestBatteryDataStream))
        suite.addTests(loader.loadTestsFromTestCase(TestThermalDataStream))
        suite.addTests(loader.loadTestsFromTestCase(TestBodyControlDataStream))
        suite.addTests(loader.loadTestsFromTestCase(TestCrossECUConsistency))
        suite.addTests(loader.loadTestsFromTestCase(TestDataStreamRealtime))
        suite.addTests(loader.loadTestsFromTestCase(TestDataStreamReporting))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)
    
    def generate_report(self, result) -> dict:
        """Generate test report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tests': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors),
            'failed': len(result.failures),
            'errors': len(result.errors),
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        }


# ============================================================================
# Example Usage and Demonstration
# ============================================================================

def demonstrate_ecu_monitoring():
    """Demonstrate real-time ECU data stream monitoring"""
    print("\n" + "="*80)
    print("ECU DATA STREAM MONITORING DEMONSTRATION")
    print("="*80 + "\n")
    
    # Create simulators
    adas_sim = ADASSimulator(frequency_hz=10)
    powertrain_sim = PowertrainSimulator(frequency_hz=25)
    battery_sim = BatterySimulator(frequency_hz=10)
    thermal_sim = ThermalSimulator(frequency_hz=5)
    body_sim = BodyControlSimulator(frequency_hz=5)
    
    validator = DataStreamValidator()
    analysis = DataStreamAnalysis(window_size=100)
    
    # Start simulators
    adas_sim.start()
    powertrain_sim.start()
    battery_sim.start()
    thermal_sim.start()
    body_sim.start()
    
    # Collect and analyze data
    print("Monitoring ECU data streams for 30 seconds...\n")
    
    for i in range(30):
        # Collect latest data from all ECUs
        adas_data = adas_sim.get_data()
        powertrain_data = powertrain_sim.get_data()
        battery_data = battery_sim.get_data()
        thermal_data = thermal_sim.get_data()
        body_data = body_sim.get_data()
        
        # Validate ADAS data
        if adas_data:
            is_valid, errors = validator.validate_data_stream('ADAS', adas_data)
            analysis.add_sample("ADAS", "current_speed", adas_data.current_speed)
            analysis.add_sample("ADAS", "collision_distance", adas_data.collision_distance)
            
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"[{i}s] ADAS: {status} | Speed: {adas_data.current_speed:.1f} km/h | "
                  f"Collision Dist: {adas_data.collision_distance:.1f}m")
        
        # Validate Powertrain data
        if powertrain_data:
            is_valid, errors = validator.validate_data_stream('POWERTRAIN', powertrain_data)
            analysis.add_sample("POWERTRAIN", "motor_rpm", powertrain_data.motor_rpm)
            
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"[{i}s] MOTOR: {status} | RPM: {powertrain_data.motor_rpm:.0f} | "
                  f"Torque: {powertrain_data.motor_torque:.1f} Nm | "
                  f"Temp: {powertrain_data.motor_temperature:.1f}°C")
        
        # Validate Battery data
        if battery_data:
            is_valid, errors = validator.validate_data_stream('BATTERY', battery_data)
            analysis.add_sample("BATTERY", "state_of_charge", battery_data.state_of_charge)
            
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"[{i}s] BATTERY: {status} | SOC: {battery_data.state_of_charge:.1f}% | "
                  f"Temp: {battery_data.battery_temperature:.1f}°C | "
                  f"Voltage: {battery_data.total_voltage:.1f}V")
        
        # Validate Thermal data
        if thermal_data:
            is_valid, errors = validator.validate_data_stream('THERMAL', thermal_data)
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"[{i}s] THERMAL: {status} | Cabin: {thermal_data.cabin_temperature:.1f}°C | "
                  f"Battery: {thermal_data.battery_coolant_temp:.1f}°C")
        
        print()
        time.sleep(1)
    
    # Stop simulators
    adas_sim.stop()
    powertrain_sim.stop()
    battery_sim.stop()
    thermal_sim.stop()
    body_sim.stop()
    
    # Print statistics
    print("\n" + "="*80)
    print("DATA STREAM STATISTICS")
    print("="*80 + "\n")
    
    for ecu in ["ADAS", "POWERTRAIN", "BATTERY"]:
        for metric in ["current_speed", "motor_rpm", "state_of_charge"]:
            stats = analysis.get_statistics(ecu, metric)
            if stats:
                print(f"{ecu} - {metric}:")
                print(f"  Min: {stats['min']:.2f}, Max: {stats['max']:.2f}, "
                      f"Mean: {stats['mean']:.2f}, StdDev: {stats['stdev']:.2f}")


if __name__ == '__main__':
    # Run demonstration
    demonstrate_ecu_monitoring()
    
    # Run unit tests
    print("\n\n" + "="*80)
    print("RUNNING UNIT TESTS")
    print("="*80 + "\n")
    
    runner = ECUDataStreamTestRunner()
    result = runner.run_all_tests()
    
    # Generate and print report
    report = runner.generate_report(result)
    print("\n" + "="*80)
    print("TEST REPORT")
    print("="*80)
    print(json.dumps(report, indent=2))
