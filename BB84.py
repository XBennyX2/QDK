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

def privacy_amplify_sha256(bitstring: str) -> str:
    """Simple demo: compress bitstring with SHA-256 (not real universal hashing)."""
    if not bitstring:
        return ''
    b = int(bitstring, 2).to_bytes((len(bitstring) + 7) // 8, 'big')
    return hashlib.sha256(b).hexdigest()


# 1) A: random bits & bases
A_bits = [random.randint(0, 1) for _ in range(N)]
A_bases = [random.choice(['Z', 'X']) for _ in range(N)]

# Print A's choices (partial)
print("=== A: preparation ===")
print(f"Total qubits to send: {N}")
print("First 40 A bits & bases (index: bit, basis):")
for i in range(min(PRINT_EXAMPLE, N)):
    print(f"{i:03d}: {A_bits[i]}, {A_bases[i]}")
print("...")

# 2) Transmission with optional Eve
B_bases = [random.choice(['Z', 'X']) for _ in range(N)]
B_results = [None] * N
eve_bases = [None] * N
eve_results = [None] * N  # only filled when Eve present

print("\n=== TRANSMISSION (A -> channel -> B). Eve enabled:", EVE_ENABLED, ") ===")

for i in range(N):
    # A prepares
    qc_A = prepare_state(A_bits[i], A_bases[i])

    if EVE_ENABLED:
        # Eve intercepts the qubit
        eve_basis = random.choice(['Z', 'X'])
        eve_bases[i] = eve_basis
        eve_meas = measure_in_basis(qc_A, eve_basis)   # Eve measures -> collapse
        eve_results[i] = eve_meas

        # Eve resends a newly prepared qubit based on her measurement outcome & basis
        qc_after_eve = prepare_state(eve_meas, eve_basis)
        # B measures the resent qubit
        B_meas = measure_in_basis(qc_after_eve, B_bases[i])
        B_results[i] = B_meas
    else:
        # No Eve: B measures A's prepared qubit directly
        B_meas = measure_in_basis(qc_A, B_bases[i])
        B_results[i] = B_meas

# Print some examples of transmission results
print("\nFirst 40 transmissions (index: A_bit A_basis | EveBasis EveMeas | B_basis B_meas):")
for i in range(min(PRINT_EXAMPLE, N)):
    a_bit = A_bits[i]
    a_basis = A_bases[i]
    if EVE_ENABLED:
        e_basis = eve_bases[i]
        e_meas = eve_results[i]
    else:
        e_basis = e_meas = '-'
    b_basis = B_bases[i]
    b_meas = B_results[i]
    print(f"{i:03d}: {a_bit} {a_basis} | {e_basis} {e_meas} | {b_basis} {b_meas}")

# -----------------------------
# 3) Sifting: basis reconciliation
# -----------------------------
sift_positions = [i for i in range(N) if A_bases[i] == B_bases[i]]
sifted_A = [A_bits[i] for i in sift_positions]
sifted_B   = [B_results[i] for i in sift_positions]

print("\n=== SIFTING ===")
print(f"Total sent: {N}")
print(f"Positions where A and B used same basis (sifted): {len(sift_positions)}")
print("Sifted indices (first 40):", sift_positions[:40])

# -----------------------------
# 4) Parameter estimation: reveal sample, compute QBER
# -----------------------------
sift_len = len(sifted_A)
if sift_len == 0:
    raise RuntimeError("No sifted bits. Increase N or check code.")

sample_size = max(1, int(SAMPLE_FRACTION * sift_len))
sample_indices = random.sample(range(sift_len), sample_size)

# compute mismatches on sample
mismatches = sum(1 for idx in sample_indices if sifted_A[idx] != sifted_B[idx])
QBER = mismatches / sample_size

print("\n=== PARAMETER ESTIMATION ===")
print(f"Sifted key length         : {sift_len}")
print(f"Sample size (to reveal)  : {sample_size}")
print(f"Mismatches in sample      : {mismatches}")
print(f"Measured QBER (sample)    : {QBER*100:.2f}%")

# Remove sample bits from key (they were revealed)
remaining_indices = [i for i in range(sift_len) if i not in sample_indices]
raw_A_key = ''.join(str(sifted_A[i]) for i in remaining_indices)
raw_B_key   = ''.join(str(sifted_B[i])   for i in remaining_indices)

# -----------------------------
# 5) Decision and demo privacy amplification
# -----------------------------
print("\n=== DECISION ===")
if QBER > QBER_THRESHOLD:
    print(f"QBER ({QBER*100:.2f}%) exceeds threshold ({QBER_THRESHOLD*100:.2f}%). ABORT: possible eavesdropping.")
else:
    print(f"QBER ({QBER*100:.2f}%) within threshold ({QBER_THRESHOLD*100:.2f}%). Proceed.")

    # NOTE: Error correction (reconciliation) is required in practice. Here we only demo.
    if raw_A_key == raw_B_key:
        print("Raw keys already match (no error-correction needed).")
    else:
        print("Raw keys differ (error-correction would be required in practice).")
        # For a toy demonstration we won't implement full error-correction here.

    print(f"Raw key length (after removing sample): {len(raw_A_key)}")
    # Privacy-amplify (demo with SHA-256)
    final_key_hex = privacy_amplify_sha256(raw_A_key)
    print("Demo final key (SHA-256 hex of raw key):", final_key_hex)

# -----------------------------
# Summary statistics and notes
# -----------------------------
total_mismatches_full = sum(1 for a,b in zip(sifted_A, sifted_B) if a != b)
full_qber = total_mismatches_full / sift_len
print("\n=== SUMMARY ===")
print(f"Sifted bits             : {sift_len}")
print(f"Total mismatches (full) : {total_mismatches_full}")
print(f"Full QBER (sifted)      : {full_qber*100:.2f}%")
if EVE_ENABLED:
    print("Note: With intercept-resend Eve, expected QBER ~25% (ideal model).")
else:
    print("Note: With no Eve, QBER should be ~0% (only finite-shot noise).")

print("\nEnd of BB84 simulation.")
