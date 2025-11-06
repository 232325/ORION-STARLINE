"""
ML Model Updates Demo
Tizimni ishlatish bo'yicha demo
"""

import numpy as np
import pandas as pd
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import MLModelUpdateSystem
from utils.helpers import data_loader, data_saver, model_validator, performance_profiler

def create_sample_data():
    """Demo uchun sample data yaratish"""
    np.random.seed(42)
    
    # Classification dataset
    classification_data = pd.DataFrame({
        'feature1': np.random.randn(1000),
        'feature2': np.random.randn(1000),
        'feature3': np.random.randn(1000),
        'feature4': np.random.randn(1000),
        'categorical_feature': np.random.choice(['A', 'B', 'C'], 1000),
        'protected_attribute': np.random.choice(['Group_X', 'Group_Y'], 1000),
        'target': np.random.choice([0, 1], 1000)
    })
    
    # Regression dataset
    regression_data = pd.DataFrame({
        'feature1': np.random.randn(1000),
        'feature2': np.random.randn(1000),
        'feature3': np.random.randn(1000),
        'feature4': np.random.randn(1000),
        'categorical_feature': np.random.choice(['A', 'B', 'C'], 1000),
        'target': np.random.randn(1000) * 10 + 50  # Target with some noise
    })
    
    return classification_data, regression_data

def demo_model_lifecycle():
    """Model lifecycle demo"""
    print("=" * 60)
    print("ML MODEL LIFECYCLE DEMO")
    print("=" * 60)
    
    # 1. System initialization
    print("\n1. Tizimni initialize qilish...")
    system = MLModelUpdateSystem("demo_config")
    
    # 2. Create sample data
    print("\n2. Sample data yaratish...")
    classification_data, regression_data = create_sample_data()
    print(f"Classification data shape: {classification_data.shape}")
    print(f"Regression data shape: {regression_data.shape}")
    
    # 3. Initialize models
    print("\n3. Modellarni initialize qilish...")
    
    # Classification model
    cls_version = system.initialize_model(
        model_name="customer_churn_classifier",
        model_type="classification",
        framework="sklearn"
    )
    print(f"Classification model initialized: {cls_version}")
    
    # Regression model
    reg_version = system.initialize_model(
        model_name="price_prediction_regressor",
        model_type="regression",
        framework="sklearn"
    )
    print(f"Regression model initialized: {reg_version}")
    
    return system, classification_data, regression_data

def demo_model_monitoring(system):
    """Model monitoring demo"""
    print("\n4. Model monitoring boshlanishi...")
    
    # Start monitoring for both models
    system.start_monitoring("customer_churn_classifier")
    system.start_monitoring("price_prediction_regressor")
    
    print("Monitoring started for both models")
    
    # Get system status
    print("\n5. Tizim statusini ko'rish...")
    overview = system.get_system_overview()
    print(f"Registered models count: {overview['registered_models_count']}")
    print(f"Monitoring status: {overview['monitoring_status']}")

def demo_automl_demo(system, classification_data):
    """AutoML demo"""
    print("\n6. AutoML pipeline demo...")
    
    try:
        automl_results = system.run_automl(
            model_name="automl_demo_classifier",
            training_data=classification_data,
            config={
                'task_type': 'classification',
                'algorithms': ['random_forest', 'gradient_boosting', 'logistic_regression'],
                'search_strategy': 'random',
                'max_trials': 10,
                'timeout_hours': 1.0,
                'cv_folds': 3,
                'optimization_metric': 'accuracy',
                'optimization_direction': 'maximize'
            }
        )
        
        print(f"AutoML status: {automl_results['status']}")
        if automl_results['status'] == 'completed':
            best_trial = automl_results['best_trial']
            print(f"Best algorithm: {best_trial['algorithm']}")
            print(f"Best CV score: {best_trial['cv_score']:.4f}")
            
    except Exception as e:
        print(f"AutoML demo xatosi: {str(e)}")

