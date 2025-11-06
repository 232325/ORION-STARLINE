"""
Quantum Approximate Optimization Algorithm (QAOA)
Combination optimization uchun hybrid quantum-classical algorithm
"""

import numpy as np
import networkx as nx
from qiskit import QuantumCircuit, transpile, Aer, execute
from qiskit.algorithms.optimizers import COBYLA, SPSA, ADAM
from qiskit.circuit.library import TwoLocal, XXPlusYYGate
import matplotlib.pyplot as plt

class QAOA:
    """
    Quantum Approximate Optimization Algorithm
    Optimization muammolari uchun hybrid approach
    """
    
    def __init__(self, problem, p_levels=1):
        """
        Args:
            problem (dict): Optimization problem definition
            p_levels (int): QAOA p-levels (circuit depth)
        """
        self.problem = problem
        self.p_levels = p_levels
        self.n_qubits = len(problem.get('variables', []))
        
        # Default optimization parameters
        self.gammas = np.random.random(self.p_levels) * 2 * np.pi
        self.betas = np.random.random(self.p_levels) * np.pi
        
    def create_cost_hamiltonian(self):
        """Cost Hamiltonian yaratish (problem)"""
        from qiskit.opflow import PauliOp, X, Y, Z, I, PauliSumOp
        
        # Simple case: Max-Cut problem
        if self.problem.get('type') == 'maxcut':
            return self._create_maxcut_hamiltonian()
        
        # Default: Simple penalty Hamiltonian
        return self._create_simple_cost_hamiltonian()
    
    def _create_maxcut_hamiltonian(self):
        """Max-Cut problem uchun Hamiltonian"""
        from qiskit.opflow import PauliOp, Z, I
        
        n_qubits = self.n_qubits
        hamiltonian = 0
        
        # Graph edges
        edges = self.problem.get('edges', [])
        
        for edge in edges:
            i, j = edge
            # Hamiltonian: (1 - Z_i Z_j) / 2
            hamiltonian += (I - Z.tensor(Z)) / 2
            
        return hamiltonian
    
    def _create_simple_cost_hamiltonian(self):
        """Simple cost Hamiltonian"""
        from qiskit.opflow import PauliOp, Z
        
        n_qubits = self.n_qubits
        hamiltonian = 0
        
        # Simple objective: minimize sum of qubit values
        for i in range(n_qubits):
            hamiltonian += (I - Z) / 2
            
        return hamiltonian
    
    def create_mixer_hamiltonian(self):
        """Mixer Hamiltonian yaratish (X rotations)"""
        from qiskit.opflow import X
        
        n_qubits = self.n_qubits
        mixer = 0
        
        for i in range(n_qubits):
            mixer += X
            
        return mixer
    
    def qaoa_circuit(self, gammas=None, betas=None):
        """QAOA circuit yaratish"""
        if gammas is None:
            gammas = self.gammas
        if betas is None:
            betas = self.betas
            
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Initial superposition
        for i in range(self.n_qubits):
            qc.h(i)
            
        # QAOA layers
        for p in range(self.p_levels):
            # Cost layer
            gamma = gammas[p]
            # Simplified: Pauli-Z rotations
            for i in range(self.n_qubits):
                qc.rz(2 * gamma, i)
                
            # Mixer layer
            beta = betas[p]
            for i in range(self.n_qubits):
                qc.rx(2 * beta, i)
        
        # Measurement
        qc.measure_all()
        
        return qc
    
    def objective_function(self, parameters):
        """Objective function (maximize/minimize)"""
        gammas = parameters[:self.p_levels]
        betas = parameters[self.p_levels:]
        
        # Run QAOA circuit
        qc = self.qaoa_circuit(gammas, betas)
        qc = transpile(qc, Aer.get_backend('qasm_simulator'))
        
        # Execute
        job = execute(qc, Aer.get_backend('qasm_simulator'), shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        # Calculate expected value
        expected_value = self.calculate_expectation(counts)
        
        return -expected_value  # Minimize for classical optimizer
    
    def calculate_expectation(self, counts):
        """Measurement natijalaridan expected value hisoblash"""
        from qiskit.opflow import PauliOp, Z
        
        total_shots = sum(counts.values())
        expected_value = 0
        
        for bitstring, frequency in counts.items():
            probability = frequency / total_shots
            
            # Calculate expectation for current state
            # Simplified: count number of 1s
            num_ones = sum(1 for bit in bitstring if bit == '1')
            value = num_ones  # Simple objective: more 1s = better
            
            expected_value += probability * value
            
        return expected_value
    
    def optimize_parameters(self, optimizer=None, maxiter=100):
        """QAOA parametrlarni optimizatsiya qilish"""
        if optimizer is None:
            optimizer = COBYLA(maxiter=maxiter)
            
        print(f"QAOA Parameter Optimization (p={self.p_levels})")
        print("=" * 40)
        
        # Initial parameters
        initial_params = np.concatenate([self.gammas, self.betas])
        
        # Optimization
        result = optimizer.optimize(
            num_vars=len(initial_params),
            objective_function=self.objective_function,
            initial_point=initial_params
        )
        
        optimal_params = result[0]
        optimal_value = -result[1]  # Convert back to maximize
        
        # Update parameters
        self.gammas = optimal_params[:self.p_levels]
        self.betas = optimal_params[self.p_levels:]
        
        print(f"Optimal parameters: {optimal_params}")
        print(f"Optimal value: {optimal_value:.4f}")
        
        return optimal_params, optimal_value
    
    def solve_maxcut(self, graph):
        """
        Max-Cut muammosini yechish
        """
        print("QAOA Max-Cut Solution")
        print("=" * 25)
        
        # Set up problem
        self.problem = {
            'type': 'maxcut',
            'edges': list(graph.edges()),
            'nodes': list(graph.nodes())
        }
        
        # Optimize parameters
        optimal_params, optimal_value = self.optimize_parameters()
        
        # Generate optimal circuit
        qc = self.qaoa_circuit()
        
        # Run final solution
        qc = transpile(qc, Aer.get_backend('qasm_simulator'))
        job = execute(qc, Aer.get_backend('qasm_simulator'), shots=1024)
        result = job.result()
        counts = result.get_counts()
        
        # Find best solution
        best_solution = max(counts.items(), key=lambda x: x[1])
        best_bitstring = best_solution[0]
        best_frequency = best_solution[1]
        
        print(f"Best solution: {best_bitstring} (frequency: {best_frequency})")
        print(f"Solution probability: {best_frequency/1024:.2%}")
        
        return best_bitstring, best_frequency, optimal_value
    
    def demonstrate_qaoa(self):
        """QAOA demo ko'rsatish"""
        print("Quantum Approximate Optimization Algorithm Demo")
        print("=" * 45)
        
        # Create simple graph for Max-Cut
        graph = nx.Graph()
        graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (1, 3)])
        
        # Solve with different p-levels
        for p in range(1, 4):
            print(f"\\nQAOA with p={p}:")
            qaoa = QAOA({'type': 'maxcut'}, p_levels=p)
            solution, frequency, value = qaoa.solve_maxcut(graph)
            
            # Analyze solution
            partition = [int(bit) for bit in solution]
            print(f"Partition: {partition}")
            
            # Calculate cut size
            cut_size = 0
            for edge in graph.edges():
                u, v = edge
                if partition[u] != partition[v]:
                    cut_size += 1
                    
            print(f"Cut size: {cut_size}")
            print(f"Expected value: {value:.4f}")


