import random
import hashlib
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


N = 200                    # number of qubits A sends
SAMPLE_FRACTION = 0.25     # fraction of sifted key revealed for QBER estimation
QBER_THRESHOLD = 0.11      # threshold to abort (illustrative)
EVE_ENABLED = False         # toggle Eve on/off
PRINT_EXAMPLE = 40         # how many transmissions to print in detail

simulator = AerSimulator()


