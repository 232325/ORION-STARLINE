"""
Quantum Support Vector Machines (QSVM)
Klassik SVM'ning kvant versiyasi
"""

import numpy as np
from sklearn.svm import SVC
from sklearn.datasets import make_classification, make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from qiskit import QuantumCircuit, Aer, execute
from qiskit_machine_learning.kernels import QuantumKernel
from qiskit_machine_learning.algorithms.classifiers import QSVC
import matplotlib.pyplot as plt

class QuantumSVM:
    """
    Quantum Support Vector Machine
    Kernel methods for quantum machine learning
    """
    
    def __init__(self, feature_dim, backend=None, shots=1024):
        """
        Args:
            feature_dim (int): Feature dimension
            backend (Backend): Quantum backend
            shots (int): Number of shots for quantum computation
        """
        self.feature_dim = feature_dim
        self.n_qubits = feature_dim
        self.backend = backend or Aer.get_backend('qasm_simulator')
        self.shots = shots
        self.qkernel = None
        self.qsvc = None
        
    def amplitude_encoding_circuit(self, features):
        """
        Create quantum circuit for amplitude encoding
        
        Args:
            features (array): Classical features to encode
            
        Returns:
            QuantumCircuit: Circuit with encoded features
        """
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Normalize features for amplitude encoding
        norm = np.linalg.norm(features)
        if norm > 0:
            normalized_features = features / norm
        else:
            normalized_features = features
            
        # Amplitude encoding (simplified)
        for i in range(min(self.n_qubits, len(normalized_features))):
            angle = np.arccos(np.sqrt(abs(normalized_features[i])))
            qc.ry(2 * angle, i)
            
        # Add entanglement
        for i in range(self.n_qubits - 1):
            qc.cx(i, i + 1)
            
        return qc
    
    def angle_encoding_circuit(self, features):
        """
        Create quantum circuit for angle encoding
        
        Args:
            features (array): Classical features to encode
            
        Returns:
            QuantumCircuit: Circuit with encoded features
        """
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        
        # Initialize in superposition
        for i in range(self.n_qubits):
            qc.h(i)
            
        # Angle encoding
        for i in range(min(self.n_qubits, len(features))):
            # Scale features to [0, 2π]
            scaled_feature = (features[i] + 1) * np.pi
            qc.rz(scaled_feature, i)
            
        # Add entanglement for feature mixing
        for i in range(self.n_qubits - 1):
            qc.cx(i, i + 1)
            
        return qc
    
    def create_quantum_kernel(self, encoding='angle'):
        """
        Create quantum kernel
        
        Args:
            encoding (str): Type of encoding ('angle' or 'amplitude')
            
        Returns:
            QuantumKernel: Quantum kernel object
        """
        def feature_map_circuit(x1, x2):
            # For quantum kernel, we need to create a circuit
            # that represents both input vectors
            qc = QuantumCircuit(self.n_qubits, self.n_qubits)
            
            # Encode first vector
            if encoding == 'angle':
                for i in range(min(self.n_qubits, len(x1))):
                    scaled_feature = (x1[i] + 1) * np.pi
                    qc.rz(scaled_feature, i)
            elif encoding == 'amplitude':
                norm = np.linalg.norm(x1)
                if norm > 0:
                    normalized_x1 = x1 / norm
                else:
                    normalized_x1 = x1
                for i in range(min(self.n_qubits, len(normalized_x1))):
                    angle = np.arccos(np.sqrt(abs(normalized_x1[i])))
                    qc.ry(2 * angle, i)
            
            # Add entanglement
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
                
            # Add second vector interaction
            for i in range(self.n_qubits):
                qc.rz(np.pi / 2, i)  # Phase gates
                
            return qc
        
        # Create quantum kernel
        self.qkernel = QuantumKernel(
            feature_map=feature_map_circuit,
            quantum_instance=self.backend
        )
        
        return self.qkernel
    
    def train_qsvc(self, X_train, y_train, kernel='quantum'):
        """
        Train Quantum SVM
        
        Args:
            X_train (array): Training features
            y_train (array): Training labels
            kernel (str): Kernel type
        """
        print("Training Quantum SVM")
        print("=" * 25)
        
        if kernel == 'quantum':
            # Create quantum kernel
            self.create_quantum_kernel()
            
            # Create quantum SVM
            self.qsvc = QSVC(
                quantum_kernel=self.qkernel,
                quantum_instance=self.backend
            )
            
        else:
            # Classical SVM with quantum features
            self.qsvc = SVC(kernel='rbf', C=1.0)
        
        # Train the model
        self.qsvc.fit(X_train, y_train)
        
        print(f"Model trained on {len(X_train)} samples")
        print(f"Feature dimension: {X_train.shape[1]}")
        
        return self.qsvc
    
    def predict(self, X_test):
        """
        Make predictions
        
        Args:
            X_test (array): Test features
            
        Returns:
            array: Predictions
        """
        if self.qsvc is None:
            raise ValueError("Model not trained yet")
            
        predictions = self.qsvc.predict(X_test)
        return predictions
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test (array): Test features
            y_test (array): Test labels
            
        Returns:
            dict: Evaluation results
        """
        predictions = self.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        results = {
            'accuracy': accuracy,
            'predictions': predictions,
            'classification_report': classification_report(y_test, predictions)
        }
        
        return results
    
    def quantum_feature_extraction(self, X):
        """
        Extract quantum features from classical data
        
        Args:
            X (array): Input data
            
        Returns:
            array: Quantum-enhanced features
        """
        quantum_features = []
        
        for sample in X:
            # Create quantum circuit
            qc = self.angle_encoding_circuit(sample)
            
            # Simulate measurements
            job = execute(qc, self.backend, shots=self.shots)
            result = job.result()
            counts = result.get_counts()
            
            # Extract features from measurement statistics
            feature_vector = []
            for i in range(self.n_qubits):
                # Count |1⟩ measurements for qubit i
                ones_count = sum(count for state, count in counts.items() 
                               if state[self.n_qubits - 1 - i] == '1')
                feature = ones_count / self.shots
                feature_vector.append(feature)
                
            quantum_features.append(feature_vector)
            
        return np.array(quantum_features)
    
    def demonstrate_quantum_advantage(self, X_train, X_test):
        """Demonstrate quantum advantage in feature mapping"""
        print("Quantum Advantage Demonstration")
        print("=" * 35)
        
        # Classical features
        classical_features = X_train[:10]  # Sample
        
        # Quantum features
        quantum_features = self.quantum_feature_extraction(X_train[:10])
        
        print("Feature Comparison:")
        print(f"Classical feature space: {classical_features.shape[1]}D")
        print(f"Quantum feature space: {quantum_features.shape[1]}D")
        
        # Compute feature separability
        classical_distances = np.linalg.norm(classical_features[:, None, :] - classical_features[None, :, :], axis=2)
        quantum_distances = np.linalg.norm(quantum_features[:, None, :] - quantum_features[None, :, :], axis=2)
        
        print(f"Classical separation range: {np.min(classical_distances):.3f} - {np.max(classical_distances):.3f}")
        print(f"Quantum separation range: {np.min(quantum_distances):.3f} - {np.max(quantum_distances):.3f}")
        
        return quantum_features


class QuantumKernelMatrix:
    """
    Quantum Kernel Matrix computation
    """
    
    def __init__(self, quantum_kernel):
        """
        Args:
            quantum_kernel (QuantumKernel): Quantum kernel object
        """
        self.quantum_kernel = quantum_kernel
        
    def compute_kernel_matrix(self, X1, X2):
        """
        Compute quantum kernel matrix
        
        Args:
            X1 (array): First set of samples
            X2 (array): Second set of samples
            
        Returns:
            array: Kernel matrix
        """
        n1, n2 = len(X1), len(X2)
        kernel_matrix = np.zeros((n1, n2))
        
        for i in range(n1):
            for j in range(n2):
                # Compute kernel value
                kernel_value = self.quantum_kernel.evaluate(X1[i], X2[j])
                kernel_matrix[i, j] = kernel_value
                
        return kernel_matrix
    
    def visualize_kernel_matrix(self, X, title="Quantum Kernel Matrix"):
        """Visualize kernel matrix"""
        kernel_matrix = self.compute_kernel_matrix(X, X)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(kernel_matrix, cmap='viridis', aspect='auto')
        plt.colorbar(label='Kernel Value')
        plt.title(title)
        plt.xlabel('Sample Index')
        plt.ylabel('Sample Index')
        plt.show()
        
        return kernel_matrix


def create_datasets():
    """Create sample datasets for QSVM testing"""
    datasets = {}
    
    # XOR dataset
    np.random.seed(42)
    X_xor = np.random.randn(100, 2)
    y_xor = np.logical_xor(X_xor[:, 0] > 0, X_xor[:, 1] > 0).astype(int)
    datasets['xor'] = (X_xor, y_xor)
    
    # Moons dataset
    X_moons, y_moons = make_moons(n_samples=100, noise=0.1, random_state=42)
    datasets['moons'] = (X_moons, y_moons)
    
    # Circle dataset
    X_circle, y_circle = make_classification(n_samples=100, n_features=2, 
                                           n_redundant=0, n_informative=2,
                                           n_clusters_per_class=1, 
                                           class_sep=1.5, random_state=42)
    datasets['circle'] = (X_circle, y_circle)
    
    return datasets


def compare_classical_quantum_svm():
    """Compare classical and quantum SVM performance"""
    print("Classical vs Quantum SVM Comparison")
    print("=" * 40)
    
    # Create datasets
    datasets = create_datasets()
    
    results = {}
    
    for name, (X, y) in datasets.items():
        print(f"\\nDataset: {name}")
        print("-" * 20)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        # Standardize
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Classical SVM
        classical_svm = SVC(kernel='rbf', C=1.0)
        classical_svm.fit(X_train_scaled, y_train)
        classical_pred = classical_svm.predict(X_test_scaled)
        classical_acc = accuracy_score(y_test, classical_pred)
        
        # Quantum SVM
        qsvm = QuantumSVM(feature_dim=X.shape[1])
        qsvm.train_qsvc(X_train_scaled, y_train)
        quantum_results = qsvm.evaluate(X_test_scaled, y_test)
        
        # Store results
        results[name] = {
            'classical_accuracy': classical_acc,
            'quantum_accuracy': quantum_results['accuracy'],
            'improvement': quantum_results['accuracy'] - classical_acc
        }
        
        print(f"Classical SVM Accuracy: {classical_acc:.3f}")
        print(f"Quantum SVM Accuracy: {quantum_results['accuracy']:.3f}")
        print(f"Improvement: {results[name]['improvement']:+.3f}")
    
    return results


def quantum_kernel_analysis():
    """Analyze quantum kernel properties"""
    print("Quantum Kernel Analysis")
    print("=" * 25)
    
    # Create sample data
    X, y = make_moons(n_samples=50, noise=0.1, random_state=42)
    
    # Create quantum SVM
    qsvm = QuantumSVM(feature_dim=2)
    qsvm.create_quantum_kernel()
    
    # Analyze kernel matrix
    kernel_matrix = QuantumKernelMatrix(qsvm.qkernel)
    matrix = kernel_matrix.visualize_kernel_matrix(X, "Quantum Kernel Matrix")
    
    # Kernel properties
    print("Kernel Matrix Properties:")
    print(f"Matrix size: {matrix.shape}")
    print(f"Positive definite: {np.all(np.linalg.eigvals(matrix) > 0)}")
    print(f"Condition number: {np.linalg.cond(matrix):.2e}")
    
    return matrix


def quantum_svm_applications():
    """Demonstrate quantum SVM applications"""
    print("Quantum SVM Applications")
    print("=" * 30)
    
    applications = [
        {
            'name': 'Financial Market Prediction',
            'description': 'Stock price movement prediction using quantum features',
            'advantages': 'Quantum entanglement captures market correlations'
        },
        {
            'name': 'Medical Diagnosis',
            'description': 'Disease classification using quantum medical imaging',
            'advantages': 'Quantum superposition for medical pattern recognition'
        },
        {
            'name': 'Natural Language Processing',
            'description': 'Text classification with quantum text embeddings',
            'advantages': 'Quantum feature space provides better separability'
        },
        {
            'name': 'Image Recognition',
            'description': 'Quantum-enhanced image classification',
            'advantages': 'Quantum kernels exploit quantum correlations in pixels'
        }
    ]
    
    for app in applications:
        print(f"\\n{app['name']}:")
        print(f"  Description: {app['description']}")
        print(f"  Advantages: {app['advantages']}")


def main():
    """Main QSVM demonstration"""
    print("Quantum Support Vector Machines (QSVM)")
    print("=" * 40)
    
    # Create QSVM instance
    qsvm = QuantumSVM(feature_dim=2)
    
    # Create and test with sample data
    X, y = make_moons(n_samples=50, noise=0.1, random_state=42)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Train quantum SVM
    qsvm.train_qsvc(X_train, y_train)
    
    # Evaluate performance
    results = qsvm.evaluate(X_test, y_test)
    print(f"\\nQuantum SVM Accuracy: {results['accuracy']:.3f}")
    
    # Demonstrate quantum advantage
    quantum_features = qsvm.demonstrate_quantum_advantage(X_train, X_test)
    
    # Compare classical and quantum SVM
    comparison_results = compare_classical_quantum_svm()
    
    # Quantum kernel analysis
    kernel_matrix = quantum_kernel_analysis()
    
    # Applications
    quantum_svm_applications()
    
    return qsvm, results, comparison_results, quantum_features


if __name__ == "__main__":
    main()