def demo_bias_analysis_demo(system, classification_data):
    """Bias analysis demo"""
    print("\n7. Bias analysis demo...")
    
    try:
        bias_results = system.analyze_bias(
            model_name="customer_churn_classifier",
            data=classification_data,
            protected_attributes=['protected_attribute', 'categorical_feature']
        )
        
        print(f"Protected attributes tested: {bias_results['protected_attributes_tested']}")
        print(f"Bias detected count: {bias_results['bias_detected_count']}")
        
        # Display detailed results
        for result in bias_results['results']:
            print(f"\nAttribute: {result['attribute']}")
            print(f"Bias detected: {result['bias_detected']}")
            print(f"Severity: {result['severity']}")
            
            if result['bias_detected']:
                print("Recommendations:")
                for rec in result['recommendations']:
                    print(f"  - {rec}")
                    
    except Exception as e:
        print(f"Bias analysis demo xatosi: {str(e)}")

def demo_model_status(system):
    """Model status demo"""
    print("\n8. Model status ko'rish...")
    
    models = ["customer_churn_classifier", "price_prediction_regressor"]
    
    for model_name in models:
        print(f"\n--- {model_name} Status ---")
        status = system.get_model_status(model_name)
        
        print(f"Version: {status.get('version_id', 'N/A')}")
        print(f"Framework: {status.get('framework', 'N/A')}")
        print(f"Model Type: {status.get('model_type', 'N/A')}")
        print(f"Created: {status.get('created_at', 'N/A')}")
        
        # Monitoring status
        monitoring = status.get('monitoring', {})
        if monitoring:
            print(f"Monitoring average accuracy: {monitoring.get('average_accuracy', 0):.4f}")
            
        # Governance status
        governance = status.get('governance', {})
        if governance:
            print(f"Risk Level: {governance.get('risk_level', 'N/A')}")
            print(f"Compliance Status: {governance.get('compliance_status', 'N/A')}")

def demo_utility_functions():
    """Utility functions demo"""
    print("\n9. Utility functions demo...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'numeric_feature': np.random.randn(100),
        'categorical_feature': np.random.choice(['A', 'B', 'C'], 100),
        'target': np.random.choice([0, 1], 100)
    })
    
    # Data validation
    print("Data validation...")
    is_valid = model_validator.validate_model_input(
        sample_data, 
        required_columns=['numeric_feature', 'target']
    )
    print(f"Data valid: {is_valid}")
    
    # Data processing
    from utils.helpers import data_processor
    cleaned_data = data_processor.clean_data(sample_data)
    print(f"Data shape after cleaning: {cleaned_data.shape}")
    
    # Categorical encoding
    encoded_data = data_processor.encode_categorical(cleaned_data, strategy='one_hot')
    print(f"Data shape after encoding: {encoded_data.shape}")

def demo_performance_profiling():
    """Performance profiling demo"""
    print("\n10. Performance profiling demo...")
    
    try:
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Create sample data
        X = pd.DataFrame({
            'feature1': np.random.randn(1000),
            'feature2': np.random.randn(1000),
            'feature3': np.random.randn(1000)
        })
        y = np.random.randint(0, 2, 1000)
        
        # Train model
        model.fit(X, y)
        
        # Profile inference
        profiler = performance_profiler
        profile_results = profiler.profile_model_inference(model, X, iterations=50)
        
        print("Model inference profiling:")
        for metric, value in profile_results.items():
            print(f"  {metric}: {value}")
            
        # Profile model size
        size_profile = profiler.profile_model_size(model)
        print(f"\nModel size: {size_profile['size_mb_formatted']}")
        
    except ImportError:
        print("sklearn not available, skipping performance profiling")

def demo_file_management():
    """File management demo"""
    print("\n11. File management demo...")
    
    from utils.helpers import file_manager
    
    # Create directory structure
    demo_dirs = ['demo_data', 'demo_models', 'demo_logs']
    file_manager.create_directory_structure('demo_output', demo_dirs)
    print("Directory structure created")
    
    # Create sample file
    sample_data = pd.DataFrame({
        'col1': np.random.randn(100),
        'col2': np.random.choice(['A', 'B'], 100)
    })
    
    file_path = 'demo_output/demo_data/sample.csv'
    data_saver.save_csv(sample_data, file_path)
    print(f"Sample data saved: {file_path}")
    
    # Calculate file hash
    file_hash = file_manager.calculate_file_hash(file_path)
    print(f"File hash: {file_hash}")
    
    # Directory size
    dir_size = file_manager.get_directory_size('demo_output')
    print(f"Directory size: {dir_size['total_size_mb']:.2f} MB")

