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

def measure_bell_pair(qc: QuantumCircuit, angle_A: float, angle_B: float):
    """
    Measure both qubits in their respective rotated bases simultaneously.
    Returns (bit_A, bit_B)
    """
    qc_r = qc.copy()
    qc_r.ry(-2*angle_A, 0)
    qc_r.ry(-2*angle_B, 1)
    qc_r.measure([0,1], [0,1])
    job = simulator.run(qc_r, shots=1)
    counts = job.result().get_counts()
    bits = list(counts.keys())[0]
    # Qiskit counts in little-endian: bits[0] = qubit 1, bits[1] = qubit 0
    return int(bits[1]), int(bits[0])  # (A,B)

def privacy_amplify_sha256(bitstring: str) -> str:
    """Demo: compress bitstring using SHA-256"""
    if not bitstring:
        return ''
    b = int(bitstring, 2).to_bytes((len(bitstring) + 7) // 8, 'big')
    return hashlib.sha256(b).hexdigest()

# 1) Generate entangled pairs & choose measurement angles
angles_A = [random.choice([0, pi/4, pi/2]) for _ in range(N)]
angles_B = [random.choice([pi/4, pi/2, 3*pi/4]) for _ in range(N)]

results_A = []
results_B = []
eve_results = []
eve_angles = []

print("=== TRANSMISSION & MEASUREMENT ===")
for i in range(N):
    qc = prepare_bell_pair()

    # Eve intercepts B's qubit
    if EVE_ENABLED:
        eve_angle = random.choice([pi/4, pi/2, 3*pi/4])
        eve_angles.append(eve_angle)
        # Measure B's qubit alone
        qc_eve = qc.copy()
        qc_eve.ry(-2*eve_angle, 1)
        qc_eve.measure(1,1)
        job = simulator.run(qc_eve, shots=1)
        eve_meas = int(list(job.result().get_counts().keys())[0])
        eve_results.append(eve_meas)
        # Eve resends B’s qubit
        qc = QuantumCircuit(2,2)
        if eve_meas == 1:
            qc.x(1)

    # Measure both qubits simultaneously
    a_meas, b_meas = measure_bell_pair(qc, angles_A[i], angles_B[i])
    results_A.append(a_meas)
    results_B.append(b_meas)

    # Print first examples
    if i < PRINT_EXAMPLE:
        if EVE_ENABLED:
            print(f"{i:03d}: Angle A={angles_A[i]:.2f}, Angle B={angles_B[i]:.2f} | EveAngle={eve_angles[i]:.2f}, EveMeas={eve_results[i]} -> A={a_meas}, B={b_meas}")
        else:
            print(f"{i:03d}: Angle A={angles_A[i]:.2f}, Angle B={angles_B[i]:.2f} -> A={a_meas}, B={b_meas}")

# 2) SIFTING: keep only pairs where bases match
sift_positions = [i for i in range(N) if angles_A[i] == angles_B[i]]
sifted_A = [results_A[i] for i in sift_positions]
sifted_B = [results_B[i] for i in sift_positions]

print("\n=== SIFTING ===")
print(f"Sifted key positions (first 40): {sift_positions[:PRINT_EXAMPLE]}")
print(f"Sifted key length: {len(sifted_A)}")

# 3) Parameter estimation: reveal a sample
sift_len = len(sifted_A)
if sift_len == 0:
    raise RuntimeError("No sifted bits. Increase N or adjust angles.")

sample_size = max(1, int(SAMPLE_FRACTION * sift_len))
sample_indices = random.sample(range(sift_len), sample_size)
mismatches = sum(1 for idx in sample_indices if sifted_A[idx] != sifted_B[idx])
QBER = mismatches / sample_size

print("\n=== PARAMETER ESTIMATION ===")
print(f"Sample size: {sample_size}, Mismatches: {mismatches}, QBER: {QBER*100:.2f}%")

# Remove sample bits from key
remaining_indices = [i for i in range(sift_len) if i not in sample_indices]
raw_A_key = ''.join(str(sifted_A[i]) for i in remaining_indices)
raw_B_key = ''.join(str(sifted_B[i]) for i in remaining_indices)

# 4) Decision and privacy amplification
print("\n=== DECISION ===")
if QBER > QBER_THRESHOLD:
    print(f"QBER ({QBER*100:.2f}%) exceeds threshold ({QBER_THRESHOLD*100:.2f}%). ABORT: possible eavesdropping.")
else:
    print(f"QBER ({QBER*100:.2f}%) within threshold. Proceed.")
    final_key_hex = privacy_amplify_sha256(raw_A_key)
    print("Demo final key (SHA-256 hex):", final_key_hex)

# SUMMARY
total_mismatches_full = sum(1 for a,b in zip(sifted_A, sifted_B) if a != b)
full_qber = total_mismatches_full / sift_len
print("\n=== SUMMARY ===")
print(f"Sifted bits: {sift_len}")
print(f"Total mismatches (full): {total_mismatches_full}")
print(f"Full QBER: {full_qber*100:.2f}%")
if EVE_ENABLED:
    print("Note: With Eve intercept-resend, QBER is expected to increase (~25%).")
else:
    print("Note: With no Eve, QBER should be ~0% (only simulator noise).")

print("\nEnd of E91 simulation.")
