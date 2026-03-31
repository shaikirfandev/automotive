# CAPL Scripting Tutorial: From Zero to Hero

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basics](#basics)
4. [Data Types and Variables](#data-types-and-variables)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Functions](#functions)
8. [Event Handlers](#event-handlers)
9. [CAN Bus Operations](#can-bus-operations)
10. [Advanced Topics](#advanced-topics)
11. [Best Practices](#best-practices)
12. [Complete Examples](#complete-examples)

---

## Introduction

### What is CAPL?

**CAPL** (Communication Access Programming Language) is a C-like scripting language designed for automotive communication testing and simulation. It's primarily used in:

- **Vector CANoe** - CAN/LIN network simulation and testing
- **Vector CANalyzer** - CAN/LIN network analysis
- **PEAK PCAN** - CAN network development tools

### Why CAPL?

- Test CAN, LIN, MOST, and Ethernet communication
- Automate testing procedures
- Simulate ECU (Electronic Control Unit) behavior
- Monitor and analyze bus traffic
- Validate network protocols

### Before You Start

You'll need:
- **Vector CANoe** or **CANalyzer** (or equivalent PEAK PCAN tool)
- A basic understanding of CAN bus concept
- Basic programming knowledge (C-like syntax)
- Understanding of DBC files (CAN database)

---

## Getting Started

### Step 1: Understanding Your Environment

In CANoe, scripts are written in `.can` files and are integrated into your simulation setup. Each script has access to:

- All defined messages in your DBC file
- All signals within those messages
- CAN bus communication channels
- Timer functions
- System variables

### Step 2: Creating Your First Script

1. In CANoe, go to **Measurement > Edit Test Setup**
2. Click **Add > CAPL Test Module**
3. Create a new `.can` file
4. Start with basic syntax

### Step 3: Script Structure

Every CAPL script follows this general structure:

```capl
// 1. Variable Declarations (Global)
variables {
    int counter = 0;
    dword timeOut = 5000;
}

// 2. Event Handlers
on preStart {
    // Runs once when measurement starts
    Write("Measurement starting...");
}

on busTypes.CAN.init {
    // Initialization code
}

on message CanMessage {
    // Handle incoming CAN message
}

// 3. Functions
void MyFunction() {
    // Function implementation
}

// 4. Cleanup
on postStop {
    // Cleanup code before measurement stops
}
```

---

## Basics

### Comments

```capl
// Single line comment

/* Multi-line
   comment */
```

### Output Functions

Print debugging information to the Output window:

```capl
Write("Message: %d", value);              // Write to output
WriteHex(0x1234);                         // Write hex value
WriteFloat(3.14);                         // Write float value

// Format specifiers:
// %d - integer
// %x - hexadecimal
// %f - float
// %s - string
```

### Delay and Timing

```capl
// Delay execution
delay(1000);        // Delay 1000 milliseconds

// Using timers (better approach)
SetTimer(MyTimer, 1000);    // Set timer for 1 second
CancelTimer(MyTimer);        // Cancel timer
```

---

## Data Types and Variables

### Primitive Data Types

```capl
variables {
    // Integer types
    byte b = 255;              // 0-255
    word w = 65535;            // 0-65535
    dword dw = 4294967295;     // 0-4294967295
    int i = -2147483648;       // Signed integer
    long l = 9223372036854775807;  // Long integer
    
    // Floating point
    float f = 3.14;            // Single precision
    double d = 3.14159265359;  // Double precision
    
    // Character and string
    char c = 'A';              // Single character
    char str[100] = "Hello";   // String (null-terminated)
    
    // Enumeration
    enum State { Idle, Active, Error };
    State currentState = Idle;
    
    // Boolean
    int flag = 0;              // 0 = false, 1 = true
}
```

### CAN-Specific Data Types

```capl
variables {
    // Message variable (from DBC)
    CanMessage msg;            // Generic CAN message
    MessageName specifMsg;     // Specific message (from DBC)
    
    // Signal variable
    SignalName sig;            // Access DBC signal
    
    // System variables
    dword timeNow = timeNow(); // Current time in milliseconds
}
```

### Arrays

```capl
variables {
    byte data[8];              // Array of 8 bytes
    int matrix[3][4];          // 2D array
    char buffer[256];          // Character array/string
}
```

### Scope

```capl
int globalVar = 10;            // Global - accessible everywhere

on message Engine {
    int localVar = 20;         // Local - only in this event
    globalVar = globalVar + 1; // Can access global
}
```

---

## Operators

### Arithmetic Operators

```capl
int a = 10, b = 3;
int sum = a + b;       // 13
int diff = a - b;      // 7
int prod = a * b;      // 30
int quot = a / b;      // 3
int rema = a % b;      // 1 (remainder)
```

### Comparison Operators

```capl
int a = 10, b = 5;
if (a == b) { }        // Equal to
if (a != b) { }        // Not equal
if (a > b)  { }        // Greater than
if (a < b)  { }        // Less than
if (a >= b) { }        // Greater than or equal
if (a <= b) { }        // Less than or equal
```

### Logical Operators

```capl
if (a > 5 && b < 10) { }   // AND
if (a > 5 || b < 10) { }   // OR
if (!flag) { }              // NOT
```

### Bitwise Operators

```capl
byte a = 0x0F;
byte b = 0xF0;
byte and_result = a & b;    // 0x00
byte or_result = a | b;     // 0xFF
byte xor_result = a ^ b;    // 0xFF
byte not_result = ~a;       // 0xF0
byte shift_left = a << 1;   // 0x1E
byte shift_right = a >> 1;  // 0x07
```

### Assignment Operators

```capl
int x = 10;
x += 5;    // x = 15
x -= 3;    // x = 12
x *= 2;    // x = 24
x /= 4;    // x = 6
x %= 3;    // x = 0
```

### Ternary Operator

```capl
int age = 20;
char* status = (age >= 18) ? "Adult" : "Minor";
```

---

## Control Flow

### If-Else Statement

```capl
int speed = 50;

if (speed > 100) {
    Write("Too fast!");
} else if (speed > 50) {
    Write("Moderate speed");
} else {
    Write("Slow speed");
}
```

### Switch Statement

```capl
int state = 1;

switch (state) {
    case 0:
        Write("Idle");
        break;
    case 1:
        Write("Running");
        break;
    case 2:
        Write("Error");
        break;
    default:
        Write("Unknown state");
        break;
}
```

### For Loop

```capl
// Traditional for loop
for (int i = 0; i < 10; i++) {
    Write("Value: %d", i);
}

// Loop with break
for (int i = 0; i < 100; i++) {
    if (i == 50) break;  // Exit loop
    Write("%d", i);
}

// Loop with continue
for (int i = 0; i < 10; i++) {
    if (i == 5) continue;  // Skip to next iteration
    Write("%d", i);
}
```

### While Loop

```capl
int counter = 0;
while (counter < 10) {
    Write("Count: %d", counter);
    counter++;
}
```

### Do-While Loop

```capl
int counter = 0;
do {
    Write("Count: %d", counter);
    counter++;
} while (counter < 10);  // Executes at least once
```

---

## Functions

### Defining Functions

```capl
// Function without return value
void PrintMessage(char* msg) {
    Write(msg);
}

// Function with return value
int Add(int a, int b) {
    return a + b;
}

// Multiple parameters of different types
float CalculateAverage(int a, int b, int c) {
    return (float)(a + b + c) / 3.0;
}

// No parameters
int GetCounter() {
    return counter;
}
```

### Calling Functions

```capl
// Void function
PrintMessage("Hello World");

// Function with return
int result = Add(5, 3);
Write("Result: %d", result);

// With multiple parameters
float avg = CalculateAverage(10, 20, 30);
```

### Passing Parameters

```capl
// Pass by value (copy)
void ModifyValue(int val) {
    val = 100;  // Changes only local copy
}

int original = 50;
ModifyValue(original);  // original is still 50

// Pass by reference (for arrays, use with caution)
void FillArray(byte arr[], int size) {
    for (int i = 0; i < size; i++) {
        arr[i] = i;
    }
}

byte myArray[10];
FillArray(myArray, 10);  // myArray is modified
```

### Variable Scope

```capl
int global_x = 10;  // Global scope

void MyFunc() {
    int func_local = 20;  // Function scope
    
    {
        int block_local = 30;  // Block scope
    }
    
    // block_local is not accessible here
}
```

---

## Event Handlers

Event handlers are triggered by specific events in the system. They're crucial for CAPL network simulation.

### Lifecycle Events

```capl
// Before measurement starts
on preStart {
    Write("Initializing...");
    counter = 0;
    SetTimer(HeartbeatTimer, 1000);
}

// Measurement has started (CAN bus is active)
on Start {
    Write("Measurement started");
}

// Before measurement stops
on preStop {
    Write("Cleaning up...");
    CancelTimer(HeartbeatTimer);
}

// After measurement stops
on postStop {
    Write("Measurement ended");
}
```

### Timer Events

```capl
// Define timer in variables
variables {
    Timer HeartbeatTimer;
    Timer TimeoutTimer;
}

// Timer fired
on Timer HeartbeatTimer {
    Write("Heartbeat: %d ms", timeNow());
    SetTimer(HeartbeatTimer, 1000);  // Reschedule
}

on Timer TimeoutTimer {
    Write("Timeout occurred!");
}

// You can set timers like this:
SetTimer(HeartbeatTimer, 1000);     // 1 second
CancelTimer(TimeoutTimer);          // Cancel timer
```

### CAN Message Events

```capl
// Receive any CAN message
on message {
    Write("Message ID: 0x%X, Length: %d", this.ID, this.DLC);
}

// Receive specific message (from DBC)
on message EngineData {
    Write("Engine speed: %d", this.EngineSpeed);
    Write("Engine temp: %d", this.EngineTemp);
    
    // Access signal values
    int rpm = EngineData.EngineSpeed;
    int temp = EngineData.EngineTemp;
}

// Message with ID check
on message 0x100 {
    Write("Received message 0x100");
}

// Multiple messages
on message EngineData, TransmissionData, BrakesData {
    Write("Multi-message handler: ID = 0x%X", this.ID);
}
```

### Signal Events

```capl
// React to specific signal changes
on signal EngineData.EngineSpeed {
    if (EngineData.EngineSpeed > 5000) {
        Write("High RPM detected!");
    }
}
```

### Error Events

```capl
// CAN error event
on CAN.Error {
    Write("CAN Error!");
}

// Bus off event
on BusOff {
    Write("Bus is off!");
}
```

---

## CAN Bus Operations

### Sending Messages

```capl
variables {
    message EngineData msg_send;
}

// Method 1: Using message variable
on key 's' {
    msg_send.EngineSpeed = 3000;
    msg_send.EngineTemp = 85;
    output(msg_send);  // Send message
}

// Method 2: Direct message creation and send
on key 'x' {
    output(EngineData msg) {
        EngineSpeed = 2000;
        EngineTemp = 80;
    }
}

// Method 3: Using send function
void SendEngineData(int speed, int temp) {
    output(EngineData msg) {
        msg.EngineSpeed = speed;
        msg.EngineTemp = temp;
    }
}
```

### Message Properties

```capl
on message EngineData {
    // Access message properties
    dword id = this.ID;          // Message ID
    byte dlc = this.DLC;         // Data Length Code
    byte data[8];
    for (int i = 0; i < dlc; i++) {
        data[i] = this.data[i];
    }
    
    // Message timestamp
    dword timestamp = this.Timestamp;
}
```

### Signal Access

```capl
on message EngineData {
    // Read signal value
    int speed = EngineData.EngineSpeed;
    int temp = EngineData.EngineTemp;
    
    // Check if signal received
    if (EngineData.EngineSpeed_IsReceived == 1) {
        Write("Speed is valid");
    }
}

// Access raw signal values
on message GenericMsg {
    byte raw_data[8];
    for (int i = 0; i < this.DLC; i++) {
        raw_data[i] = this.data[i];
    }
}
```

### CAN Bus Control

```capl
// Check if bus is active
if (CanBusOn()) {
    Write("CAN bus is active");
}

// Monitor bus errors
on CAN.Error {
    Write("This is a CAN error event!");
}
```

---

## Advanced Topics

### State Machines

```capl
variables {
    enum SystemState {
        STATE_IDLE = 0,
        STATE_INIT = 1,
        STATE_RUNNING = 2,
        STATE_ERROR = 3
    };
    
    SystemState currentState = STATE_IDLE;
}

void UpdateState(SystemState newState) {
    if (currentState != newState) {
        Write("State transition: %d -> %d", currentState, newState);
        currentState = newState;
    }
}

void HandleStateEvent(int eventId) {
    switch (currentState) {
        case STATE_IDLE:
            if (eventId == 1) {
                UpdateState(STATE_INIT);
            }
            break;
            
        case STATE_INIT:
            if (eventId == 2) {
                UpdateState(STATE_RUNNING);
            }
            if (eventId == 3) {
                UpdateState(STATE_ERROR);
            }
            break;
            
        case STATE_RUNNING:
            if (eventId == 4) {
                UpdateState(STATE_IDLE);
            }
            break;
            
        case STATE_ERROR:
            if (eventId == 5) {
                UpdateState(STATE_IDLE);
            }
            break;
    }
}
```

### Data Structures

```capl
// Struct-like implementation using arrays
variables {
    struct VehicleState {
        int speed;
        int rpm;
        int gear;
        byte temperature;
    };
    
    VehicleState currentVehicleState;
}

void InitVehicleState() {
    currentVehicleState.speed = 0;
    currentVehicleState.rpm = 0;
    currentVehicleState.gear = 0;
    currentVehicleState.temperature = 0;
}
```

### Cyclic/Periodic Execution

```capl
variables {
    Timer CyclicTimer;
    int cycleCount = 0;
}

on preStart {
    SetTimer(CyclicTimer, 100);  // Execute every 100ms
}

on Timer CyclicTimer {
    cycleCount++;
    
    // Periodic check
    if (cycleCount % 10 == 0) {
        Write("Periodic check at cycle %d", cycleCount);
    }
    
    // Send periodic message
    output(HeartbeatMsg heartbeat) {
        heartbeat.Counter = cycleCount;
    }
    
    SetTimer(CyclicTimer, 100);  // Re-arm timer
}
```

### Error Handling and Validation

```capl
// Validate signal values
int ValidateEngineSpeed(int speed) {
    if (speed < 0) {
        Write("ERROR: Negative speed not allowed");
        return -1;  // Error
    }
    if (speed > 8000) {
        Write("ERROR: Speed exceeds maximum");
        return -1;
    }
    return speed;  // Valid
}

// Defensive programming
on message EngineData {
    int validSpeed = ValidateEngineSpeed(EngineData.EngineSpeed);
    
    if (validSpeed >= 0) {
        Write("Valid speed: %d", validSpeed);
    } else {
        Write("Invalid speed received");
    }
}
```

### Debug Helper Functions

```capl
void DebugMessage(char* label, dword value) {
    Write("[DEBUG] %s = 0x%X (%d)", label, value, value);
}

void DebugRawData(byte data[], int length) {
    char hexStr[256] = "";
    for (int i = 0; i < length; i++) {
        char tmp[4];
        sprintf(tmp, "%02X ", data[i]);
        strcat(hexStr, tmp);
    }
    Write("[HEX] %s", hexStr);
}

// Usage
on message SomeMsg {
    DebugMessage("Message ID", this.ID);
    DebugRawData(this.data, this.DLC);
}
```

### String Manipulation

```capl
variables {
    char buffer[256];
    char str1[50] = "Hello";
    char str2[50] = "World";
}

void StringExamples() {
    // String length
    int len = strlen(str1);  // Returns 5
    
    // String copy
    strcpy(buffer, str1);    // Copy str1 to buffer
    
    // String concatenation
    strcat(buffer, " ");
    strcat(buffer, str2);    // Now buffer contains "Hello World"
    
    // String comparison
    if (strcmp(str1, str2) == 0) {
        Write("Strings are equal");
    }
    
    // Formatted string
    sprintf(buffer, "Value: %d, Hex: 0x%X", 100, 255);
}
```

---

## Best Practices

### 1. Use Meaningful Names

```capl
// ❌ Bad
int x, y, z;
void f() { }

// ✅ Good
int engineRPM, engineTemperature, vehicleSpeed;
void ProcessEngineData() { }
```

### 2. Initialize Variables

```capl
// ❌ Bad - Undefined initial value
int counter;
on message SomeMsg {
    counter++;  // May have garbage value
}

// ✅ Good
variables {
    int counter = 0;
}
```

### 3. Use Constants for Magic Numbers

```capl
// ❌ Bad
if (speed > 5000) { }
delay(1000);

// ✅ Good
#define MAX_ENGINE_RPM 7000
#define TIMER_INTERVAL_MS 1000

if (speed > MAX_ENGINE_RPM) { }
delay(TIMER_INTERVAL_MS);
```

### 4. Defensive Programming

```capl
// Always check bounds and validity
void ProcessArray(byte arr[], int size) {
    if (arr == null || size <= 0) {
        Write("Invalid input to ProcessArray");
        return;
    }
    
    for (int i = 0; i < size; i++) {
        if (arr[i] > 255) {
            Write("Array index %d has invalid value", i);
            continue;
        }
    }
}
```

### 5. Structured Error Handling

```capl
#define ERROR_NONE 0
#define ERROR_INVALID_DATA 1
#define ERROR_TIMEOUT 2
#define ERROR_BUS_OFF 3

int ProcessMessage(message msg) {
    if (msg == null) {
        return ERROR_INVALID_DATA;
    }
    
    if (!CanBusOn()) {
        return ERROR_BUS_OFF;
    }
    
    // Process message...
    return ERROR_NONE;
}
```

### 6. Comment Complex Logic

```capl
// Calculate CRC16 for data validation
int CalculateCRC16(byte data[], int length) {
    int crc = 0xFFFF;  // Initial value
    
    for (int i = 0; i < length; i++) {
        crc ^= data[i];  // XOR with current byte
        
        // Shift and calculate polynomial
        for (int j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xA001;  // CRC16 polynomial
            } else {
                crc >>= 1;
            }
        }
    }
    
    return crc;
}
```

### 7. Use Enums for States

```capl
// ✅ Good - Self-documenting 
enum MessageType {
    MSG_HANDSHAKE = 0,
    MSG_DATA = 1,
    MSG_ACK = 2,
    MSG_ERROR = 3
};

on message GenericMsg {
    MessageType type = (MessageType)this.data[0];
    
    switch (type) {
        case MSG_HANDSHAKE:
            // Handle handshake
            break;
        // ...
    }
}
```

### 8. Manage Timers Properly

```capl
variables {
    Timer Tmr_SendData;
    Timer Tmr_Timeout;
}

on preStart {
    SetTimer(Tmr_SendData, 100);
}

on preStop {
    CancelTimer(Tmr_SendData);
    CancelTimer(Tmr_Timeout);  // Cancel all timers
}

on Timer Tmr_SendData {
    // Do work
    SetTimer(Tmr_SendData, 100);  // Reschedule
}
```

### 9. Test Incrementally

```capl
// Start with simple verification
on preStart {
    #if DEBUG  // Conditional compilation
    Write("DEBUG MODE - Additional logging enabled");
    #endif
}

on message EngineData {
    #if DEBUG
    Write("Received EngineData: Speed=%d, Temp=%d", 
          EngineData.EngineSpeed, 
          EngineData.EngineTemp);
    #endif
}
```

### 10. Performance Considerations

```capl
// ❌ Inefficient - Heavy computation every time
on message EngineData {
    for (int i = 0; i < 1000000; i++) {
        // Complex calculation
    }
}

// ✅ Better - Offload or optimize
variables {
    int lastCalculatedValue = 0;
    dword lastCalcTime = 0;
}

on message EngineData {
    // Only recalculate every 100ms
    if (timeNow() - lastCalcTime > 100) {
        lastCalculatedValue = HeavyCalculation();
        lastCalcTime = timeNow();
    }
    
    // Use cached value
    int result = lastCalculatedValue;
}
```

---

## Complete Examples

### Example 1: Simple Message Monitor

```capl
/*
 * Network Monitor
 * Logs all CAN messages to the Output window
 */

variables {
    int messageCount = 0;
    dword lastTimestamp = 0;
}

on preStart {
    messageCount = 0;
    Write("=== Network Monitor Started ===");
}

on message {
    messageCount++;
    
    dword timeDiff = this.Timestamp - lastTimestamp;
    lastTimestamp = this.Timestamp;
    
    Write("[%d] ID: 0x%03X | DLC: %d | Time: %d ms",
          messageCount, this.ID, this.DLC, timeDiff);
}

on postStop {
    Write("=== Monitor Stopped - Total Messages: %d ===", messageCount);
}
```

### Example 2: Engine RPM Monitor with Alerts

```capl
/*
 * Engine RPM Monitor
 * Alerts when RPM exceeds safe limits
 */

#define RPM_WARNING_THRESHOLD 5500
#define RPM_CRITICAL_THRESHOLD 7000

variables {
    int lastRPM = 0;
    int warningCount = 0;
    int criticalCount = 0;
    Timer MonitorTimer;
}

on preStart {
    SetTimer(MonitorTimer, 500);  // Check every 500ms
}

on Timer MonitorTimer {
    // Periodic monitoring logic
    SetTimer(MonitorTimer, 500);
}

on message EngineData {
    int currentRPM = EngineData.EngineSpeed;
    
    // Trend detection
    if (currentRPM > lastRPM) {
        Write("RPM increasing: %d -> %d", lastRPM, currentRPM);
    } else if (currentRPM < lastRPM) {
        Write("RPM decreasing: %d -> %d", lastRPM, currentRPM);
    }
    
    lastRPM = currentRPM;
    
    // Alert on critical threshold
    if (currentRPM > RPM_CRITICAL_THRESHOLD) {
        Write("!!! CRITICAL: RPM = %d !!!", currentRPM);
        criticalCount++;
        // Could trigger other actions
    } else if (currentRPM > RPM_WARNING_THRESHOLD) {
        Write("WARNING: High RPM = %d", currentRPM);
        warningCount++;
    }
}

on postStop {
    Write("\n=== Session Summary ===");
    Write("Warnings: %d", warningCount);
    Write("Critical Alerts: %d", criticalCount);
}
```

### Example 3: Message Sender with State Machine

```capl
/*
 * Intelligent Message Sender
 * Uses state machine to control message transmission
 */

#define HEARTBEAT_INTERVAL 100
#define INIT_TIMEOUT 5000

enum SystemState {
    INIT = 0,
    READY = 1,
    SENDING = 2,
    ERROR = 3
};

variables {
    SystemState state = INIT;
    Timer InitTimer;
    Timer SendTimer;
    int messagesSent = 0;
    int messagesReceived = 0;
}

void ChangeState(SystemState newState) {
    if (newState != state) {
        Write("[STATE] %d -> %d", state, newState);
        state = newState;
    }
}

void SendPeriodicData() {
    output(EngineData msg) {
        msg.EngineSpeed = 2000 + (messagesSent % 2000);
        msg.EngineTemp = 80 + (messagesSent % 20);
    }
    messagesSent++;
}

on preStart {
    ChangeState(INIT);
    SetTimer(InitTimer, INIT_TIMEOUT);
    Write("System initializing...");
}

on Timer InitTimer {
    if (state == INIT) {
        ChangeState(READY);
        SetTimer(SendTimer, HEARTBEAT_INTERVAL);
        Write("System ready to send");
    }
}

on Timer SendTimer {
    if (state == READY || state == SENDING) {
        ChangeState(SENDING);
        SendPeriodicData();
        SetTimer(SendTimer, HEARTBEAT_INTERVAL);
    }
}

on message EngineDataACK {
    messagesReceived++;
    if (state == INIT) {
        ChangeState(READY);
    }
}

on CAN.Error {
    ChangeState(ERROR);
    CancelTimer(SendTimer);
    Write("ERROR: CAN communication failed");
}

on preStop {
    CancelTimer(InitTimer);
    CancelTimer(SendTimer);
    Write("\n=== Final Statistics ===");
    Write("Messages Sent: %d", messagesSent);
    Write("Messages Received: %d", messagesReceived);
    Write("Success Rate: %.1f%%", 
          (float)messagesReceived / messagesSent * 100);
}
```

### Example 4: Protocol Handler with Validation

```capl
/*
 * Protocol Handler
 * Implements message validation and checksum verification
 */

#define PROTOCOL_VERSION 1
#define TIMEOUT_MS 2000

enum ProtocolState {
    WAITING_HEADER = 0,
    RECEIVING_DATA = 1,
    VALIDATING = 2,
    COMPLETE = 3
};

variables {
    byte rxBuffer[64];
    int rxIndex = 0;
    ProtocolState currentState = WAITING_HEADER;
    Timer TimeoutTimer;
}

// Calculate simple checksum
byte CalculateChecksum(byte data[], int length) {
    byte checksum = 0;
    for (int i = 0; i < length; i++) {
        checksum ^= data[i];
    }
    return checksum;
}

// Validate received data
int ValidateMessage(byte buffer[], int length) {
    if (length < 4) {
        Write("ERROR: Message too short");
        return 0;
    }
    
    if (buffer[0] != 0xAA) {
        Write("ERROR: Invalid header byte");
        return 0;
    }
    
    if (buffer[1] != PROTOCOL_VERSION) {
        Write("ERROR: Protocol version mismatch");
        return 0;
    }
    
    byte expectedChecksum = CalculateChecksum(buffer, length - 1);
    byte receivedChecksum = buffer[length - 1];
    
    if (expectedChecksum != receivedChecksum) {
        Write("ERROR: Checksum mismatch (expected 0x%02X, got 0x%02X)",
              expectedChecksum, receivedChecksum);
        return 0;
    }
    
    return 1;  // Valid
}

void ProcessMessage(byte buffer[], int length) {
    if (!ValidateMessage(buffer, length)) {
        return;
    }
    
    Write("Valid message received, length: %d", length);
    // Process validated message...
}

on message DataPacket {
    // Copy data to buffer
    for (int i = 0; i < this.DLC; i++) {
        rxBuffer[rxIndex++] = this.data[i];
    }
    
    SetTimer(TimeoutTimer, TIMEOUT_MS);
    
    // Check if we have a complete message
    if (rxIndex >= 5) {  // Minimum message length
        ProcessMessage(rxBuffer, rxIndex);
        rxIndex = 0;
        CancelTimer(TimeoutTimer);
    }
}

on Timer TimeoutTimer {
    Write("ERROR: Message reception timeout");
    rxIndex = 0;
}
```

---

## Tips & Tricks

### Debugging Tips

1. **Use Write() liberally** - Place Write() calls at critical points
2. **Trace variable changes** - Monitor important variables
3. **Log message reception** - Track incomplete or unexpected messages
4. **Check timing** - Use timestamps to understand message flow

### Performance Tips

1. **Cache results** - Don't recalculate same values frequently
2. **Batch operations** - Process multiple signals together
3. **Use timers wisely** - Don't set too many fast timers
4. **Avoid loops** - Especially nested loops in message handlers

### Common Patterns

1. **Cyclic sender** - Use timer + SetTimer in handler
2. **Request/Response** - Send message, wait for ACK with timeout
3. **State machine** - Track states with enum and switch
4. **Data accumulator** - Collect data and process in batch

---

## Quick Reference

### Frequently Used Functions

```capl
// I/O
Write(...);
WriteHex(value);
output(msg);

// Timing
SetTimer(timer, interval);
CancelTimer(timer);
timeNow();
delay(milliseconds);

// String
strlen(str);
strcpy(dest, src);
strcat(dest, src);
strcmp(str1, str2);
sprintf(buffer, format, ...);

// Message
msg.SignalName;
this.ID;
this.DLC;
this.data[index];
this.Timestamp;
```

### Common Events

```capl
on preStart { }
on Start { }
on preStop { }
on postStop { }
on message MessageName { }
on message 0xID { }
on message { }
on signal SignalName { }
on Timer TimerName { }
on key 'c' { }
on CAN.Error { }
```

---

## Conclusion

You've now learned CAPL from zero to hero! Key takeaways:

1. **Understand the basics** - Variables, operators, control flow
2. **Master event handlers** - Core of CAPL programming
3. **Practice CAN operations** - Send/receive messages
4. **Apply best practices** - Write maintainable code
5. **Debug effectively** - Use logging and testing

### Next Steps

1. Start with simple message monitors
2. Progress to state machines
3. Implement error handling
4. Build complex simulators
5. Optimize for performance

Happy coding! 🚗📊

