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


def prepare_bell_pair() -> QuantumCircuit:
    """Prepare a Bell state |Φ+>"""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    return qc