def qaoa_optimization_comparison():
    """QAOA optimizatsiya solishtirish"""
    print("QAOA Optimization Comparison")
    print("=" * 30)
    
    # Different problems
    problems = [
        {'name': 'Max-Cut Small', 'type': 'maxcut', 'n_qubits': 4},
        {'name': 'Max-Cut Medium', 'type': 'maxcut', 'n_qubits': 6},
        {'name': 'Max-Cut Large', 'type': 'maxcut', 'n_qubits': 8}
    ]
    
    # Different p-levels
    p_levels = [1, 2, 3]
    
    results = []
    
    for problem in problems:
        for p in p_levels:
            print(f"\\nTesting {problem['name']} with p={p}")
            
            qaoa = QAOA(problem, p_levels=p)
            qc = qaoa.qaoa_circuit()
            
            # Quick objective evaluation
            test_params = np.random.random(2 * p) * 2 * np.pi
            objective = qaoa.objective_function(test_params)
            
            results.append({
                'problem': problem['name'],
                'p_levels': p,
                'qubits': qaoa.n_qubits,
                'objective': -objective,
                'circuit_depth': 2 * p  # Simplified depth estimation
            })
            
            print(f"Objective: {-objective:.4f}")
    
    return results


def qaoa_advantages():
    """QAOA afzalliklari"""
    print("QAOA Advantages and Applications")
    print("=" * 35)
    
    advantages = [
        "Hybrid algorithm - works on near-term quantum devices",
        "Optimizes specific parameters (gammas, betas)",
        "Suitable for combinatorial optimization",
        "Can handle constraints through mixer design",
        "Demonstrates quantum advantage for some problems"
    ]
    
    applications = [
        "Portfolio optimization",
        "Supply chain management", 
        "Traffic flow optimization",
        "Resource allocation",
        "Scheduling problems"
    ]
    
    print("Advantages:")
    for adv in advantages:
        print(f"  • {adv}")
        
    print("\\nApplications:")
    for app in applications:
        print(f"  • {app}")


def main():
    """QAOA main demo"""
    print("Quantum Approximate Optimization Algorithm (QAOA)")
    print("=" * 50)
    
    # Basic QAOA demonstration
    qaoa = QAOA({'type': 'simple'}, p_levels=2)
    qaoa.demonstrate_qaoa()
    
    # Optimization comparison
    results = qaoa_optimization_comparison()
    
    # QAOA advantages
    qaoa_advantages()
    
    return qaoa, results


if __name__ == "__main__":
    main()