def run_complete_demo():
    """To'liq demo ishga tushirish"""
    print("🚀 ML MODEL UPDATES SYSTEM DEMO")
    print("=" * 60)
    
    try:
        # 1. Model lifecycle
        system, cls_data, reg_data = demo_model_lifecycle()
        
        # 2. Monitoring
        demo_model_monitoring(system)
        
        # 3. AutoML
        demo_automl_demo(system, cls_data)
        
        # 4. Bias analysis
        demo_bias_analysis_demo(system, cls_data)
        
        # 5. Model status
        demo_model_status(system)
        
        # 6. Utilities
        demo_utility_functions()
        
        # 7. Performance profiling
        demo_performance_profiling()
        
        # 8. File management
        demo_file_management()
        
        print("\n" + "=" * 60)
        print("✅ Demo muvaffaqiyatli tugallandi!")
        print("=" * 60)
        
        # Final system overview
        final_overview = system.get_system_overview()
        print(f"\nFinal system overview:")
        print(f"- Registered models: {final_overview['registered_models_count']}")
        print(f"- Total updates: {final_overview['update_statistics']['total_updates']}")
        print(f"- System status: {final_overview['system_status']}")
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {str(e)}")
        import traceback
        traceback.print_exc()

def interactive_demo():
    """Interaktiv demo"""
    print("🎯 INTERACTIVE DEMO")
    print("=" * 40)
    
    system = MLModelUpdateSystem("interactive_config")
    
    while True:
        print("\nKerakli amalni tanlang:")
        print("1. Model initialize qilish")
        print("2. Model status ko'rish")
        print("3. Tizim overview")
        print("4. Monitoring boshlanishi")
        print("5. AutoML ishga tushirish")
        print("6. Bias analysis")
        print("7. Exit")
        
        choice = input("\nTanlovingiz (1-7): ").strip()
        
        if choice == '1':
            model_name = input("Model nomi: ").strip()
            model_type = input("Model turi (classification/regression): ").strip()
            if model_name:
                try:
                    version = system.initialize_model(model_name, model_type)
                    print(f"✅ Model initialized: {version}")
                except Exception as e:
                    print(f"❌ Xato: {str(e)}")
                    
        elif choice == '2':
            model_name = input("Model nomi: ").strip()
            if model_name:
                try:
                    status = system.get_model_status(model_name)
                    print(json.dumps(status, indent=2, default=str))
                except Exception as e:
                    print(f"❌ Xato: {str(e)}")
                    
        elif choice == '3':
            try:
                overview = system.get_system_overview()
                print(json.dumps(overview, indent=2, default=str))
            except Exception as e:
                print(f"❌ Xato: {str(e)}")
                
        elif choice == '4':
            model_name = input("Model nomi: ").strip()
            if model_name:
                try:
                    success = system.start_monitoring(model_name)
                    print(f"Monitoring {'started' if success else 'failed'}")
                except Exception as e:
                    print(f"❌ Xato: {str(e)}")
                    
        elif choice == '5':
            print("AutoML demo - placeholder")
            
        elif choice == '6':
            print("Bias analysis demo - placeholder")
            
        elif choice == '7':
            print("Sayonara!")
            break
            
        else:
            print("Noto'g'ri tanlov!")

if __name__ == "__main__":
    import json
    
    # Command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="ML Model Updates Demo")
    parser.add_argument('--mode', choices=['complete', 'interactive'], 
                       default='complete', help='Demo mode')
    
    args = parser.parse_args()
    
    if args.mode == 'complete':
        run_complete_demo()
    else:
        interactive_demo()