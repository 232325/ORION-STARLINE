"""
Shor's Algorithm Implementation
Kvant factoring algoritmi - polynomial time factorization
"""

import numpy as np
import math
from fractions import Fraction
from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

class ShorAlgorithm:
    """
    Shor's Algorithm for Integer Factorization
    Classical factoring'ning kvant versiyasi - exponential speedup
    """
    
    def __init__(self, number_to_factor):
        """
        Args:
            number_to_factor (int): Faktorlash kerak bo'lgan son
        """
        self.N = number_to_factor
        self.n_qubits = int(np.ceil(np.log2(self.N)))
        self.ancilla_qubits = self.n_qubits
        
    def extended_gcd(self, a, b):
        """Extended Euclidean Algorithm"""
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = self.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    def find_period(self, a):
        """
        Period find qilish (r) - Shor algoritmining asosiy qismi
        
        Args:
            a (int): Base for modular exponentiation
            
        Returns:
            int: Period (r)
        """
        print(f"Finding period for a = {a}")
        
        # Classical period finding if gcd(a, N) != 1
        gcd_val, x, y = self.extended_gcd(a, self.N)
        if gcd_val != 1:
            return gcd_val
        
        # Quantum period finding would go here
        # For demo, using classical approach
        r = 1
        current = a % self.N
        while current != 1:
            current = (current * a) % self.N
            r += 1
            if r > self.N:
                break
                
        return r
    
    def quantum_period_finder(self, a):
        """
        Quantum period finding circuit
        """
        total_qubits = self.n_qubits + self.ancilla_qubits
        
        # Quantum circuit
        qc = QuantumCircuit(total_qubits, total_qubits)
        
        # First register (ancilla qubits)
        for i in range(self.n_qubits):
            qc.h(i)
        
        # Second register (output qubits)
        for i in range(self.n_qubits, total_qubits):
            qc.x(i)  # |1> state
            
        # Modular exponentiation controlled gates
        # This is a simplified version - real implementation would be complex
        
        # QFT on first register
        from algorithms.qft import QuantumFourierTransform
        qft = QuantumFourierTransform(self.n_qubits)
        qc.append(qft.inverse_qft_circuit(), range(self.n_qubits))
        
        # Measurement
        qc.measure_all()
        
        return qc
    
    def classical_period_finder(self, a):
        """Classical period finding for demonstration"""
        print(f"Classical period finding for a={a}, N={self.N}")
        
        # Simple brute force period finding
        r = 1
        current = a % self.N
        
        while current != 1:
            current = (current * a) % self.N
            r += 1
            if r > 100:  # Safety limit
                print("Period finding failed, trying next a")
                return None
                
        print(f"Period found: r = {r}")
        return r
    
    def factor_number(self, a=None):
        """Main factoring function"""
        print(f"Shor's Algorithm for factoring {self.N}")
        print("=" * 40)
        
        if a is None:
            # Try different values of a
            for test_a in range(2, min(self.N, 10)):
                gcd_val, _, _ = self.extended_gcd(test_a, self.N)
                if gcd_val == 1:
                    a = test_a
                    break
            else:
                print("No suitable a found")
                return None
        
        # Find period
        r = self.classical_period_finder(a)
        
        if r is None or r % 2 != 0:
            print("Period is odd, trying different a")
            return self.factor_number(a + 1)
        
        # Calculate factors
        print(f"Period r = {r}")
        
        # Compute a^(r/2) mod N
        a_power_r2 = pow(a, r // 2, self.N)
        
        print(f"a^(r/2) mod N = {a_power_r2}")
        
        # Factor 1
        gcd1, _, _ = self.extended_gcd(a_power_r2 + 1, self.N)
        
        # Factor 2
        gcd2, _, _ = self.extended_gcd(a_power_r2 - 1, self.N)
        
        factor1 = max(gcd1, gcd2) if gcd1 != 1 and gcd2 != 1 else min(gcd1, gcd2)
        factor2 = self.N // factor1 if factor1 != 1 else None
        
        print(f"Factors: {factor1} × {factor2} = {self.N}")
        
        return factor1, factor2
    
    def demonstrate_factorization(self):
        """Faktorlash demo ko'rsatish"""
        print("Shor's Algorithm Factorization Demo")
        print("=" * 35)
        
        # Test numbers
        test_numbers = [15, 21, 35, 77, 143]
        
        for num in test_numbers:
            print(f"\\nFactoring {num}:")
            shor = ShorAlgorithm(num)
            factors = shor.factor_number()
            
            if factors and len(factors) == 2:
                f1, f2 = factors
                if f1 * f2 == num:
                    print(f"✓ Success: {f1} × {f2} = {num}")
                else:
                    print(f"✗ Failed: {f1} × {f2} ≠ {num}")
            else:
                print(f"✗ Failed to factor {num}")
    
    def analyze_complexity(self):
        """Murakkablik tahlili"""
        print("Shor's Algorithm Complexity Analysis")
        print("=" * 40)
        
        N = self.N
        print(f"Number to factor (N): {N}")
        print(f"Bit length: {int(np.log2(N)) + 1}")
        
        # Classical factoring complexity
        print("\\nClassical Factoring:")
        print("- Simple trial division: O(N)")
        print("- General number field sieve: O(exp((log N)^(1/3)))")
        
        # Quantum factoring complexity
        print("\\nQuantum Factoring (Shor):")
        print("- Period finding: O((log N)^2)")
        print("- Post-processing: O(log N)")
        print("- Total: O((log N)^3)")
        
        # Qubit requirements
        print("\\nQubit Requirements:")
        print(f"- Total qubits needed: ~2 × {int(np.log2(N)) + 1} = {2 * (int(np.log2(N)) + 1)}")
        
        # Comparison table
        print("\\nPerformance Comparison:")
        bit_lengths = [8, 16, 32, 64, 128]
        for bits in bit_lengths:
            classical_ops = 2**bits  # Rough estimate
            quantum_ops = bits**3    # O((log N)^3)
            speedup = classical_ops / quantum_ops
            print(f"{bits:3d} bits: Classical ~{classical_ops:12.0e} ops, "
                  f"Quantum ~{quantum_ops:6.0e} ops, Speedup: {speedup:.2e}x")


def quantum_factorization_demo():
    """Quantum factorization demo"""
    print("Quantum Factorization Demonstration")
    print("=" * 35)
    
    # Shor's algorithm for different numbers
    numbers = [15, 21, 35, 143]
    
    for num in numbers:
        print(f"\\nFactoring {num} using Shor's Algorithm:")
        shor = ShorAlgorithm(num)
        shor.analyze_complexity()
        
        factors = shor.factor_number()
        
        if factors:
            f1, f2 = factors
            if f1 * f2 == num:
                print(f"✓ Factorization successful: {f1} × {f2} = {num}")
            else:
                print(f"✗ Factorization failed")
    
    return numbers


def classical_vs_quantum_comparison():
    """Classical va quantum factoring solishtirish"""
    print("Classical vs Quantum Factorization Comparison")
    print("=" * 45)
    
    numbers = [15, 35, 77, 143, 1009]
    
    print(f"{'Number':>8} {'Bits':>4} {'Classical Ops':>12} {'Quantum Ops':>12} {'Speedup':>8}")
    print("-" * 55)
    
    for num in numbers:
        bits = int(np.log2(num)) + 1
        # Classical operations (rough estimate)
        classical_ops = 10 ** (bits // 2)  # Exponential
        # Quantum operations (polynomial)
        quantum_ops = bits ** 3  # Polynomial
        speedup = classical_ops / quantum_ops if quantum_ops > 0 else 0
        
        print(f"{num:8d} {bits:4d} {classical_ops:12.0e} {quantum_ops:12.0e} {speedup:8.2e}")
    
    print("\\nKey Observations:")
    print("- Classical factoring is exponential in bit length")
    print("- Quantum factoring is polynomial in bit length")
    print("- Speedup grows exponentially with problem size")
    print("- Large numbers require quantum advantage")


def main():
    """Shor's Algorithm main demo"""
    print("Shor's Algorithm for Integer Factorization")
    print("=" * 45)
    
    # Shor's algorithm demonstration
    shor = ShorAlgorithm(15)
    shor.analyze_complexity()
    shor.demonstrate_factorization()
    
    # Classical vs Quantum comparison
    classical_vs_quantum_comparison()
    
    # Quantum factorization demo
    quantum_factorization_demo()
    
    return shor


if __name__ == "__main__":
    main()