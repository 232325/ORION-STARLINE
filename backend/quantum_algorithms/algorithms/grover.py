"""
Grover's Search Algorithm Implementation
Kvant qidiruv algoritmi - quadratic speedup
"""

import numpy as np
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

class GroverSearch:
    """
    Grover's Search Algorithm
    Kvant qidiruv algoritmi O(√N) samaradorlik
    """
    
    def __init__(self, n_qubits, marked_items):
        """
        Args:
            n_qubits (int): Qubitlar soni
            marked_items (list): Qidirilayotgan elementlar ro'yxati
        """
        self.n_qubits = n_qubits
        self.marked_items = marked_items
        self.n_items = 2 ** n_qubits
        self.n_marked = len(marked_items)
        self.n_iterations = int(np.pi / 4 * np.sqrt(self.n_items / self.n_marked))
        
    def create_oracle(self):
        """
        Oracle yaratish - qidirilayotgan elementlarni belgilab beradi
        """
        qc = QuantumCircuit(self.n_qubits)
        
        # Marked items uchun phase flip
        for item in self.marked_items:
            # Binary ko'rinishda
            binary = format(item, f'0{self.n_qubits}b')
            
            # Controlled-Z gates qo'shish
            for i, bit in enumerate(binary):
                if bit == '0':
                    qc.x(i)  # 0 ni 1 ga aylantirish
                    
            # Multi-controlled Z gate
            qc.h(self.n_qubits - 1)
            qc.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
            qc.h(self.n_qubits - 1)
            
            for i, bit in enumerate(binary):
                if bit == '0':
                    qc.x(i)  # Qayta o'sha joyga qaytish
        
        return qc.to_gate(label="Oracle")
    
    def create_diffusion_operator(self):
        """
        Diffusion operator (amplitude amplification)
        """
        qc = QuantumCircuit(self.n_qubits)
        
        # Hadamard gates
        for i in range(self.n_qubits):
            qc.h(i)
            
        # X gates
        for i in range(self.n_qubits):
            qc.x(i)
            
        # Multi-controlled Z gate
        qc.h(self.n_qubits - 1)
        qc.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
        qc.h(self.n_qubits - 1)
        
        # X gates
        for i in range(self.n_qubits):
            qc.x(i)
            
        # Hadamard gates
        for i in range(self.n_qubits):
            qc.h(i)
            
        return qc.to_gate(label="Diffusion")
    
    def grover_circuit(self):
        """Grover algoritmi circuit yaratish"""
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Superposition yaratish
        for i in range(self.n_qubits):
            qc.h(i)
            
        # Oracle va diffusion operatorlarni takrorlash
        oracle = self.create_oracle()
        diffusion = self.create_diffusion_operator()
        
        for _ in range(self.n_iterations):
            qc.append(oracle, range(self.n_qubits))
            qc.append(diffusion, range(self.n_qubits))
            
        # O'lchash
        qc.measure_all()
        
        return qc
    
    def run_demo(self):
        """Grover demo ishga tushirish"""
        print(f"Grover's Search Algorithm Demo")
        print(f"Qubits: {self.n_qubits}, Database size: {self.n_items}")
        print(f"Marked items: {self.marked_items}")
        print(f"Optimal iterations: {self.n_iterations}")
        print("=" * 50)
        
        # Circuit yaratish
        qc = self.grover_circuit()
        
        # Circuit visualization
        print("Grover Circuit:")
        print(qc.draw())
        
        return qc
    
    def simulate_results(self, simulator=Aer.get_backend('qasm_simulator')):
        """Natijalarni simulyatsiya qilish"""
        print("Grover's Algorithm Results")
        print("=" * 30)
        
        qc = self.grover_circuit()
        
        # Execute
        job = execute(qc, simulator, shots=1024)
        result = job.result()
        counts = result.get_counts()
        
        # Visualization
        print("Measurement Results:")
        plot_histogram(counts)
        plt.title("Grover's Algorithm Results")
        plt.show()
        
        # Success rate analysis
        success_counts = sum(counts.get(format(item, f'0{self.n_qubits}b'), 0) 
                           for item in self.marked_items)
        total_shots = sum(counts.values())
        success_rate = success_counts / total_shots
        
        print(f"Success rate: {success_rate:.2%}")
        
        return counts
    
    def analyze_complexity(self):
        """Murakkablik tahlili"""
        print("Grover's Algorithm Complexity Analysis")
        print("=" * 40)
        
        print(f"Database size (N): {self.n_items}")
        print(f"Marked items (M): {self.n_marked}")
        print(f"Classical search complexity: O(N) = {self.n_items}")
        print(f"Quantum Grover complexity: O(√N) = {int(np.sqrt(self.n_items))}")
        print(f"Speedup factor: {int(np.sqrt(self.n_items))}x faster")
        
        # Iterations
        print(f"Optimal iterations: {int(np.pi / 4 * np.sqrt(self.n_items / self.n_marked))}")
        
    def demonstrate_amplitude_amplification(self):
        """Amplitude amplification ko'rsatish"""
        print("Amplitude Amplification Demonstration")
        print("=" * 35)
        
        # Random states uchun
        n_qubits = 2
        n_items = 2 ** n_qubits
        
        for marked_item in range(n_items):
            print(f"\\nSearching for item: {marked_item}")
            
            grover = GroverSearch(n_qubits, [marked_item])
            grover.analyze_complexity()
            
            # Circuit va results
            circuit = grover.run_demo()
            counts = grover.simulate_results()


def create_grover_variations():
    """Grover algoritmi variantlarini yaratish"""
    
    print("Grover Algorithm Variations")
    print("=" * 30)
    
    # 1. Multiple marked items
    print("\\n1. Multiple Marked Items:")
    grover_multi = GroverSearch(3, [2, 5, 7])
    grover_multi.run_demo()
    
    # 2. Database search
    print("\\n2. Large Database Search:")
    grover_large = GroverSearch(6, [15, 32, 48])
    grover_large.analyze_complexity()
    grover_large.run_demo()
    
    # 3. Single marked item
    print("\\n3. Single Marked Item:")
    grover_single = GroverSearch(4, [10])
    grover_single.analyze_complexity()
    grover_single.run_demo()


def main():
    """Grover's Algorithm main demo"""
    print("Grover's Search Algorithm")
    print("=" * 35)
    
    # Basic Grover demo
    grover = GroverSearch(3, [5])
    grover.run_demo()
    grover.analyze_complexity()
    grover.simulate_results()
    
    # Variations
    create_grover_variations()
    
    return grover


if __name__ == "__main__":
    main()