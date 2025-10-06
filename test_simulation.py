"""
Test script to run the simulation with predefined parameters.
This helps verify the simulation runs correctly without manual input.
"""

import subprocess
import sys

# Predefined inputs for the simulation
inputs = [
    "5",    # Number of customers
    "2",    # Number of employees  
    "20",   # Number of books
    "30"    # Number of steps (increased to 30)
]

# Join inputs with newlines
input_data = "\n".join(inputs) + "\n"

# Run the simulation
process = subprocess.Popen(
    [sys.executable, "gui/run_simulation.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send inputs and get output
stdout, stderr = process.communicate(input=input_data)

# Print output
print(stdout)

# Print errors if any
if stderr:
    print("ERRORS:")
    print(stderr)

# Exit with the same code as the subprocess
sys.exit(process.returncode)
