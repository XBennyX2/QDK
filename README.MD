# **Quantum Key Distribution Protocol**

## **BB84 Protocol (Bennett & Brassard)**

BB84 lets two distant parties like **A** and **B** establish a shared secret key over an insecure quantum channel plus an authenticated classical channel. Its security is guaranteed by basic quantum features: non-orthogonal states cannot be perfectly distinguished and measurements generally disturb quantum states. So any eavesdropper trying to get information introduces detectable errors.

**Two bases are used to encode classical bits:**  
- **Rectilinear basis (+)**
- **Diagonal basis (×)**

### **Steps in BB84**

1. **Key Preparation:**  
   **A** randomly generates a sequence of classical bits (0s and 1s). For each bit, **A** randomly chooses a basis (Rectilinear or Diagonal). **A** sends a stream of photons, each prepared in one of four states: |0⟩, |1⟩, |+⟩, |−⟩.

2. **Measurement:**  
   **B** measures the qubits, randomly choosing a basis for each photon. If **B** chooses the same basis as **A**, **B** gets the correct bit with certainty; otherwise, the result is random (50% chance).

3. **Basis Announcement:**  
   After sending all qubits, **A** and **B** publicly announce which bases they used (not the bit values). They discard all bits where their bases were different; the remaining bits form the raw key.

4. **Eavesdropper Detection:**  
   **A** and **B** publicly compare a random subset of their raw key bits. If too many errors are found (above a threshold), they abort the protocol. If the error rate is low, they assume no significant eavesdropping occurred.

5. **Error Correction & Privacy Amplification:**  
   They perform error correction to fix small mismatches. Privacy amplification shortens the key but ensures the eavesdropper has negligible knowledge. The final result is a shared secret key known only to **A** and **B**.

---

## **E91 Protocol (Ekert)**

Unlike BB84, which relies on sending individual qubits prepared in random bases, **E91 uses entangled quantum pairs**. Security comes from entanglement correlations that violate Bell's inequalities—something no classical system or eavesdropper can mimic.

- The source produces entangled qubit pairs, usually in the Bell state.
- If **A** measures 0, **B** must measure 1; if **A** measures 1, **B** must measure 0 (anti-correlated in the same basis).

**Measurement Settings:**  
- **A** chooses randomly from a₁, a₂, a₃.  
- **B** chooses randomly from b₁, b₂, b₃.

While **A** measures along aᵢ and **B** measures along bⱼ, their results are correlated according to:  
**E(aᵢ, bⱼ) (expectation value of correlation) = −cos(θₐᵢ − θ_bⱼ)**  
where θ is the angle of measurement bases.

**Eavesdropper Detection:**  
- **A** and **B** check Bell's inequality.
- If their results violate Bell's inequality, they confirm quantum correlations and that Eve cannot have cloned the qubits.

**Key Extraction:**  
- From cases where their bases are the same, measurement outcomes are perfectly correlated or anti-correlated.
- Classical techniques remove errors and ensure Eve has no information.

---

**Summary:**  
- **E91 uses entanglement + Bell's theorem to guarantee security.**  
- **BB84 uses state preparation + basis mismatch.**
