"""
Online Learning Demo - Real-time model adaptation

Ushbu demo online learning va concept drift detection qanday ishlashini ko'rsatadi
"""

import sys
import os
import numpy as np
import pandas as pd
import torch
import asyncio
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from self_improving.online_learning import OnlineLearningEngine
from adaptive_mechanisms.concept_drift import ConceptDriftDetector
from implementation.streaming_data_processing import StreamingDataProcessor
from core.adaptive_model import AdaptiveModel


class OnlineLearningDemo:
    """Online Learning demo tizimi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Componentlarni yaratish
        self.model = self.create_model()
        self.online_learner = OnlineLearningEngine(
            model=self.model,
            update_frequency=1,  # Har yangilanishda
            adaptation_threshold=0.05
        )
        
        self.concept_drift_detector = ConceptDriftDetector(
            window_size=100,
            threshold=0.05,
            method='ks_test'
        )
        
        self.streaming_processor = StreamingDataProcessor(
            buffer_size=1000,
            processing_interval=1  # Tez simulyatsiya
        )
        
        # Demo ma'lumotlari
        self.drift_points = [200, 400, 600, 800]  # Concept drift sodir bo'lish nuqtalari
        self.generate_streaming_data()
        
    def setup_logging(self):
        """Logging sozlamalar"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def create_model(self):
        """Model yaratish"""
        return AdaptiveModel(
            input_features=10,
            hidden_layers=[32, 16],
            output_size=1,
            learning_rate=0.01
        )
    
    def generate_streaming_data(self):
        """Streaming data generation"""
        self.logger.info("Streaming ma'lumotlar yaratilmoqda...")
        
        # 1000 kunlik data
        total_points = 1000
        np.random.seed(42)
        
        self.data_stream = []
        
        for i in range(total_points):
            # X ma'lumotlar (features)
            X = np.random.randn(10)
            
            # Y target (trend bilan)
            if i < self.drift_points[0]:  # Birinchi phase
                base_trend = 1.0
                coefficient = 0.8
            elif i < self.drift_points[1]:  # Ikkinchi phase
                base_trend = 1.5
                coefficient = -0.6
            elif i < self.drift_points[2]:  # Uchinchi phase
                base_trend = 0.8
                coefficient = 1.2
            else:  # To'rtinchi phase
                base_trend = -0.5
                coefficient = 0.9
            
            # Noise qo'shish
            noise = np.random.normal(0, 0.1)
            y = base_trend + coefficient * X[0] + noise
            
            self.data_stream.append({
                'timestamp': datetime.now() - timedelta(days=total_points-i),
                'features': X,
                'target': y,
                'point_id': i
            })
        
        self.logger.info(f"{len(self.data_stream)} ta ma'lumot nuqta yaratildi")
    
    async def run_online_learning_simulation(self):
        """Online learning simulyatsiyasi"""
        self.logger.info("Online learning simulyatsiyasi boshlanmoqda...")
        
        adaptation_history = []
        drift_history = []
        prediction_history = []
        
        for i, data_point in enumerate(self.data_stream):
            # Streaming data process qilish
            processed_data = await self.streaming_processor.process_data(data_point)
            
            # Prediction qilish
            features_tensor = torch.tensor(data_point['features'], dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                prediction = self.model(features_tensor).item()
            
            prediction_history.append(prediction)
            
            # Actual target
            actual = data_point['target']
            
            # Prediction error
            error = abs(prediction - actual)
            
            # Concept drift check
            recent_window = [dp['target'] for dp in self.data_stream[max(0, i-99):i+1]]
            
            if len(recent_window) > 10:
                is_drift = self.concept_drift_detector.detect_drift(
                    current_window=recent_window
                )
                
                if is_drift:
                    drift_history.append({
                        'point_id': i,
                        'timestamp': data_point['timestamp'],
                        'drift_score': self.concept_drift_detector.last_drift_score
                    })
                    self.logger.info(f"🚨 Concept drift aniqlandi: nuqta {i}")
            
            # Online learning update
            should_update = False
            
            # Adaptation threshold check
            if error > self.online_learner.adaptation_threshold:
                should_update = True
            
            # Periodic update (har 10 nuqta da)
            if i % 10 == 0:
                should_update = True
            
            if should_update:
                # Model update
                update_result = await self.online_learner.update_model(
                    new_data={
                        'features': data_point['features'],
                        'target': actual,
                        'error': error
                    },
                    force_update=True
                )
                
                adaptation_history.append({
                    'point_id': i,
                    'timestamp': data_point['timestamp'],
                    'update_reason': 'threshold' if error > self.online_learner.adaptation_threshold else 'periodic',
                    'error_before': error,
                    'performance_improvement': update_result.get('improvement', 0)
                })
                
                self.logger.info(
                    f"Model yangilandi (nuqta {i}): "
                    f"Error={error:.3f}, Improvement={update_result.get('improvement', 0):.3f}"
                )
            
            # Progress reporting
            if i % 100 == 0:
                self.logger.info(
                    f"Progress: {i}/{len(self.data_stream)} "
                    f"(Current error: {error:.3f})"
                )
        
        # Simulyatsiya natijalarini analiz qilish
        self.analyze_results(prediction_history, adaptation_history, drift_history)
        
        return {
            'prediction_history': prediction_history,
            'adaptation_history': adaptation_history,
            'drift_history': drift_history,
            'total_adaptations': len(adaptation_history),
            'drift_detections': len(drift_history)
        }
    
    def analyze_results(self, prediction_history, adaptation_history, drift_history):
        """Natijalarni analiz qilish"""
        self.logger.info("\n" + "="*50)
        self.logger.info("ONLINE LEARNING ANALIZ NATIJALARI")
        self.logger.info("="*50)
        
        # 1. Drift nuqtalari analizi
        self.logger.info(f"\n1️⃣ CONCEPT DRIFT DETECTION:")
        self.logger.info(f"   • Jami drift aniqlandi: {len(drift_history)}")
        for drift in drift_history:
            self.logger.info(f"   • Nuqta {drift['point_id']}: "
                           f"Score={drift['drift_score']:.3f}")
        
        # Drift accuracy
        expected_drifts = self.drift_points
        detected_drifts = [d['point_id'] for d in drift_history]
        
        drift_accuracy = 0
        for expected in expected_drifts:
            closest_detected = min(detected_drifts, 
                                 key=lambda x: abs(x - expected),
                                 default=None)
            if closest_detected and abs(closest_detected - expected) <= 50:
                drift_accuracy += 1
        
        drift_accuracy /= len(expected_drifts)
        self.logger.info(f"   • Drift detection accuracy: {drift_accuracy:.1%}")
        
        # 2. Model adaptation natijalari
        self.logger.info(f"\n2️⃣ MODEL ADAPTATIONS:")
        self.logger.info(f"   • Jami yangilanish: {len(adaptation_history)}")
        
        # Adaptation reasons
        reasons = {}
        for adaptation in adaptation_history:
            reason = adaptation['update_reason']
            reasons[reason] = reasons.get(reason, 0) + 1
        
        for reason, count in reasons.items():
            self.logger.info(f"   • {reason}: {count} marta")
        
        # Performance improvements
        improvements = [a['performance_improvement'] for a in adaptation_history 
                       if a['performance_improvement'] != 0]
        if improvements:
            avg_improvement = np.mean(improvements)
            max_improvement = np.max(improvements)
            self.logger.info(f"   • O'rtacha yaxshilash: {avg_improvement:.3f}")
            self.logger.info(f"   • Maksimal yaxshilash: {max_improvement:.3f}")
        
        # 3. Prediction accuracy
        actual_targets = [dp['target'] for dp in self.data_stream]
        
        # Split by phases
        phases = [
            (0, 200, "Phase 1"),
            (200, 400, "Phase 2"), 
            (400, 600, "Phase 3"),
            (600, 800, "Phase 4"),
            (800, 1000, "Phase 5")
        ]
        
        self.logger.info(f"\n3️⃣ PREDICTION ACCURACY BY PHASE:")
        for start, end, phase_name in phases:
            phase_predictions = prediction_history[start:end]
            phase_actual = actual_targets[start:end]
            
            # MAE hisoblash
            mae = np.mean(np.abs(np.array(phase_predictions) - np.array(phase_actual)))
            
            # RMSE hisoblash
            rmse = np.sqrt(np.mean((np.array(phase_predictions) - np.array(phase_actual))**2))
            
            self.logger.info(f"   • {phase_name} (nuqtalar {start}-{end}):")
            self.logger.info(f"     - MAE: {mae:.3f}")
            self.logger.info(f"     - RMSE: {rmse:.3f}")
        
        # 4. Overall performance
        overall_mae = np.mean(np.abs(np.array(prediction_history) - np.array(actual_targets)))
        overall_rmse = np.sqrt(np.mean((np.array(prediction_history) - np.array(actual_targets))**2))
        
        self.logger.info(f"\n4️⃣ OVERALL PERFORMANCE:")
        self.logger.info(f"   • Overall MAE: {overall_mae:.3f}")
        self.logger.info(f"   • Overall RMSE: {overall_rmse:.3f}")
        self.logger.info(f"   • Model response to drift: "
                        f"{'✅ Yaxshi' if drift_accuracy > 0.6 else '⚠️ O\'rtacha' if drift_accuracy > 0.3 else '❌ Yomon'}")
        
        # 5. Recommendations
        self.logger.info(f"\n5️⃣ TAVSIYALAR:")
        
        if len(drift_history) < len(self.drift_points):
            self.logger.info(f"   • Concept drift detection threshold pasaytirilishi mumkin")
        
        if np.mean([a['performance_improvement'] for a in adaptation_history if a['performance_improvement'] > 0]) < 0.1:
            self.logger.info(f"   • Adaptation strategy ko'rib chiqilishi kerak")
        
        if overall_mae > 1.0:
            self.logger.info(f"   • Model architecture qayta ko'rib chiqilishi kerak")
        
        self.logger.info("="*50)
    
    def create_visualization(self, results):
        """Natijalarni visualizatsiya qilish"""
        self.logger.info("Visualizatsiya yaratilmoqda...")
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # 1. Actual vs Predicted
        actual_targets = [dp['target'] for dp in self.data_stream]
        axes[0].plot(actual_targets, label='Actual', alpha=0.7)
        axes[0].plot(results['prediction_history'], label='Predicted', alpha=0.7)
        
        # Drift nuqtalarini belgilash
        for drift in results['drift_history']:
            axes[0].axvline(x=drift['point_id'], color='red', linestyle='--', alpha=0.5)
            axes[0].text(drift['point_id'], max(actual_targets), 'Drift', 
                        rotation=90, fontsize=8, color='red')
        
        axes[0].set_title('Actual vs Predicted Values')
        axes[0].set_xlabel('Data Point')
        axes[0].set_ylabel('Value')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 2. Adaptation timeline
        adaptation_points = [a['point_id'] for a in results['adaptation_history']]
        adaptation_reasons = [a['update_reason'] for a in results['adaptation_history']]
        
        colors = {'threshold': 'blue', 'periodic': 'green'}
        for i, (point, reason) in enumerate(zip(adaptation_points, adaptation_reasons)):
            axes[1].scatter(point, 1, c=colors.get(reason, 'gray'), 
                          alpha=0.6, s=50)
        
        axes[1].set_title('Model Adaptation Timeline')
        axes[1].set_xlabel('Data Point')
        axes[1].set_ylabel('Adaptation')
        axes[1].set_ylim(0.5, 1.5)
        axes[1].grid(True, alpha=0.3)
        
        # Drift nuqtalarini ham qo'shish
        for drift in results['drift_history']:
            axes[1].axvline(x=drift['point_id'], color='red', linestyle='--', alpha=0.3)
        
        # 3. Performance over time
        window_size = 50
        moving_errors = []
        
        for i in range(len(actual_targets) - window_size + 1):
            window_actual = actual_targets[i:i+window_size]
            window_pred = results['prediction_history'][i:i+window_size]
            window_mae = np.mean(np.abs(np.array(window_pred) - np.array(window_actual)))
            moving_errors.append(window_mae)
        
        axes[2].plot(range(window_size-1, len(actual_targets)), moving_errors)
        axes[2].set_title('Moving Average Error (Window Size: 50)')
        axes[2].set_xlabel('Data Point')
        axes[2].set_ylabel('MAE')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('online_learning_results.png', dpi=300, bbox_inches='tight')
        self.logger.info("Visualizatsiya 'online_learning_results.png' ga saqlandi")


async def main():
    """Asosiy demo funksiya"""
    print("🚀 ONLINE LEARNING DEMO")
    print("="*40)
    
    try:
        demo = OnlineLearningDemo()
        
        # Online learning simulyatsiyasi
        print("\n1️⃣ Online Learning Simulyatsiyasi...")
        results = await demo.run_online_learning_simulation()
        
        # Visualizatsiya yaratish
        print("\n2️⃣ Visualizatsiya Yaratish...")
        demo.create_visualization(results)
        
        # Natijalarni konsolga chiqarish
        print(f"\n📊 DEMO NATIJALARI:")
        print(f"   • Processing points: {len(demo.data_stream)}")
        print(f"   • Drift detections: {results['drift_detections']}")
        print(f"   • Model adaptations: {results['total_adaptations']}")
        print(f"   • Visualization saved: online_learning_results.png")
        
        print(f"\n✅ Demo muvaffaqiyatli tugallandi!")
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {e}")
        logging.error(f"Demo xatosi: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())