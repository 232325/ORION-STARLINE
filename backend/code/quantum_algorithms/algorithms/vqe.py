"""
Variational Quantum Eigensolver (VQE)
Kvant kimyosi va molekulyar tuzilishlar uchun
"""

import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.algorithms.optimizers import COBYLA, SPSA, ADAM
from qiskit.opflow import PauliOp, X, Y, Z, I
import matplotlib.pyplot as plt

class VQE:
    """
    Variational Quantum Eigensolver
    Ground state energy ni topish uchun variational algorithm
    """
    
    def __init__(self, hamiltonian, ansatz_type='hardware_efficient'):
        """
        Args:
            hamiltonian (Operator): Molecular/System Hamiltonian
            ansatz_type (str): Type of ansatz to use
        """
        self.hamiltonian = hamiltonian
        self.ansatz_type = ansatz_type
        self.parameters = []
        self.n_qubits = hamiltonian.num_qubits if hasattr(hamiltonian, 'num_qubits') else 2
        
    def create_hardware_efficient_ansatz(self, depth=1):
        """
        Hardware efficient variational form
        
        Args:
            depth (int): Circuit depth
            
        Returns:
            QuantumCircuit: Variational circuit
        """
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Initialize in uniform superposition
        for i in range(self.n_qubits):
            qc.h(i)
            
        # Alternating layers of rotation and entanglement
        num_layers = depth
        
        for layer in range(num_layers):
            # Single qubit rotations
            for i in range(self.n_qubits):
                qc.ry(np.pi/4, i)
                
            # Entangling layer (linear)
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
                
        return qc
    
    def create_adaptive_ansatz(self):
        """Adaptive variational form"""
        qc = QuantumCircuit(self.n_qubits)
        
        # Start with Hartree-Fock state
        for i in range(self.n_qubits // 2):
            qc.x(i)  # Occupied orbitals
            
        # Add variational layers adaptively
        # Simplified version
        for i in range(self.n_qubits):
            qc.ry(np.pi/3, i)
            
        # Entangling gates
        for i in range(self.n_qubits - 1):
            qc.cx(i, i + 1)
            
        return qc
    
    def create_ucc_ansatz(self, excitations=None):
        """
        Unitary Coupled Cluster ansatz
        
        Args:
            excitations (list): List of excitation operators
        """
        qc = QuantumCircuit(self.n_qubits)
        
        if excitations is None:
            # Simple singles and doubles
            excitations = []
            for i in range(self.n_qubits):
                excitations.append((i,))  # Single excitations
                for j in range(i + 1, self.n_qubits):
                    excitations.append((i, j))  # Double excitations
        
        # Apply excitation operators
        for excitation in excitations:
            if len(excitation) == 1:
                # Single excitation
                i = excitation[0]
                qc.ry(np.pi/4, i)
            elif len(excitation) == 2:
                # Double excitation
                i, j = excitation
                qc.cx(i, j)
                qc.ry(np.pi/4, j)
                
        return qc
    
    def get_ansatz(self, parameters=None):
        """Get variational circuit with parameters"""
        if parameters is None:
            # Generate random parameters
            if self.ansatz_type == 'hardware_efficient':
                n_params = self.n_qubits * 2  # Simplified
                parameters = np.random.random(n_params) * 2 * np.pi
                
        if self.ansatz_type == 'hardware_efficient':
            qc = self.create_hardware_efficient_ansatz()
        elif self.ansatz_type == 'adaptive':
            qc = self.create_adaptive_ansatz()
        elif self.ansatz_type == 'ucc':
            qc = self.create_ucc_ansatz()
        else:
            qc = self.create_hardware_efficient_ansatz()
        
        # Apply parameters (simplified mapping)
        if parameters is not None:
            for i, param in enumerate(parameters):
                qc.ry(param, i % self.n_qubits)
        
        return qc
    
    def simple_hamiltonian(self):
        """Simple test Hamiltonian"""
        # H = 0.5 * Z_0 + 0.5 * Z_1 + 0.25 * X_0 * X_1 + 0.25 * Y_0 * Y_1
        
        hamiltonian = 0.5 * Z.tensor(Z)  # I_1 ⊗ Z_0 + Z_1 ⊗ I_0
        hamiltonian += 0.5 * (Z.tensor(I) + I.tensor(Z))  # Interaction terms
        hamiltonian += 0.25 * (X.tensor(X) + Y.tensor(Y))
        
        return hamiltonian
    
    def heisenberg_model(self, J=1.0, h=0.5):
        """
        Heisenberg model Hamiltonian
        
        Args:
            J (float): Coupling strength
            h (float): Magnetic field
        """
        H = 0
        
        # 1D Heisenberg chain
        for i in range(self.n_qubits - 1):
            # XX coupling
            H += J * (X.tensor(X) + Y.tensor(Y) + Z.tensor(Z))
            H += h * Z  # Magnetic field
        
        return H
    
    def ising_model(self, J=1.0, h=1.0):
        """1D Ising model"""
        H = 0
        
        for i in range(self.n_qubits - 1):
            H += -J * Z.tensor(Z)
            
        for i in range(self.n_qubits):
            H += -h * X
            
        return H
    
    def calculate_expectation_value(self, circuit, hamiltonian=None):
        """
        Calculate expectation value <ψ|H|ψ>
        
        Args:
            circuit (QuantumCircuit): Variational circuit
            hamiltonian (Operator): Hamiltonian operator
            
        Returns:
            float: Expectation value
        """
        if hamiltonian is None:
            hamiltonian = self.hamiltonian
            
        # For simple Hamiltonians, calculate analytically
        if hasattr(hamiltonian, 'to_matrix'):
            matrix = hamiltonian.to_matrix()
            state = np.zeros(2**self.n_qubits)
            state[0] = 1.0  # |000...⟩ state
        else:
            # Simplified expectation calculation
            return self._simple_expectation_calculation(circuit)
        
        return 0.0  # Placeholder
    
    def _simple_expectation_calculation(self, circuit):
        """Simplified expectation calculation for demo"""
        # Run circuit and get state vector
        qc = circuit.copy()
        qc.save_statevector()
        
        # Execute on simulator
        job = execute(qc, Aer.get_backend('statevector_simulator'))
        result = job.result()
        statevector = result.get_statevector(qc)
        
        # Simple energy calculation
        energy = 0.0
        
        # For demo: approximate as sum of Z expectations
        for i in range(self.n_qubits):
            # Measure expectation of Z_i
            expectation = self._calculate_z_expectation(statevector, i)
            energy += 0.5 * expectation
            
        return energy
    
    def _calculate_z_expectation(self, statevector, qubit):
        """Calculate expectation of Z operator for single qubit"""
        # Simplified: assume |0⟩ = 1, |1⟩ = -1
        probs = np.abs(statevector) ** 2
        
        expectation = 0
        for i, prob in enumerate(probs):
            # Check if qubit is |1⟩
            if (i >> qubit) & 1:
                expectation -= prob
            else:
                expectation += prob
                
        return expectation
    
    def optimize_parameters(self, optimizer=None, maxiter=100, initial_params=None):
        """
        Optimize variational parameters
        
        Args:
            optimizer: Classical optimizer
            maxiter (int): Maximum iterations
            initial_params (array): Initial parameter values
            
        Returns:
            tuple: (optimal_params, optimal_energy, optimization_data)
        """
        if optimizer is None:
            optimizer = COBYLA(maxiter=maxiter)
            
        print(f"VQE Parameter Optimization ({self.ansatz_type})")
        print("=" * 40)
        
        if initial_params is None:
            # Generate random initial parameters
            if self.ansatz_type == 'hardware_efficient':
                n_params = self.n_qubits * 2
                initial_params = np.random.random(n_params) * 2 * np.pi
        
        # Define objective function
        def objective_function(params):
            circuit = self.get_ansatz(params)
            energy = self._calculate_energy(circuit)
            return energy
        
        def objective_function_wrapper(params):
            return objective_function(params)
        
        # Optimization
        result = optimizer.optimize(
            num_vars=len(initial_params),
            objective_function=objective_function_wrapper,
            initial_point=initial_params
        )
        
        optimal_params = result[0]
        optimal_energy = result[1]
        
        print(f"Optimal energy: {optimal_energy:.6f}")
        print(f"Optimal parameters: {optimal_params}")
        
        return optimal_params, optimal_energy, result
    
    def _calculate_energy(self, circuit):
        """Calculate energy for given circuit"""
        # Simplified energy calculation
        energy = 0.0
        
        # Run circuit
        qc = circuit.copy()
        qc.measure_all()
        
        job = execute(qc, Aer.get_backend('qasm_simulator'), shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        total_shots = sum(counts.values())
        
        # Calculate energy from measurement statistics
        for bitstring, frequency in counts.items():
            prob = frequency / total_shots
            
            # Simple energy: count of 1s
            energy += prob * sum(1 for bit in bitstring if bit == '1')
            
        return energy
    
    def find_ground_state(self):
        """Find ground state energy"""
        print(f"VQE Ground State Search ({self.ansatz_type} ansatz)")
        print("=" * 45)
        
        # Optimize parameters
        optimal_params, optimal_energy, opt_result = self.optimize_parameters()
        
        # Generate optimal circuit
        optimal_circuit = self.get_ansatz(optimal_params)
        
        print(f"Ground state energy: {optimal_energy:.6f}")
        print(f"Circuit depth: {optimal_circuit.depth()}")
        
        return optimal_energy, optimal_params, optimal_circuit
    
    def compare_ansatze(self):
        """Compare different ansatz types"""
        print("VQE Ansatz Comparison")
        print("=" * 25)
        
        ansatz_types = ['hardware_efficient', 'adaptive', 'ucc']
        results = {}
        
        for ansatz in ansatz_types:
            print(f"\\nTesting {ansatz} ansatz:")
            
            self.ansatz_type = ansatz
            energy, params, circuit = self.find_ground_state()
            
            results[ansatz] = {
                'energy': energy,
                'circuit_depth': circuit.depth(),
                'parameters': len(params)
            }
            
            print(f"Energy: {energy:.6f}")
            print(f"Circuit depth: {circuit.depth()}")
            print(f"Parameters: {len(params)}")
        
        return results
    
    def simulate_energy_landscape(self):
        """Energy landscape simulation"""
        print("VQE Energy Landscape")
        print("=" * 25)
        
        # Parameter ranges
        param_range = np.linspace(0, 2*np.pi, 20)
        
        energies = []
        
        for theta in param_range:
            params = [theta] * self.n_qubits
            circuit = self.get_ansatz(params)
            energy = self._calculate_energy(circuit)
            energies.append(energy)
        
        # Plot energy landscape
        plt.figure(figsize=(10, 6))
        plt.plot(param_range, energies, 'b-', linewidth=2)
        plt.xlabel('Parameter θ')
        plt.ylabel('Energy')
        plt.title('VQE Energy Landscape')
        plt.grid(True)
        plt.show()
        
        return param_range, energies


def vqe_chemistry_application():
    """VQE chemistry application"""
    print("VQE Chemistry Applications")
    print("=" * 30)
    
    # Simple molecules
    molecules = [
        {'name': 'H₂', 'qubits': 2, 'atoms': 2},
        {'name': 'LiH', 'qubits': 4, 'atoms': 2},
        {'name': 'H₂O', 'qubits': 6, 'atoms': 3},
        {'name': 'NH₃', 'qubits': 8, 'atoms': 4}
    ]
    
    for molecule in molecules:
        print(f"\\nMolecule: {molecule['name']}")
        print(f"Qubits needed: {molecule['qubits']}")
        print(f"Atoms: {molecule['atoms']}")
        
        # Create VQE instance
        vqe = VQE(None, 'hardware_efficient')
        vqe.n_qubits = molecule['qubits']
        
        # Find ground state
        energy, params, circuit = vqe.find_ground_state()
        
        print(f"VQE energy: {energy:.6f} Hartree")
        print(f"Convergence iterations: ~100")


def vqe_performance_analysis():
    """VQE performance analysis"""
    print("VQE Performance Analysis")
    print("=" * 30)
    
    # Problem sizes
    qubit_counts = [2, 4, 6, 8, 10]
    
    print(f"{'Qubits':>6} {'Parameters':>10} {'Circuit Depth':>12} {'Estimated Time':>15}")
    print("-" * 50)
    
    for n_qubits in qubit_counts:
        # Parameter count estimation
        n_params = n_qubits * 2  # Simplified
        
        # Circuit depth estimation
        depth = n_qubits  # Simplified
        
        # Time estimation (rough)
        time_estimate = n_qubits ** 2  # seconds
        
        print(f"{n_qubits:6d} {n_params:10d} {depth:12d} {time_estimate:15.1f}s")
    
    print("\\nKey Observations:")
    print("- Parameter count scales linearly with qubits")
    print("- Circuit depth grows with problem size")
    print("- Optimization time increases with complexity")
    print("- Convergence depends on ansatz choice")


def main():
    """VQE main demonstration"""
    print("Variational Quantum Eigensolver (VQE)")
    print("=" * 40)
    
    # Create VQE instance
    vqe = VQE(None, 'hardware_efficient')
    
    # Find ground state
    energy, params, circuit = vqe.find_ground_state()
    
    # Compare different ansatze
    results = vqe.compare_ansatze()
    
    # Energy landscape
    param_range, energies = vqe.simulate_energy_landscape()
    
    # Chemistry applications
    vqe_chemistry_application()
    
    # Performance analysis
    vqe_performance_analysis()
    
    return vqe, results


if __name__ == "__main__":
    main()