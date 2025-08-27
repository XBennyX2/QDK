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


def prepare_state(bit: int, basis: str) -> QuantumCircuit:
    """Return a QuantumCircuit(1,1) preparing 'bit' in basis 'Z' or 'X'."""
    qc = QuantumCircuit(1, 1)
    if basis == 'Z':
        if bit == 1:
            qc.x(0)
    elif basis == 'X':
        if bit == 0:
            qc.h(0)         # |+>
        else:
            qc.x(0)
            qc.h(0)         # |->
    else:
        raise ValueError("basis must be 'Z' or 'X'")
    return qc

def measure_in_basis(qc_prep: QuantumCircuit, basis: str) -> int:
    """
    Measure the prepared circuit qc_prep in basis 'Z' or 'X'.
    Returns measured bit (0 or 1).
    """
    qc = qc_prep.copy()
    if basis == 'X':
        qc.h(0)
    qc.measure(0, 0)
    job = simulator.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    # single-shot => one key in counts
    bitstr = list(counts.keys())[0]
    return int(bitstr)

