"""
Quantum Fourier Transform (QFT) Implementation
QFT - kvant hisoblashning asosiy algoritmi
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

class QuantumFourierTransform:
    """
    Quantum Fourier Transform algoritmi
    Classical discrete Fourier transform'ning kvant versiyasi
    """
    
    def __init__(self, n_qubits):
        """
        Args:
            n_qubits (int): Qubitlar soni
        """
        self.n_qubits = n_qubits
        self.circuit = None
        
    def qft_circuit(self):
        """QFT circuit yaratish"""
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # QFT algoritmi
        for j in range(self.n_qubits):
            qc.h(j)  # Hadamard gate
            
            # Controlled phase rotations
            for k in range(j + 1, self.n_qubits):
                qc.cp(np.pi / (2 ** (k - j)), j, k)
                
            # Barrier for circuit visualization
            if j < self.n_qubits - 1:
                qc.barrier()
        
        # Swap gates for output reordering
        for i in range(self.n_qubits // 2):
            qc.swap(i, self.n_qubits - i - 1)
            
        return qc
    
    def inverse_qft_circuit(self):
        """Inverse QFT circuit"""
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Reverse swap gates
        for i in range(self.n_qubits // 2):
            qc.swap(i, self.n_qubits - i - 1)
            
        # Inverse QFT
        for j in range(self.n_qubits - 1, -1, -1):
            # Barrier for circuit visualization
            if j > 0:
                qc.barrier()
                
            # Controlled phase rotations (reversed)
            for k in range(j - 1, -1, -1):
                qc.cp(-np.pi / (2 ** (j - k)), j, k)
                
            qc.h(j)  # Hadamard gate
            
        return qc
    
    def create_periodic_input(self, period):
        """
        Davrli kiritish yaratish
        
        Args:
            period (int): Davr qiymati
        """
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Superposition yaratish
        for i in range(self.n_qubits):
            qc.h(i)
            
        # Davrli pattern qo'shish
        for i in range(self.n_qubits):
            if i % period == 0:
                qc.x(i)
                
        return qc
    
    def run_qft_demo(self, backend=None):
        """QFT demo ishga tushirish"""
        print(f"Quantum Fourier Transform Demo - {self.n_qubits} qubits")
        print("=" * 50)
        
        # QFT circuit yaratish
        qc = self.qft_circuit()
        qc.measure_all()
        
        # Transpile for backend
        if backend:
            qc = transpile(qc, backend)
        
        # Circuit visualization
        print("QFT Circuit:")
        print(qc.draw())
        
        return qc
    
    def demonstrate_period_detection(self):
        """Davrni aniqlash demo"""
        print("QFT Period Detection Demo")
        print("=" * 30)
        
        # Davr = 4 bo'lgan input
        period = 4
        qc = self.create_periodic_input(period)
        
        # QFT qo'shish
        qc.append(self.qft_circuit(), range(self.n_qubits))
        qc.measure_all()
        
        print(f"Input period: {period}")
        print("QFT bilan period detection")
        
        return qc


def main():
    """QFT demo ishga tushirish"""
    print("Quantum Fourier Transform (QFT) Demo")
    print("=" * 40)
    
    # 4 qubit QFT
    qft = QuantumFourierTransform(4)
    
    # QFT circuit yaratish
    circuit = qft.run_qft_demo()
    
    # Period detection demo
    period_circuit = qft.demonstrate_period_detection()
    
    return qft, circuit, period_circuit


if __name__ == "__main__":
    main()