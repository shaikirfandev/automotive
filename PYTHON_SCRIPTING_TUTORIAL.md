# Python Scripting Tutorial: From Zero to Hero

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basics](#basics)
4. [Data Types and Variables](#data-types-and-variables)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Functions](#functions)
8. [Data Structures](#data-structures)
9. [Object-Oriented Programming](#object-oriented-programming)
10. [File I/O and Exception Handling](#file-io-and-exception-handling)
11. [Advanced Topics](#advanced-topics)
12. [Best Practices](#best-practices)
13. [Complete Examples](#complete-examples)

---

## Introduction

### What is Python?

**Python** is a high-level, interpreted programming language known for its:

- **Readability** - Clean, intuitive syntax that resembles natural language
- **Versatility** - Used in web development, data science, automation, AI, etc.
- **Ease of Learning** - Perfect for beginners and experts alike
- **Rich Ecosystem** - Thousands of libraries and frameworks

### Why Python?

- **Fast Development** - Write more with less code
- **Cross-platform** - Works on Windows, macOS, Linux
- **Community** - Huge community with libraries for any task
- **Career Prospects** - High demand in industry
- **Data Science** - Industry standard for data analysis and ML

### Before You Start

You'll need:
- **Python 3.8+** installed on your system
- A **text editor** or IDE (VS Code, PyCharm, Thonny)
- Basic computer literacy
- Willingness to practice

### Installation

**Windows:**
1. Download from python.org
2. Run installer
3. Check "Add Python to PATH"

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3
```

**Verify Installation:**
```bash
python3 --version
```

---

## Getting Started

### Step 1: Your First Program

Create a file named `hello.py`:

```python
print("Hello, World!")
```

Run it:
```bash
python3 hello.py
```

Output:
```
Hello, World!
```

### Step 2: Interactive Shell (REPL)

Python's interactive shell is perfect for learning:

```bash
python3
```

```python
>>> 2 + 2
4
>>> print("Hello from Python!")
Hello from Python!
>>> exit()
```

### Step 3: Script Structure

A typical Python script follows this structure:

```python
#!/usr/bin/env python3
"""
Module docstring: Describe what this script does.
"""

# Imports at the top
import sys
from datetime import datetime

# Constants (uppercase)
MAX_RETRIES = 3
DEBUG_MODE = True

# Global variables (with caution)
counter = 0

# Function definitions
def main():
    """Main entry point of the program."""
    print("Program started")
    # Main logic here

# Run main function if this is the entry point
if __name__ == "__main__":
    main()
```

---

## Basics

### Comments

```python
# This is a single-line comment

# Multi-line comment
# can span multiple lines
# just use multiple comment symbols

"""
This is a docstring - used to document modules, 
functions, and classes. It can span multiple lines.
"""
```

### Print Function

```python
# Simple print
print("Hello, World!")

# Multiple values
print("Name:", "Alice", "Age:", 30)

# Using f-strings (Python 3.6+)
name = "Bob"
age = 25
print(f"Name: {name}, Age: {age}")

# Using format() method
print("Name: {}, Age: {}".format("Charlie", 28))

# Using % operator (old style)
print("Name: %s, Age: %d" % ("David", 35))

# Print without newline
print("Loading...", end="")
print(" Done!")  # Prints on same line

# Print with custom separator
print("A", "B", "C", sep="-")  # Output: A-B-C

# Print with custom separator and end
print("X", "Y", "Z", sep="|", end="!\n")  # Output: X|Y|Z!
```

### Input Function

```python
# Get user input (returns string)
name = input("What is your name? ")
print(f"Hello, {name}!")

# Convert to integer
age = int(input("How old are you? "))
print(f"You are {age} years old")

# Convert to float
height = float(input("Your height in meters: "))
print(f"Your height is {height}m")
```

### Variables and Assignment

```python
# Create variables by assignment
x = 10
y = 20
z = x + y

# Multiple assignment
a, b, c = 1, 2, 3
print(a, b, c)  # Output: 1 2 3

# Unpacking
numbers = [10, 20, 30]
first, second, third = numbers

# Multiple assignment (same value)
x = y = z = 0
```

### Naming Conventions

```python
# ✅ Good names
user_age = 25
is_active = True
MAX_CONNECTIONS = 100
PI = 3.14159

# ❌ Avoid these
x = 25           # Too vague
a1a2a3 = 100     # Hard to read
myVariable = 10  # Use snake_case, not camelCase (in Python)
```

---

## Data Types and Variables

### Numeric Types

```python
# Integer
age = 25
temperature = -10
count = 0

# Float (decimal)
price = 19.99
pi = 3.14159
distance = 1.5e-3  # Scientific notation: 0.0015

# Complex numbers
z = 3 + 4j
print(z.real, z.imag)  # Output: 3 4

# Type checking
print(type(age))      # <class 'int'>
print(type(price))    # <class 'float'>
print(type(z))        # <class 'complex'>
```

### Boolean Type

```python
# Boolean values
is_active = True
is_deleted = False

# Boolean expressions
x = 10
print(x > 5)          # True
print(x < 5)          # False
print(x == 10)        # True
print(x != 10)        # False

# Truthiness (non-zero, non-empty evaluates to True)
print(bool(1))        # True
print(bool(0))        # False
print(bool("hello"))  # True
print(bool(""))       # False
print(bool([1, 2]))   # True
print(bool([]))       # False
```

### String Type

```python
# Single or double quotes
name = "Alice"
greeting = 'Hello'

# Multi-line strings
message = """
This is a multi-line
string that spans
multiple lines
"""

# String escape sequences
text = "Hello\nWorld"      # Newline
path = "C:\\Users\\Bob"    # Backslash
quote = "She said \"Hi\""  # Double quote

# Raw strings (skip escape processing)
regex = r"\d+\w+"
path = r"C:\Users\Documents"

# String length
length = len("Hello")      # Output: 5

# String indexing (0-based)
word = "Python"
first = word[0]   # 'P'
last = word[-1]   # 'n'
middle = word[2]  # 't'

# String slicing
word = "Programming"
print(word[0:4])    # "Prog"
print(word[4:11])   # "ramming"
print(word[::2])    # "Pormig" (every 2nd char)
print(word[::-1])   # "gnimmargorP" (reversed)

# String methods
text = "Hello World"
print(text.lower())          # "hello world"
print(text.upper())          # "HELLO WORLD"
print(text.replace("World", "Python"))  # "Hello Python"
print(text.split())          # ['Hello', 'World']
print("hello".capitalize())  # "Hello"
print("  spaces  ".strip())  # "spaces"
print("a-b-c".split("-"))    # ['a', 'b', 'c']

# String formatting
name = "Charlie"
age = 30
print(f"Name: {name}, Age: {age}")
print(f"Next year: {age + 1}")
```

### Type Conversion

```python
# String to integer
age_str = "25"
age = int(age_str)  # 25

# String to float
price_str = "19.99"
price = float(price_str)  # 19.99

# Number to string
num = 42
text = str(num)     # "42"

# To boolean
print(bool(1))      # True
print(bool(0))      # False
print(bool("text")) # True
print(bool(""))     # False

# Between numeric types
x = int(3.14)       # 3
y = float(10)       # 10.0
```

---

## Operators

### Arithmetic Operators

```python
a = 10
b = 3

print(a + b)     # 13 - Addition
print(a - b)     # 7  - Subtraction
print(a * b)     # 30 - Multiplication
print(a / b)     # 3.33... - Division (float)
print(a // b)    # 3 - Floor division (integer)
print(a % b)     # 1 - Modulo (remainder)
print(a ** b)    # 1000 - Exponentiation
```

### Comparison Operators

```python
x = 10
y = 20

print(x == y)    # False - Equal to
print(x != y)    # True - Not equal to
print(x < y)     # True - Less than
print(x > y)     # False - Greater than
print(x <= y)    # True - Less than or equal
print(x >= y)    # False - Greater than or equal
```

### Logical Operators

```python
a = True
b = False

print(a and b)   # False - Both must be True
print(a or b)    # True - At least one True
print(not a)     # False - Inverts boolean

# Short-circuit evaluation
x = 5
print(x > 0 and x < 10)      # True
print(x < 0 or x > 100)      # False
```

### Bitwise Operators

```python
a = 5      # Binary: 0101
b = 3      # Binary: 0011

print(a & b)   # 1 - AND: 0001
print(a | b)   # 7 - OR:  0111
print(a ^ b)   # 6 - XOR: 0110
print(~a)      # -6 - NOT (inverts bits)
print(a << 1)  # 10 - Left shift: 1010
print(a >> 1)  # 2 - Right shift: 0010
```

### Assignment Operators

```python
x = 10

x += 5    # x = 15
x -= 3    # x = 12
x *= 2    # x = 24
x /= 4    # x = 6.0
x //= 2   # x = 3.0
x %= 2    # x = 1.0
x **= 2   # x = 1.0

# Bitwise assignment
x = 5
x &= 3    # x = 1
x |= 2    # x = 3
x ^= 1    # x = 2
x <<= 1   # x = 4
x >>= 1   # x = 2
```

### Membership Operators

```python
# Check if element is in sequence
numbers = [1, 2, 3, 4, 5]

print(3 in numbers)      # True
print(10 in numbers)     # False
print(10 not in numbers) # True

# For strings
text = "Hello World"
print("H" in text)       # True
print("xyz" in text)     # False
```

### Identity Operators

```python
# Check if same object in memory
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)      # True (same value)
print(a is b)      # False (different objects)
print(a is c)      # True (same object)
print(a is not b)  # True
```

### Operator Precedence

```python
# Order of operations (PEMDAS-like)
# 1. Parentheses
# 2. Exponentiation (**)
# 3. Multiplication, Division, Floor Division, Modulo (*, /, //, %)
# 4. Addition, Subtraction (+, -)
# 5. Comparison (==, !=, <, >, <=, >=)
# 6. Membership (in, not in)
# 7. Identity (is, is not)
# 8. Logical NOT (not)
# 9. Logical AND (and)
# 10. Logical OR (or)

result = 2 + 3 * 4      # 14 (multiplication first)
result = (2 + 3) * 4    # 20 (parentheses first)
result = 10 - 3 - 2     # 5 (left to right)
```

---

## Control Flow

### If-Else Statement

```python
age = 20

if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")

# Single statement if
if age >= 18:
    print("Adult")

# No else needed
if condition:
    do_something()

# Multiple conditions
if age >= 18 and age < 65:
    print("Working age")

if age < 13 or age > 65:
    print("Not working age")
```

### Ternary Operator

```python
age = 20
status = "Adult" if age >= 18 else "Minor"
print(status)  # Output: Adult

# Nested ternary
score = 85
grade = "A" if score >= 90 else "B" if score >= 80 else "C"
print(grade)   # Output: B
```

### For Loop

```python
# Loop through range
for i in range(5):
    print(i)  # Output: 0, 1, 2, 3, 4

# Range with start and stop
for i in range(1, 5):
    print(i)  # Output: 1, 2, 3, 4

# Range with step
for i in range(0, 10, 2):
    print(i)  # Output: 0, 2, 4, 6, 8

# Loop through sequence
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Loop through string
for char in "Hello":
    print(char)

# Enumerate (get index and value)
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Loop with break
for i in range(10):
    if i == 5:
        break  # Exit loop
    print(i)

# Loop with continue
for i in range(5):
    if i == 2:
        continue  # Skip to next iteration
    print(i)

# For-else (else runs if loop completes)
for i in range(5):
    if i == 10:
        break
else:
    print("Loop completed normally")
```

### While Loop

```python
count = 0
while count < 5:
    print(count)
    count += 1

# While-else
count = 0
while count < 5:
    count += 1
else:
    print("Loop completed")

# Infinite loop (be careful!)
# while True:
#     print("Running...")
#     if condition:
#         break
```

### Switch-like with Dictionary

```python
# Python 3.10+ has match-case, but here's the dictionary approach
def get_day_name(day):
    days = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    return days.get(day, "Invalid day")

print(get_day_name(1))  # Output: Monday

# With default value
print(get_day_name(10))  # Output: Invalid day
```

### Match-Case (Python 3.10+)

```python
def describe_status(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:  # Default case
            return "Unknown Status"

print(describe_status(200))  # Output: OK
```

---

## Functions

### Basic Function Definition

```python
# Function with no parameters
def greet():
    print("Hello!")

greet()  # Call the function

# Function with parameters
def greet_name(name):
    print(f"Hello, {name}!")

greet_name("Alice")  # Output: Hello, Alice!

# Function with return value
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # Output: 8

# Function with default parameters
def introduce(name, age=25):
    print(f"My name is {name} and I'm {age} years old")

introduce("Bob")           # Uses default age
introduce("Charlie", 30)   # Overrides default
```

### Function Parameters

```python
# Positional parameters
def divide(a, b):
    return a / b

print(divide(10, 2))  # Output: 5.0

# Keyword parameters
print(divide(b=2, a=10))  # Output: 5.0

# Mixed positional and keyword
print(divide(10, b=2))    # Output: 5.0

# Default parameters
def make_coffee(type="espresso", size="medium"):
    print(f"Making {size} {type}")

make_coffee()                    # Making medium espresso
make_coffee("cappuccino")        # Making medium cappuccino
make_coffee("latte", "large")    # Making large latte
make_coffee(size="small")        # Making small espresso

# *args - Variable number of positional arguments
def sum_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3))       # Output: 6
print(sum_all(1, 2, 3, 4, 5)) # Output: 15

# **kwargs - Variable number of keyword arguments
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=30, city="NYC")
# Output:
# name: Alice
# age: 30
# city: NYC

# Combining all parameter types
def complex_function(a, b, *args, c=10, **kwargs):
    print(f"a={a}, b={b}, args={args}, c={c}, kwargs={kwargs}")

complex_function(1, 2, 3, 4, 5, c=20, x="x", y="y")
# Output: a=1, b=2, args=(3, 4, 5), c=20, kwargs={'x': 'x', 'y': 'y'}
```

### Return Values

```python
# Single return value
def square(x):
    return x * x

# Multiple return values (returns tuple)
def get_coordinates():
    return 10, 20

x, y = get_coordinates()
print(x, y)  # Output: 10 20

# Return with tuple unpacking
def get_user():
    return "Alice", 30, "NYC"

name, age, city = get_user()

# Early return
def process_user(age):
    if age < 0:
        return "Invalid age"
    if age < 18:
        return "Minor"
    return "Adult"

# No return statement (returns None)
def do_something():
    print("Doing something...")

result = do_something()
print(result)  # Output: None
```

### Scope

```python
# Global scope
x = 10

def modify_global():
    global x  # Declare to modify global variable
    x = 20

print(x)          # Output: 10
modify_global()
print(x)          # Output: 20

# Local scope
def local_scope():
    y = 30  # Local to function
    print(y)

local_scope()    # Output: 30
# print(y)       # Error: y is not defined in global scope

# Closure - nested function accessing outer scope
def outer():
    x = 10
    
    def inner():
        return x + 5
    
    return inner()

print(outer())   # Output: 15
```

### Docstrings and Type Hints

```python
def add(a: int, b: int) -> int:
    """
    Add two numbers and return the result.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        The sum of a and b
    
    Example:
        >>> add(2, 3)
        5
    """
    return a + b

# Access docstring
print(add.__doc__)
```

### Lambda Functions

```python
# Lambda - anonymous function
square = lambda x: x * x
print(square(5))  # Output: 25

# Lambda with multiple parameters
add = lambda x, y: x + y
print(add(3, 4))  # Output: 7

# Lambda with map
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x * x, numbers))
print(squared)  # Output: [1, 4, 9, 16, 25]

# Lambda with filter
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # Output: [2, 4, 6]

# Lambda with sorted
students = [("Alice", 90), ("Bob", 85), ("Charlie", 92)]
sorted_students = sorted(students, key=lambda x: x[1])
```

---

## Data Structures

### Lists

```python
# Create a list
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]
empty = []

# Access elements (0-indexed)
print(fruits[0])     # "apple"
print(fruits[-1])    # "cherry" (last element)
print(fruits[1:3])   # ["banana", "cherry"]

# Modify elements
fruits[0] = "apricot"
fruits[1] = "blueberry"

# Add elements
fruits.append("date")           # Add to end
fruits.insert(0, "avocado")     # Insert at index
fruits.extend(["elderberry"])   # Add multiple

# Remove elements
fruits.remove("banana")         # Remove by value
popped = fruits.pop()           # Remove and return last
removed = fruits.pop(0)         # Remove by index
fruits.clear()                  # Remove all

# List operations
print(len(fruits))              # Length
print("apple" in fruits)        # Check membership
print(fruits.index("cherry"))   # Get index of element
print(fruits.count("apple"))    # Count occurrences

# List methods
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
numbers.sort()                  # Sort in-place
print(sorted(numbers, reverse=True))  # Sort descending
numbers.reverse()               # Reverse in-place

# List comprehension
squares = [x * x for x in range(1, 6)]
# Output: [1, 4, 9, 16, 25]

evens = [x for x in range(10) if x % 2 == 0]
# Output: [0, 2, 4, 6, 8]

# Nested list comprehension
matrix = [[i * j for j in range(3)] for i in range(3)]
# Output: [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# Unpacking
a, b, c = [1, 2, 3]
first, *middle, last = [1, 2, 3, 4, 5]
# first = 1, middle = [2, 3, 4], last = 5
```

### Tuples

```python
# Create tuple (immutable - can't be modified)
coordinates = (10, 20)
single = (42,)  # Comma needed for single element
empty = ()

# Access elements
print(coordinates[0])    # 10
print(coordinates[-1])   # 20

# Tuple unpacking
x, y = (10, 20)
a, b, c = (1, 2, 3)

# Tuple operations
print(len(coordinates))           # 2
print(10 in coordinates)          # True
print((10, 20).count(10))         # 1
print((1, 2, 3, 2).index(2))      # 1

# Immutability
# coordinates[0] = 30  # Error!

# But lists within tuples can be modified
mixed = (1, [2, 3], 4)
mixed[1][0] = 20  # This works!

# Tuple packing/unpacking
data = (1, 2, 3)
a, b, c = data

# Multiple return values
def get_info():
    return ("Alice", 30, "NYC")
name, age, city = get_info()
```

### Dictionaries

```python
# Create dictionary (key-value pairs)
person = {"name": "Alice", "age": 30, "city": "NYC"}
empty = {}

# Accessing values
print(person["name"])         # "Alice"
print(person.get("age"))      # 30
print(person.get("country", "USA"))  # "USA" (default)

# Modify values
person["age"] = 31
person["job"] = "Engineer"    # Add new key-value

# Delete key-value
del person["city"]
removed = person.pop("job")   # Remove and return value

# Dictionary methods
print(person.keys())          # dict_keys(['name', 'age'])
print(person.values())        # dict_values(['Alice', 31])
print(person.items())         # dict_items([('name', 'Alice'), ...])

# Check key exists
print("name" in person)       # True
print("email" in person)      # False

# Dictionary iteration
for key in person:
    print(f"{key}: {person[key]}")

for key, value in person.items():
    print(f"{key}: {value}")

# Dictionary methods
person.update({"age": 32, "email": "alice@example.com"})
person.clear()                # Remove all items

# Dictionary comprehension
squares = {x: x*x for x in range(1, 6)}
# Output: {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

word_lengths = {word: len(word) for word in ["hello", "world"]}
# Output: {'hello': 5, 'world': 5}

# Nested dictionaries
user = {
    "name": "Bob",
    "age": 28,
    "address": {
        "street": "123 Main St",
        "city": "Boston"
    }
}
print(user["address"]["city"])  # "Boston"
```

### Sets

```python
# Create set (unordered, unique elements)
colors = {"red", "green", "blue"}
numbers = {1, 2, 3, 4, 5}
empty = set()  # Not {}, that's an empty dict

# Add/remove elements
colors.add("yellow")
colors.remove("red")        # Error if not exists
colors.discard("purple")    # No error if not exists
popped = colors.pop()       # Remove arbitrary element
colors.clear()              # Remove all

# Set operations
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

union = set1 | set2         # {1, 2, 3, 4, 5, 6}
intersection = set1 & set2  # {3, 4}
difference = set1 - set2    # {1, 2}
symmetric_diff = set1 ^ set2  # {1, 2, 5, 6}

# Set methods
print(set1.union(set2))
print(set1.intersection(set2))
print(set1.difference(set2))

# Membership
print(3 in set1)            # True
print(10 in set1)           # False

# Set comprehension
squares = {x*x for x in range(1, 6)}
# Output: {1, 4, 9, 16, 25}

# Remove duplicates
duplicates = [1, 2, 2, 3, 3, 3, 4]
unique = set(duplicates)    # {1, 2, 3, 4}
unique = list(unique)       # [1, 2, 3, 4]
```

---

## Object-Oriented Programming

### Classes and Objects

```python
# Define a class
class Dog:
    """A class representing a dog."""
    
    # Class variable (shared by all instances)
    species = "Canis familiaris"
    
    # Constructor
    def __init__(self, name, age):
        # Instance variables
        self.name = name
        self.age = age
    
    # Instance method
    def bark(self):
        return f"{self.name} says Woof!"
    
    def birthday(self):
        self.age += 1
        return f"{self.name} is now {self.age} years old"

# Create objects (instances)
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

# Access attributes
print(dog1.name)           # "Buddy"
print(dog1.age)            # 3
print(dog1.species)        # "Canis familiaris"

# Call methods
print(dog1.bark())         # "Buddy says Woof!"
print(dog2.birthday())     # "Max is now 6 years old"
```

### Inheritance

```python
# Parent class
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} makes a sound"

# Child class inherits from parent
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # Call parent constructor
        self.breed = breed
    
    def speak(self):  # Override parent method
        return f"{self.name} barks"

# Child class 2
class Cat(Animal):
    def speak(self):
        return f"{self.name} meows"

# Usage
dog = Dog("Buddy", "Golden Retriever")
cat = Cat("Whiskers")

print(dog.speak())  # "Buddy barks"
print(cat.speak())  # "Whiskers meows"
```

### Polymorphism

```python
class Shape:
    def area(self):
        raise NotImplementedError("Subclass must implement area()")

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

# Polymorphic behavior
shapes = [Circle(5), Rectangle(4, 6)]

for shape in shapes:
    print(f"Area: {shape.area()}")
```

### Encapsulation

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance  # Private (name mangling)
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return f"Deposited ${amount}"
        return "Invalid amount"
    
    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return f"Withdrew ${amount}"
        return "Insufficient funds"
    
    def get_balance(self):
        return self.__balance

account = BankAccount("Alice", 1000)
print(account.deposit(500))         # Deposited $500
print(account.withdraw(200))        # Withdrew $200
print(account.get_balance())        # 1300
# print(account.__balance)          # Error - private
```

### Properties and Getters/Setters

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("Radius must be positive")
        self._radius = value
    
    @property
    def area(self):
        return 3.14 * self._radius ** 2

circle = Circle(5)
print(circle.radius)          # 5
print(circle.area)            # 78.5

circle.radius = 10
print(circle.area)            # 314.0

# circle.radius = -5           # Error!
```

### Static Methods and Class Methods

```python
class MathUtils:
    # Static method - doesn't access instance or class
    @staticmethod
    def add(a, b):
        return a + b
    
    # Class method - receives class as first argument
    @classmethod
    def multiply(cls, a, b):
        return a * b
    
    @classmethod
    def from_string(cls, value):
        return cls(float(value))

# Call without creating instance
print(MathUtils.add(5, 3))        # 8
print(MathUtils.multiply(5, 3))   # 15
```

### Magic Methods (Dunder Methods)

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __str__(self):
        return f"{self.name}, {self.age} years old"
    
    def __repr__(self):
        return f"Person('{self.name}', {self.age})"
    
    def __eq__(self, other):
        return self.age == other.age
    
    def __lt__(self, other):
        return self.age < other.age
    
    def __len__(self):
        return self.age
    
    def __getitem__(self, index):
        return (self.name, self.age)[index]

person = Person("Alice", 30)
print(str(person))           # "Alice, 30 years old"
print(repr(person))          # "Person('Alice', 30)"
print(len(person))           # 30

person2 = Person("Bob", 25)
print(person == person2)     # False
print(person > person2)      # True
```

---

## File I/O and Exception Handling

### Reading Files

```python
# Read entire file
with open("data.txt", "r") as file:
    content = file.read()
    print(content)

# Read line by line
with open("data.txt", "r") as file:
    for line in file:
        print(line.strip())

# Read all lines into list
with open("data.txt", "r") as file:
    lines = file.readlines()
    print(lines[0])

# Read specific number of characters
with open("data.txt", "r") as file:
    first_100 = file.read(100)
```

### Writing Files

```python
# Write to file (overwrites)
with open("output.txt", "w") as file:
    file.write("Hello, World!\n")
    file.write("Python is great!")

# Append to file
with open("output.txt", "a") as file:
    file.write("\nAdding more content\n")

# Write multiple lines
lines = ["Line 1\n", "Line 2\n", "Line 3\n"]
with open("output.txt", "w") as file:
    file.writelines(lines)
```

### Working with JSON

```python
import json

# Write JSON
data = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

with open("user.json", "w") as file:
    json.dump(data, file, indent=4)

# Read JSON
with open("user.json", "r") as file:
    loaded_data = json.load(file)
    print(loaded_data["name"])  # "Alice"

# JSON strings
json_string = json.dumps(data)
back_to_dict = json.loads(json_string)
```

### CSV Files

```python
import csv

# Write CSV
data = [
    ["Name", "Age", "City"],
    ["Alice", 30, "NYC"],
    ["Bob", 25, "LA"],
    ["Charlie", 35, "Chicago"]
]

with open("people.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(data)

# Read CSV
with open("people.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)

# Read as dictionaries
with open("people.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row["Name"], row["Age"])
```

### Exception Handling

```python
# Try-except
try:
    x = int("abc")  # Will raise ValueError
except ValueError:
    print("Invalid number format")

# Multiple except blocks
try:
    result = 10 / 0
except ValueError:
    print("Value error")
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Unexpected error: {e}")

# Else clause (runs if no exception)
try:
    x = int("123")
except ValueError:
    print("Invalid input")
else:
    print(f"Number is {x}")

# Finally clause (always runs)
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found")
finally:
    if 'file' in locals():
        file.close()

# Raising exceptions
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age

# Custom exception
class InvalidUserError(Exception):
    pass

def create_user(name, age):
    if not name or age < 0:
        raise InvalidUserError("Invalid user data")
    return {"name": name, "age": age}
```

---

## Advanced Topics

### List, Dict, and Set Comprehensions

```python
# List comprehension
squares = [x**2 for x in range(1, 6)]  # [1, 4, 9, 16, 25]
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]

# Nested comprehension
matrix = [[i+j for j in range(3)] for i in range(3)]

# Dictionary comprehension
word_len = {w: len(w) for w in ["hello", "world"]}  # {'hello': 5, 'world': 5}
squares_dict = {x: x**2 for x in range(1, 4)}  # {1: 1, 2: 4, 3: 9}

# Set comprehension
unique_lengths = {len(w) for w in ["hello", "world", "hi"]}  # {2, 5}
```

### Decorators

```python
# Simple decorator
def my_decorator(func):
    def wrapper():
        print("Something before function")
        func()
        print("Something after function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Something before function
# Hello!
# Something after function

# Decorator with arguments
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")
# Output:
# Hello, Alice!
# Hello, Alice!
# Hello, Alice!

# Decorator with functools.wraps
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(1)
```

### Generators

```python
# Generator function - uses yield
def count_up(n):
    i = 0
    while i < n:
        yield i
        i += 1

# Use generator
for num in count_up(5):
    print(num)  # Output: 0, 1, 2, 3, 4

# Generator expression (like list comprehension but lazy)
squares = (x**2 for x in range(1000000))  # Not computed until needed
print(next(squares))  # 0
print(next(squares))  # 1

# Generator with send
def echo():
    value = None
    while True:
        value = (yield value)

gen = echo()
next(gen)
print(gen.send("Hello"))  # Print and echo back "Hello"
```

### Iterators and Iterables

```python
# Custom iterator
class CountUp:
    def __init__(self, n):
        self.current = 0
        self.n = n
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current < self.n:
            self.current += 1
            return self.current
        else:
            raise StopIteration

# Use custom iterator
for num in CountUp(5):
    print(num)

# zip - combine iterables
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name}: {age}")

# enumerate - get index and value
for i, name in enumerate(names):
    print(f"{i}: {name}")

# map - apply function to each element
squared = list(map(lambda x: x**2, [1, 2, 3, 4]))

# filter - keep elements matching condition
evens = list(filter(lambda x: x % 2 == 0, range(10)))
```

### Context Managers

```python
# Using with statement (context manager)
with open("file.txt", "r") as file:
    content = file.read()
# File is automatically closed

# Custom context manager
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# Using custom context manager
with FileManager("data.txt", "r") as f:
    content = f.read()

# Using contextlib decorator
from contextlib import contextmanager

@contextmanager
def temporary_value(value):
    print(f"Setting up {value}")
    yield value
    print(f"Cleaning up {value}")

with temporary_value("resource") as val:
    print(f"Using {val}")
```

### Modules and Packages

```python
# Import module
import math
print(math.pi)

# Import specific function
from math import sqrt
print(sqrt(16))

# Import with alias
import numpy as np
from datetime import datetime as dt

# Import everything (use with caution)
# from module import *

# Create module (save as mymodule.py)
# def greet(name):
#     return f"Hello, {name}!"

# Use module
# import mymodule
# print(mymodule.greet("Alice"))

# __name__ == '__main__' pattern
# if __name__ == "__main__":
#     # Code here runs only when script is executed directly
#     print("Running as main script")
```

---

## Best Practices

### 1. Follow PEP 8 Style Guide

```python
# ✅ Good - follows PEP 8
def calculate_total_price(items):
    """Calculate total price of items."""
    total = 0
    for item in items:
        total += item["price"]
    return total

# ❌ Bad - doesn't follow conventions
def calculateTotalPrice(items):
    total=0
    for item in items:
        total+=item['price']
    return total

# PEP 8 key points:
# - Use 4 spaces for indentation
# - Max 79 characters per line
# - Use snake_case for variables and functions
# - Use UPPERCASE for constants
# - Two blank lines between top-level functions
# - One blank line between methods in a class
```

### 2. Use Meaningful Names

```python
# ❌ Bad
def f(x):
    return x * x

data = [1, 2, 3]
for i in data:
    print(i)

# ✅ Good
def calculate_square(number):
    return number * number

numbers = [1, 2, 3]
for number in numbers:
    print(number)
```

### 3. Keep Functions Small and Focused

```python
# ❌ Bad - doing too many things
def process_user_data(user_id):
    user = fetch_user(user_id)
    user['email_verified'] = verify_email(user['email'])
    user['phone_verified'] = verify_phone(user['phone'])
    save_to_database(user)
    send_notification(user)
    generate_report(user)
    # ... more code

# ✅ Good - single responsibility
def update_user_verification(user):
    verify_email(user)
    verify_phone(user)
    save_user(user)

def process_user(user_id):
    user = fetch_user(user_id)
    update_user_verification(user)
    notify_user(user)
```

### 4. Use Type Hints

```python
# ✅ Good - type hints improve clarity
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

def greet(name: str, age: int) -> str:
    """Create a greeting message."""
    return f"Hello {name}, you are {age} years old"

# Optional types
from typing import Optional, List, Dict

def find_user(user_id: int) -> Optional[Dict]:
    # Returns a dict or None
    pass

def process_items(items: List[str]) -> None:
    # Takes a list of strings, returns nothing
    for item in items:
        print(item)
```

### 5. Handle Exceptions Properly

```python
# ❌ Bad - too broad
try:
    result = 10 / 0
except:
    pass

# ✅ Good - specific exception handling
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 6. Use Constants for Magic Numbers

```python
# ❌ Bad
def is_adult(age):
    return age >= 18

def can_drive(age):
    return age >= 16

# ✅ Good
ADULT_AGE = 18
DRIVING_AGE = 16

def is_adult(age):
    return age >= ADULT_AGE

def can_drive(age):
    return age >= DRIVING_AGE
```

### 7. Document Your Code

```python
def fibonacci(n: int) -> List[int]:
    """
    Generate Fibonacci sequence up to n terms.
    
    Args:
        n: Number of Fibonacci terms to generate
    
    Returns:
        List of Fibonacci numbers
    
    Raises:
        ValueError: If n is negative
    
    Example:
        >>> fibonacci(5)
        [0, 1, 1, 2, 3]
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n == 0:
        return []
    
    fib_list = [0, 1]
    for i in range(2, n):
        fib_list.append(fib_list[-1] + fib_list[-2])
    
    return fib_list[:n]
```

### 8. Use List Comprehensions

```python
# ❌ Less Pythonic
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x ** 2)

# ✅ More Pythonic
squares = [x**2 for x in range(10) if x % 2 == 0]
```

### 9. Avoid Mutable Default Arguments

```python
# ❌ Bad - mutable default is shared
def add_item(item, items=[]):
    items.append(item)
    return items

# add_item(1)      # [1]
# add_item(2)      # [1, 2] - unexpected!

# ✅ Good - use None as default
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 10. Use Virtual Environments

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate    # On Windows

# Install packages
pip install package_name

# Create requirements file
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Deactivate
deactivate
```

---

## Complete Examples

### Example 1: Simple Calculator

```python
"""
Simple Calculator
Supports basic arithmetic operations
"""

def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract b from a."""
    return a - b

def multiply(a, b):
    """Multiply two numbers."""
    return a * b

def divide(a, b):
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def calculator():
    """Main calculator function."""
    print("Simple Calculator")
    print("-" * 30)
    
    while True:
        print("\nOperations: +, -, *, /, quit")
        operation = input("Choose operation: ").strip()
        
        if operation.lower() == "quit":
            print("Goodbye!")
            break
        
        if operation not in ["+", "-", "*", "/"]:
            print("Invalid operation")
            continue
        
        try:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
        except ValueError:
            print("Invalid input")
            continue
        
        try:
            if operation == "+":
                result = add(a, b)
            elif operation == "-":
                result = subtract(a, b)
            elif operation == "*":
                result = multiply(a, b)
            elif operation == "/":
                result = divide(a, b)
            
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    calculator()
```

### Example 2: Todo List Application

```python
"""
Simple Todo List Application
"""

class TodoList:
    def __init__(self):
        self.todos = []
    
    def add_todo(self, task):
        """Add a new todo."""
        todo = {"task": task, "done": False}
        self.todos.append(todo)
        print(f"Added: {task}")
    
    def mark_done(self, index):
        """Mark todo as done."""
        if 0 <= index < len(self.todos):
            self.todos[index]["done"] = True
            print(f"Marked done: {self.todos[index]['task']}")
        else:
            print("Invalid index")
    
    def remove_todo(self, index):
        """Remove a todo."""
        if 0 <= index < len(self.todos):
            removed = self.todos.pop(index)
            print(f"Removed: {removed['task']}")
        else:
            print("Invalid index")
    
    def list_todos(self):
        """Display all todos."""
        if not self.todos:
            print("No todos!")
            return
        
        print("\n" + "=" * 40)
        for i, todo in enumerate(self.todos):
            status = "✓" if todo["done"] else "○"
            print(f"{i}. [{status}] {todo['task']}")
        print("=" * 40)
    
    def get_pending(self):
        """Get count of pending todos."""
        return sum(1 for todo in self.todos if not todo["done"])

def main():
    """Main application loop."""
    todos = TodoList()
    
    while True:
        print("\n1. Add    2. Done    3. Remove    4. List    5. Exit")
        choice = input("Choose: ").strip()
        
        if choice == "1":
            task = input("Enter task: ").strip()
            if task:
                todos.add_todo(task)
        
        elif choice == "2":
            todos.list_todos()
            try:
                index = int(input("Mark todo done (index): "))
                todos.mark_done(index)
            except ValueError:
                print("Invalid input")
        
        elif choice == "3":
            todos.list_todos()
            try:
                index = int(input("Remove todo (index): "))
                todos.remove_todo(index)
            except ValueError:
                print("Invalid input")
        
        elif choice == "4":
            todos.list_todos()
            print(f"Pending: {todos.get_pending()}/{len(todos.todos)}")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
```

### Example 3: Data Analysis Example

```python
"""
Simple Data Analysis Script
Analyze student grades
"""

class StudentGrades:
    def __init__(self):
        self.grades = {}
    
    def add_student(self, name: str, grades: List[float]) -> None:
        """Add student and their grades."""
        self.grades[name] = grades
    
    def get_average(self, name: str) -> float:
        """Get student's average grade."""
        if name not in self.grades:
            raise ValueError(f"Student {name} not found")
        return sum(self.grades[name]) / len(self.grades[name])
    
    def get_highest(self, name: str) -> float:
        """Get student's highest grade."""
        if name not in self.grades:
            raise ValueError(f"Student {name} not found")
        return max(self.grades[name])
    
    def get_lowest(self, name: str) -> float:
        """Get student's lowest grade."""
        if name not in self.grades:
            raise ValueError(f"Student {name} not found")
        return min(self.grades[name])
    
    def get_class_average(self) -> float:
        """Get average for entire class."""
        if not self.grades:
            return 0
        all_grades = [g for grades in self.grades.values() for g in grades]
        return sum(all_grades) / len(all_grades)
    
    def get_top_student(self) -> str:
        """Get student with highest average."""
        if not self.grades:
            return ""
        return max(self.grades.keys(), key=lambda s: self.get_average(s))
    
    def print_report(self) -> None:
        """Print detailed report."""
        print("\n" + "=" * 50)
        print("GRADE REPORT".center(50))
        print("=" * 50)
        
        for name in sorted(self.grades.keys()):
            avg = self.get_average(name)
            print(f"\n{name}:")
            print(f"  Average: {avg:.2f}")
            print(f"  Highest: {self.get_highest(name):.2f}")
            print(f"  Lowest:  {self.get_lowest(name):.2f}")
        
        print("\n" + "-" * 50)
        print(f"Class Average: {self.get_class_average():.2f}")
        print(f"Top Student: {self.get_top_student()}")
        print("=" * 50 + "\n")

def main():
    """Main function."""
    grades = StudentGrades()
    
    # Add students
    grades.add_student("Alice", [95, 87, 92, 88])
    grades.add_student("Bob", [78, 82, 80, 85])
    grades.add_student("Charlie", [92, 95, 97, 94])
    grades.add_student("Diana", [88, 90, 89, 91])
    
    # Print report
    grades.print_report()
    
    # Get individual info
    print(f"Alice's average: {grades.get_average('Alice'):.2f}")
    print(f"Bob's highest: {grades.get_highest('Bob'):.2f}")

if __name__ == "__main__":
    main()
```

### Example 4: File Processing Example

```python
"""
Log File Analysis
Analyze and process log files
"""

import re
from collections import Counter
from typing import List, Dict

class LogAnalyzer:
    def __init__(self, filename: str):
        self.filename = filename
        self.logs = []
    
    def parse_logs(self) -> None:
        """Parse log file."""
        try:
            with open(self.filename, "r") as f:
                for line in f:
                    log_entry = self.parse_line(line.strip())
                    if log_entry:
                        self.logs.append(log_entry)
        except FileNotFoundError:
            print(f"File {self.filename} not found")
    
    def parse_line(self, line: str) -> Dict:
        """Parse a single log line."""
        # Format: [TIMESTAMP] LEVEL MESSAGE
        pattern = r'\[(.+?)\] (\w+) (.+)'
        match = re.match(pattern, line)
        
        if match:
            return {
                "timestamp": match.group(1),
                "level": match.group(2),
                "message": match.group(3)
            }
        return None
    
    def get_level_counts(self) -> Dict[str, int]:
        """Count logs by level."""
        return Counter(log["level"] for log in self.logs)
    
    def filter_by_level(self, level: str) -> List[Dict]:
        """Get logs by level."""
        return [log for log in self.logs if log["level"] == level]
    
    def search_message(self, keyword: str) -> List[Dict]:
        """Search logs by keyword."""
        return [log for log in self.logs if keyword.lower() in log["message"].lower()]
    
    def generate_report(self) -> None:
        """Generate analysis report."""
        print("\n" + "=" * 50)
        print("LOG ANALYSIS REPORT".center(50))
        print("=" * 50)
        
        print(f"\nTotal logs: {len(self.logs)}")
        
        print("\nLevel Distribution:")
        for level, count in self.get_level_counts().items():
            percentage = (count / len(self.logs)) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")
        
        print("\nSample Logs:")
        for log in self.logs[:5]:
            print(f"  [{log['timestamp']}] {log['level']}: {log['message']}")
        
        print("\n" + "=" * 50 + "\n")

def main():
    """Main function."""
    # Create sample log file
    sample_logs = [
        "[2024-01-01 10:00:01] INFO Application started",
        "[2024-01-01 10:00:02] DEBUG Initializing database",
        "[2024-01-01 10:00:03] WARNING Low memory detected",
        "[2024-01-01 10:00:04] ERROR Failed to connect to server",
        "[2024-01-01 10:00:05] INFO User logged in"
    ]
    
    with open("app.log", "w") as f:
        for log in sample_logs:
            f.write(log + "\n")
    
    # Analyze logs
    analyzer = LogAnalyzer("app.log")
    analyzer.parse_logs()
    analyzer.generate_report()
    
    # Search
    errors = analyzer.filter_by_level("ERROR")
    print(f"Found {len(errors)} error logs")

if __name__ == "__main__":
    main()
```

---

## Tips & Tricks

### Useful Built-in Functions

```python
# abs() - absolute value
print(abs(-5))  # 5

# all(), any() - check collections
print(all([True, True, True]))  # True
print(any([False, False, True]))  # True

# sorted() - sort any iterable
print(sorted([3, 1, 2]))  # [1, 2, 3]
print(sorted("hello"))  # ['e', 'h', 'l', 'l', 'o']

# zip() - combine iterables
list(zip([1, 2], ['a', 'b']))  # [(1, 'a'), (2, 'b')]

# enumerate() - with index
list(enumerate(['a', 'b','c']))  # [(0, 'a'), (1, 'b'), (2, 'c')]

# reversed() - reverse order
list(reversed([1, 2, 3]))  # [3, 2, 1]

# sum() - sum elements
print(sum([1, 2, 3, 4]))  # 10

# min(), max() - find extremes
print(min([3, 1, 2]))  # 1
print(max([3, 1, 2]))  # 3

# round() - round numbers
print(round(3.7))  # 4
print(round(3.14159, 2))  # 3.14

# isinstance() - check type
print(isinstance(5, int))  # True
print(isinstance("hello", str))  # True
```

### Common Patterns

```python
# Dictionary with default value
contacts = {}
contacts.setdefault("Alice", {})["phone"] = "555-1234"

# Count items
from collections import Counter
items = ["a", "b", "a", "c", "a", "b"]
counts = Counter(items)  # Counter({'a': 3, 'b': 2, 'c': 1})

# Group items
from itertools import groupby
people = [("Alice", 30), ("Bob", 25), ("Charlie", 30)]
for age, group in groupby(sorted(people, key=lambda x: x[1]), key=lambda x: x[1]):
    print(f"{age}: {list(group)}")

# Flatten list
nested = [[1, 2], [3, 4], [5, 6]]
flat = [x for sublist in nested for x in sublist]

# Unique elements while preserving order
seen = set()
unique = [x for x in items if not (x in seen or seen.add(x))]
```

---

## Conclusion

You've now learned Python from zero to hero! Key takeaways:

1. **Master the basics** - Variables, types, operators, control flow
2. **Understand functions** - DRY principle, reusability
3. **Use data structures** - Lists, dicts, sets, tuples
4. **Apply OOP** - Classes, inheritance, polymorphism
5. **Handle errors** - Try-except, proper error handling
6. **Write Pythonic code** - Comprehensions, context managers
7. **Follow best practices** - Clear naming, documentation, testing

### Next Steps

1. Build small scripts for automation
2. Create command-line tools
3. Develop web applications (Flask, Django)
4. Explore data science (NumPy, Pandas)
5. Machine learning (Scikit-learn, TensorFlow)
6. Contribute to open-source projects

### Useful Resources

- **Official Python Documentation**: python.org/docs
- **PEP 8**: Style guide for Python code
- **PyPI**: Repository of Python packages
- **Stack Overflow**: Q&A for programming
- **Real Python**: Comprehensive tutorials

Happy coding! 🐍✨

