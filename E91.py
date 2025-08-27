import random
import hashlib
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from math import pi


N = 200                    # Number of entangled pairs
SAMPLE_FRACTION = 0.25     # Fraction of sifted key revealed for QBER estimation
QBER_THRESHOLD = 0.11      # Threshold to abort
EVE_ENABLED = True        # Toggle Eve on/off
PRINT_EXAMPLE = 40

simulator = AerSimulator()

