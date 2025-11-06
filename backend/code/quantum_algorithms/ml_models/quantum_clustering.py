"""
Quantum Clustering Algorithms
Quantum-enhanced clustering methods
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_moons, make_circles
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import ZZFeatureMap, ZFeatureMap
import matplotlib.pyplot as plt

class QuantumKMeans:
    """
    Quantum-enhanced K-Means clustering
    """
    
    def __init__(self, n_clusters=3, n_qubits=4, encoding='angle'):
        """
        Args:
            n_clusters (int): Number of clusters
            n_qubits (int): Number of qubits for quantum computation
            encoding (str): Type of quantum encoding ('angle', 'amplitude', 'zz')
        """
        self.n_clusters = n_clusters
        self.n_qubits = n_qubits
        self.encoding = encoding
        self.cluster_centers = []
        self.quantum_circuits = []
        
    def encode_data(self, X):
        """Encode classical data into quantum states"""
        encoded_data = []
        
        if self.encoding == 'angle':
            encoded_data = self._angle_encoding(X)
        elif self.encoding == 'amplitude':
            encoded_data = self._amplitude_encoding(X)
        elif self.encoding == 'zz':
            encoded_data = self._zz_encoding(X)
        else:
            # Default to angle encoding
            encoded_data = self._angle_encoding(X)
            
        return encoded_data
    
    def _angle_encoding(self, X):
        """Angle encoding of data"""
        quantum_data = []
        
        for sample in X:
            qc = QuantumCircuit(self.n_qubits, self.n_qubits)
            
            # Scale data to [0, π]
            scaled_data = (X - np.min(X, axis=0)) / (np.max(X, axis=0) - np.min(X, axis=0)) * np.pi
            
            for i in range(min(self.n_qubits, len(sample))):
                qc.ry(scaled_data[0, i], i)  # Use first sample for scaling
            
            # Add entanglement
            for i in range(self.n_qubits - 1):
                qc.cx(i, i + 1)
                
            quantum_data.append(qc)
            
        return quantum_data
    
    def _amplitude_encoding(self, X):
        """Amplitude encoding of data"""
        quantum_data = []
        
        for sample in X:
            qc = QuantumCircuit(self.n_qubits)
            
            # Normalize data
            norm = np.linalg.norm(sample)
            if norm > 0:
                normalized_sample = sample / norm
            else:
                normalized_sample = sample
                
            # Amplitude encoding (simplified)
            for i in range(min(self.n_qubits, len(normalized_sample))):
                angle = np.arccos(np.sqrt(abs(normalized_sample[i])))
                qc.ry(2 * angle, i)
                
            quantum_data.append(qc)
            
        return quantum_data
    
    def _zz_encoding(self, X):
        """ZZ feature map encoding"""
        quantum_data = []
        
        # Create ZZ feature map
        feature_map = ZZFeatureMap(feature_dimension=self.n_qubits, reps=2)
        
        for sample in X:
            # Create circuit with ZZ encoding
            qc = feature_map.bind_parameters(sample[:self.n_qubits])
            quantum_data.append(qc)
            
        return quantum_data
    
    def quantum_distance(self, quantum_data1, quantum_data2):
        """Compute quantum distance between two encoded data points"""
        # Simplified quantum distance computation
        # In practice, would use fidelity or other quantum metrics
        
        # For demo, use measurement statistics
        distance = 0
        
        for qc1, qc2 in zip(quantum_data1, quantum_data2):
            # Measure both circuits
            qc1.measure_all()
            qc2.measure_all()
            
            backend = Aer.get_backend('qasm_simulator')
            
            job1 = execute(qc1, backend, shots=100)
            job2 = execute(qc2, backend, shots=100)
            
            result1 = job1.result()
            result2 = job2.result()
            
            counts1 = result1.get_counts()
            counts2 = result2.get_counts()
            
            # Compute distance based on measurement differences
            all_bitstrings = set(counts1.keys()) | set(counts2.keys())
            
            total_diff = 0
            total_shots = 0
            
            for bitstring in all_bitstrings:
                count1 = counts1.get(bitstring, 0)
                count2 = counts2.get(bitstring, 0)
                
                total_diff += abs(count1 - count2)
                total_shots += count1 + count2
            
            if total_shots > 0:
                distance += total_diff / total_shots
                
        return distance / len(quantum_data1) if quantum_data1 else 0
    
    def fit_quantum(self, X):
        """Quantum-enhanced K-means fitting"""
        print(f"Quantum K-Means with {self.n_clusters} clusters")
        print("=" * 45)
        
        # Encode data
        quantum_data = self.encode_data(X)
        
        # Initialize cluster centers randomly
        self.cluster_centers = np.random.randn(self.n_clusters, X.shape[1])
        
        max_iterations = 20
        for iteration in range(max_iterations):
            print(f"Iteration {iteration + 1}")
            
            # Assign points to clusters
            labels = []
            for i, sample in enumerate(X):
                # Find nearest cluster center (quantum-enhanced)
                distances = []
                for center in self.cluster_centers:
                    # Create quantum representation of center
                    center_quantum = self.encode_data([center])[0]
                    
                    # Compute quantum distance
                    dist = self.quantum_distance([quantum_data[i]], [center_quantum])
                    distances.append(dist)
                
                cluster = np.argmin(distances)
                labels.append(cluster)
            
            # Update cluster centers
            new_centers = []
            for cluster_id in range(self.n_clusters):
                cluster_points = X[np.array(labels) == cluster_id]
                if len(cluster_points) > 0:
                    new_centers.append(np.mean(cluster_points, axis=0))
                else:
                    new_centers.append(self.cluster_centers[cluster_id])
            
            new_centers = np.array(new_centers)
            
            # Check convergence
            center_shift = np.linalg.norm(new_centers - self.cluster_centers)
            self.cluster_centers = new_centers
            
            print(f"  Center shift: {center_shift:.4f}")
            
            if center_shift < 1e-6:
                break
        
        return np.array(labels)
    
    def predict_quantum(self, X):
        """Predict cluster labels for new data"""
        quantum_data = self.encode_data(X)
        labels = []
        
        for i, sample in enumerate(X):
            distances = []
            for center in self.cluster_centers:
                center_quantum = self.encode_data([center])[0]
                dist = self.quantum_distance([quantum_data[i]], [center_quantum])
                distances.append(dist)
            
            cluster = np.argmin(distances)
            labels.append(cluster)
        
        return np.array(labels)


class QuantumHierarchicalClustering:
    """
    Quantum Hierarchical Clustering
    """
    
    def __init__(self, n_qubits=4):
        """
        Args:
            n_qubits (int): Number of qubits
        """
        self.n_qubits = n_qubits
        self.distance_matrix = None
        
    def quantum_distance_matrix(self, X):
        """Compute quantum distance matrix"""
        n_samples = len(X)
        distance_matrix = np.zeros((n_samples, n_samples))
        
        # Create quantum encoding
        qkmeans = QuantumKMeans(n_clusters=2, n_qubits=self.n_qubits)
        quantum_data = qkmeans.encode_data(X)
        
        for i in range(n_samples):
            for j in range(i + 1, n_samples):
                # Quantum distance computation
                distance = qkmeans.quantum_distance([quantum_data[i]], [quantum_data[j]])
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance
        
        self.distance_matrix = distance_matrix
        return distance_matrix
    
    def agglomerative_clustering(self, X, n_clusters=3):
        """Quantum-enhanced agglomerative clustering"""
        print(f"Quantum Agglomerative Clustering to {n_clusters} clusters")
        print("=" * 50)
        
        # Compute quantum distance matrix
        distance_matrix = self.quantum_distance_matrix(X)
        
        # Initialize clusters
        clusters = list(range(len(X)))
        cluster_data = {i: [i] for i in range(len(X))}
        
        while len(clusters) > n_clusters:
            # Find closest pair of clusters
            min_distance = float('inf')
            merge_clusters = None
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    cluster1 = cluster_data[clusters[i]]
                    cluster2 = cluster_data[clusters[j]]
                    
                    # Compute inter-cluster distance
                    inter_distance = 0
                    count = 0
                    
                    for point1 in cluster1:
                        for point2 in cluster2:
                            inter_distance += distance_matrix[point1][point2]
                            count += 1
                    
                    if count > 0:
                        inter_distance /= count
                    
                    if inter_distance < min_distance:
                        min_distance = inter_distance
                        merge_clusters = (clusters[i], clusters[j])
            
            # Merge clusters
            if merge_clusters:
                cluster1_id, cluster2_id = merge_clusters
                
                # Merge data
                merged_data = cluster_data[cluster1_id] + cluster_data[cluster2_id]
                
                # Update clusters
                cluster_data[cluster1_id] = merged_data
                del cluster_data[cluster2_id]
                clusters.remove(cluster2_id)
                
                print(f"Merged clusters {cluster1_id} and {cluster2_id}, "
                      f"distance: {min_distance:.4f}")
        
        # Convert to labels
        labels = np.zeros(len(X), dtype=int)
        for cluster_id, points in cluster_data.items():
            for point in points:
                labels[point] = cluster_id
        
        return labels


class QuantumDBSCAN:
    """
    Quantum-enhanced DBSCAN clustering
    """
    
    def __init__(self, eps=0.5, min_samples=5, n_qubits=4):
        """
        Args:
            eps (float): Maximum distance between points in neighborhood
            min_samples (int): Minimum samples in neighborhood
            n_qubits (int): Number of qubits
        """
        self.eps = eps
        self.min_samples = min_samples
        self.n_qubits = n_qubits
        
    def quantum_neighborhood(self, X, point_idx):
        """Find quantum neighborhood of a point"""
        qkmeans = QuantumKMeans(n_clusters=2, n_qubits=self.n_qubits)
        quantum_data = qkmeans.encode_data(X)
        
        neighborhood = []
        quantum_point = quantum_data[point_idx]
        
        for i, other_point in enumerate(quantum_data):
            if i != point_idx:
                distance = qkmeans.quantum_distance([quantum_point], [other_point])
                if distance <= self.eps:
                    neighborhood.append(i)
        
        return neighborhood
    
    def fit_quantum(self, X):
        """Quantum-enhanced DBSCAN fitting"""
        print(f"Quantum DBSCAN: eps={self.eps}, min_samples={self.min_samples}")
        print("=" * 55)
        
        n_samples = len(X)
        labels = np.full(n_samples, -1, dtype=int)
        cluster_id = 0
        
        visited = set()
        
        for i in range(n_samples):
            if i in visited:
                continue
                
            visited.add(i)
            
            # Find quantum neighborhood
            neighborhood = self.quantum_neighborhood(X, i)
            
            if len(neighborhood) < self.min_samples:
                # Noise point
                labels[i] = -1
            else:
                # Start new cluster
                labels[i] = cluster_id
                
                # Expand cluster
                j = 0
                while j < len(neighborhood):
                    neighbor = neighborhood[j]
                    
                    if neighbor not in visited:
                        visited.add(neighbor)
                        
                        # Find neighborhood of neighbor
                        neighbor_hood = self.quantum_neighborhood(X, neighbor)
                        
                        if len(neighbor_hood) >= self.min_samples:
                            neighborhood.extend(neighbor_hood)
                    
                    if labels[neighbor] == -1:
                        labels[neighbor] = cluster_id
                    
                    j += 1
                
                cluster_id += 1
        
        print(f"Found {cluster_id} clusters")
        print(f"Noise points: {np.sum(labels == -1)}")
        
        return labels


class QuantumSpectralClustering:
    """
    Quantum-enhanced Spectral Clustering
    """
    
    def __init__(self, n_clusters=3, n_qubits=4):
        """
        Args:
            n_clusters (int): Number of clusters
            n_qubits (int): Number of qubits
        """
        self.n_clusters = n_clusters
        self.n_qubits = n_qubits
        
    def create_quantum_similarity_matrix(self, X):
        """Create quantum similarity matrix"""
        n_samples = len(X)
        similarity_matrix = np.zeros((n_samples, n_samples))
        
        # Use quantum K-means for distance computation
        qkmeans = QuantumKMeans(n_clusters=2, n_qubits=self.n_qubits)
        quantum_data = qkmeans.encode_data(X)
        
        for i in range(n_samples):
            for j in range(n_samples):
                if i != j:
                    # Quantum distance
                    distance = qkmeans.quantum_distance([quantum_data[i]], [quantum_data[j]])
                    
                    # Convert distance to similarity (using RBF kernel)
                    similarity = np.exp(-distance**2 / (2 * self.n_qubits))
                    similarity_matrix[i, j] = similarity
        
        return similarity_matrix
    
    def fit_quantum(self, X):
        """Quantum spectral clustering"""
        print(f"Quantum Spectral Clustering with {self.n_clusters} clusters")
        print("=" * 55)
        
        # Create quantum similarity matrix
        similarity_matrix = self.create_quantum_similarity_matrix(X)
        
        # Normalize and apply spectral clustering
        # For simplicity, use quantum K-means on transformed features
        
        # Transform features using quantum similarity
        quantum_features = []
        for i in range(len(X)):
            # Use quantum similarity as features
            feature = similarity_matrix[i]
            quantum_features.append(feature)
        
        quantum_features = np.array(quantum_features)
        
        # Apply classical K-means to quantum features
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(quantum_features)
        
        print(f"Spectral clustering completed")
        
        return labels


def create_test_datasets():
    """Create test datasets for clustering"""
    datasets = {}
    
    # Blobs dataset
    X_blobs, y_blobs = make_blobs(n_samples=150, centers=3, n_features=2, 
                                 random_state=42, cluster_std=1.0)
    datasets['blobs'] = (X_blobs, y_blobs)
    
    # Moons dataset
    X_moons, y_moons = make_moons(n_samples=150, noise=0.1, random_state=42)
    datasets['moons'] = (X_moons, y_moons)
    
    # Circles dataset
    X_circles, y_circles = make_circles(n_samples=150, noise=0.1, 
                                       factor=0.3, random_state=42)
    datasets['circles'] = (X_circles, y_circles)
    
    return datasets


def compare_clustering_methods():
    """Compare different quantum clustering methods"""
    print("Quantum Clustering Methods Comparison")
    print("=" * 40)
    
    datasets = create_test_datasets()
    
    results = {}
    
    for name, (X, y_true) in datasets.items():
        print(f"\\nDataset: {name}")
        print("-" * 20)
        
        # Standardize data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        methods = {
            'Quantum K-Means': QuantumKMeans(n_clusters=3, n_qubits=4),
            'Quantum DBSCAN': QuantumDBSCAN(eps=0.3, min_samples=5, n_qubits=4),
            'Quantum Spectral': QuantumSpectralClustering(n_clusters=3, n_qubits=4)
        }
        
        method_results = {}
        
        for method_name, method in methods.items():
            try:
                # Fit and predict
                if hasattr(method, 'fit_quantum'):
                    y_pred = method.fit_quantum(X_scaled)
                else:
                    y_pred = method.fit(X_scaled)
                
                # Calculate metrics
                if len(np.unique(y_pred)) > 1:
                    if -1 in y_pred:  # DBSCAN with noise
                        # Remove noise points for metrics
                        non_noise_mask = y_pred != -1
                        if np.sum(non_noise_mask) > 0:
                            y_pred_clean = y_pred[non_noise_mask]
                            y_true_clean = y_true[non_noise_mask]
                            ari = adjusted_rand_score(y_true_clean, y_pred_clean)
                        else:
                            ari = 0
                    else:
                        ari = adjusted_rand_score(y_true, y_pred)
                else:
                    ari = 0
                
                # Silhouette score (only for non-noise points)
                if hasattr(method, 'fit_quantum') and -1 not in y_pred:
                    try:
                        sil_score = silhouette_score(X_scaled, y_pred)
                    except:
                        sil_score = 0
                else:
                    sil_score = 0
                
                method_results[method_name] = {
                    'labels': y_pred,
                    'ari': ari,
                    'silhouette': sil_score
                }
                
                print(f"  {method_name}: ARI = {ari:.3f}, Silhouette = {sil_score:.3f}")
                
            except Exception as e:
                print(f"  {method_name}: Failed - {str(e)}")
                method_results[method_name] = {'error': str(e)}
        
        results[name] = method_results
    
    return results


def quantum_clustering_visualization():
    """Visualize quantum clustering results"""
    print("Quantum Clustering Visualization")
    print("=" * 35)
    
    # Create test data
    np.random.seed(42)
    X = np.random.randn(100, 2)
    X[:30] += np.array([2, 2])  # Cluster 1
    X[30:60] += np.array([2, -2])  # Cluster 2
    X[60:] += np.array([-2, 0])  # Cluster 3
    
    # Apply different clustering methods
    methods = {
        'Quantum K-Means': QuantumKMeans(n_clusters=3, n_qubits=4),
        'Quantum DBSCAN': QuantumDBSCAN(eps=1.0, min_samples=5, n_qubits=4),
        'Quantum Spectral': QuantumSpectralClustering(n_clusters=3, n_qubits=4)
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, (method_name, method) in enumerate(methods.items()):
        try:
            if hasattr(method, 'fit_quantum'):
                labels = method.fit_quantum(X)
            else:
                labels = method.fit_predict(X)
            
            # Plot results
            scatter = axes[idx].scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', alpha=0.7)
            
            if hasattr(method, 'cluster_centers'):
                centers = method.cluster_centers
                if len(centers) > 0:
                    axes[idx].scatter(centers[:, 0], centers[:, 1], 
                                    c='red', marker='x', s=200, linewidths=3, label='Centers')
            
            axes[idx].set_title(method_name)
            axes[idx].set_xlabel('Feature 1')
            axes[idx].set_ylabel('Feature 2')
            axes[idx].grid(True, alpha=0.3)
            
            if len(np.unique(labels)) > 1:
                # Add colorbar
                plt.colorbar(scatter, ax=axes[idx])
        
        except Exception as e:
            axes[idx].text(0.5, 0.5, f'Error: {str(e)}', 
                          transform=axes[idx].transAxes, ha='center', va='center')
            axes[idx].set_title(method_name)
    
    plt.tight_layout()
    plt.show()


def quantum_clustering_applications():
    """Quantum clustering applications"""
    print("Quantum Clustering Applications")
    print("=" * 35)
    
    applications = [
        {
            'domain': 'Financial Markets',
            'application': 'Portfolio clustering based on quantum correlation analysis',
            'quantum_advantage': 'Quantum entanglement captures complex market relationships'
        },
        {
            'domain': 'Medical Imaging',
            'application': 'Disease pattern recognition using quantum feature spaces',
            'quantum_advantage': 'Quantum superposition reveals hidden medical patterns'
        },
        {
            'domain': 'Molecular Biology',
            'application': 'Protein structure clustering with quantum similarity',
            'quantum_advantage': 'Quantum quantum chemistry simulation for protein interactions'
        },
        {
            'domain': 'Social Networks',
            'application': 'Community detection using quantum network analysis',
            'quantum_advantage': 'Quantum graph algorithms for complex network structures'
        },
        {
            'domain': 'Climate Science',
            'application': 'Weather pattern clustering with quantum spatio-temporal analysis',
            'quantum_advantage': 'Quantum simulation of atmospheric dynamics'
        }
    ]
    
    for app in applications:
        print(f"\\n{app['domain']}:")
        print(f"  Application: {app['application']}")
        print(f"  Quantum Advantage: {app['quantum_advantage']}")


def main():
    """Main quantum clustering demonstration"""
    print("Quantum Clustering Algorithms")
    print("=" * 35)
    
    # Compare clustering methods
    results = compare_clustering_methods()
    
    # Visualization
    quantum_clustering_visualization()
    
    # Applications
    quantum_clustering_applications()
    
    return results


if __name__ == "__main__":
    main()