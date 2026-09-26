"""Calculator module with a known bug."""

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def run_calculation():
    result = subtract(10, 4)
    print(f"Subtract result: {result}")
    return result

def calculate_average(numbers):
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

# External developer edit
