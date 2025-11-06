"""
Model Versioning System
ML model versiya boshqaruvi va registry management
"""

import os
import json
import hashlib
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import pickle

# Optional sklearn import
try:
    import sklearn
    from sklearn.base import BaseEstimator
    from sklearn.linear_model import LogisticRegression, LinearRegression
except ImportError:
    sklearn = None
    BaseEstimator = None
    LogisticRegression = None
    LinearRegression = None

@dataclass
class ModelVersion:
    """Model versiya ma'lumotlari"""
    version_id: str
    model_name: str
    version: str
    framework: str
    architecture: str
    created_at: datetime
    created_by: str
    model_path: str
    metadata_path: str
    training_data_hash: str
    model_hash: str
    performance_metrics: Dict[str, float]
    status: str  # active, deprecated, archived, testing
    parent_version: Optional[str] = None
    description: str = ""
    tags: List[str] = None
    rollback_available: bool = True
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ModelMetadata:
    """Model metama'lumotlari"""
    hyperparameters: Dict[str, Any]
    training_config: Dict[str, Any]
    data_info: Dict[str, Any]
    model_architecture: Dict[str, Any]
    performance_history: List[Dict[str, Any]]
    audit_log: List[Dict[str, Any]]
    dependencies: List[str]
    deployment_info: Dict[str, Any]
    explainability_info: Dict[str, Any]
    bias_assessment: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.bias_assessment is None:
            self.bias_assessment = {}

class ModelVersionRegistry:
    """Model versiya registry"""
    
    def __init__(self, registry_path: str = "models/registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.registry_path / "registry.db"
        self.versions_index_path = self.registry_path / "versions_index.json"
        self.models_path = self.registry_path / "models"
        self.metadata_path = self.registry_path / "metadata"
        
        # Fayl strukturasini yaratish
        self.models_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self._init_database()
        self._load_versions_index()
        
    def _init_database(self):
        """Registry ma'lumotlar bazasi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                version_id TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                version TEXT NOT NULL,
                framework TEXT NOT NULL,
                architecture TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                created_by TEXT NOT NULL,
                model_path TEXT NOT NULL,
                metadata_path TEXT NOT NULL,
                training_data_hash TEXT NOT NULL,
                model_hash TEXT NOT NULL,
                performance_metrics TEXT NOT NULL,
                status TEXT NOT NULL,
                parent_version TEXT,
                description TEXT,
                tags TEXT,
                rollback_available BOOLEAN DEFAULT TRUE,
                UNIQUE(model_name, version)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id TEXT NOT NULL,
                environment TEXT NOT NULL,
                deployed_at TIMESTAMP NOT NULL,
                deployed_by TEXT NOT NULL,
                deployment_config TEXT NOT NULL,
                status TEXT NOT NULL,
                rollback_version_id TEXT,
                FOREIGN KEY (version_id) REFERENCES model_versions (version_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_ab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                model_a_version_id TEXT NOT NULL,
                model_b_version_id TEXT NOT NULL,
                traffic_split REAL NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT NOT NULL,
                results TEXT,
                FOREIGN KEY (model_a_version_id) REFERENCES model_versions (version_id),
                FOREIGN KEY (model_b_version_id) REFERENCES model_versions (version_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_versions_index(self):
        """Versiyalar indeksini yuklash"""
        if self.versions_index_path.exists():
            with open(self.versions_index_path, 'r') as f:
                self.versions_index = json.load(f)
        else:
            self.versions_index = {}
            
    def _save_versions_index(self):
        """Versiyalar indeksini saqlash"""
        with open(self.versions_index_path, 'w') as f:
            json.dump(self.versions_index, f, indent=2, default=str)
            
    def _calculate_hash(self, file_path: str) -> str:
        """Fayl hashini hisoblash"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    def register_model(self, 
                      model_name: str,
                      version: str,
                      model_path: str,
                      metadata: ModelMetadata,
                      created_by: str,
                      framework: str,
                      architecture: str,
                      description: str = "",
                      tags: List[str] = None,
                      performance_metrics: Dict[str, float] = None) -> str:
        """Modelni registry ga ro'yxatdan o'tkazish"""
        
        # Fayllarni ko'chirish
        version_id = f"{model_name}_{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dest_model_path = self.models_path / f"{version_id}.pkl"
        dest_metadata_path = self.metadata_path / f"{version_id}.json"
        
        # Model faylini ko'chirish
        shutil.copy2(model_path, dest_model_path)
        
        # Metadata ni saqlash
        with open(dest_metadata_path, 'w') as f:
            json.dump(asdict(metadata), f, indent=2, default=str)
            
        # Hash larni hisoblash
        model_hash = self._calculate_hash(str(dest_model_path))
        training_data_hash = metadata.data_info.get('data_hash', 'unknown')
        
        # Performance metrics
        if performance_metrics is None:
            performance_metrics = {}
            
        # ModelVersion obyektini yaratish
        model_version = ModelVersion(
            version_id=version_id,
            model_name=model_name,
            version=version,
            framework=framework,
            architecture=architecture,
            created_at=datetime.now(),
            created_by=created_by,
            model_path=str(dest_model_path),
            metadata_path=str(dest_metadata_path),
            training_data_hash=training_data_hash,
            model_hash=model_hash,
            performance_metrics=performance_metrics,
            status="active",
            description=description,
            tags=tags or []
        )
        
        # Ma'lumotlar bazasiga qo'shish
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_versions (
                version_id, model_name, version, framework, architecture,
                created_at, created_by, model_path, metadata_path,
                training_data_hash, model_hash, performance_metrics,
                status, description, tags, rollback_available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model_version.version_id, model_version.model_name, model_version.version,
            model_version.framework, model_version.architecture, model_version.created_at,
            model_version.created_by, model_version.model_path, model_version.metadata_path,
            model_version.training_data_hash, model_version.model_hash,
            json.dumps(model_version.performance_metrics), model_version.status,
            model_version.description, json.dumps(model_version.tags),
            model_version.rollback_available
        ))
        
        conn.commit()
        conn.close()
        
        # Indeksni yangilash
        self.versions_index[version_id] = asdict(model_version)
        self._save_versions_index()
        
        self.logger.info(f"Model registered: {version_id}")
        return version_id
        
    def get_model_version(self, version_id: str) -> Optional[ModelVersion]:
        """Model versiyasini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM model_versions WHERE version_id = ?', (version_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        # row dict ga o'tkazish
        columns = [description[0] for description in cursor.description]
        row_dict = dict(zip(columns, row))
        
        # JSON maydonlarni parse qilish
        row_dict['performance_metrics'] = json.loads(row_dict['performance_metrics'])
        row_dict['tags'] = json.loads(row_dict['tags'])
        row_dict['created_at'] = datetime.fromisoformat(row_dict['created_at'])
        
        return ModelVersion(**row_dict)
        
    def get_model_versions(self, model_name: str, status: str = None) -> List[ModelVersion]:
        """Model versiyalarini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM model_versions 
                WHERE model_name = ? AND status = ?
                ORDER BY created_at DESC
            ''', (model_name, status))
        else:
            cursor.execute('''
                SELECT * FROM model_versions 
                WHERE model_name = ?
                ORDER BY created_at DESC
            ''', (model_name,))
            
        rows = cursor.fetchall()
        conn.close()
        
        versions = []
        for row in rows:
            columns = [description[0] for description in cursor.description]
            row_dict = dict(zip(columns, row))
            
            # JSON maydonlarni parse qilish
            row_dict['performance_metrics'] = json.loads(row_dict['performance_metrics'])
            row_dict['tags'] = json.loads(row_dict['tags'])
            row_dict['created_at'] = datetime.fromisoformat(row_dict['created_at'])
            
            versions.append(ModelVersion(**row_dict))
            
        return versions
        
    def update_version_status(self, version_id: str, new_status: str, updated_by: str) -> bool:
        """Versiya holatini yangilash"""
        valid_statuses = ['active', 'deprecated', 'archived', 'testing']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE model_versions 
            SET status = ?
            WHERE version_id = ?
        ''', (new_status, version_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if updated:
            # Audit log qo'shish
            self._add_audit_log(version_id, updated_by, f"Status changed to {new_status}")
            # Indeksni yangilash
            if version_id in self.versions_index:
                self.versions_index[version_id]['status'] = new_status
                self._save_versions_index()
                
        return updated
        
    def deploy_model(self, version_id: str, environment: str, deployed_by: str, 
                    deployment_config: Dict[str, Any] = None) -> int:
        """Modelni deployment qilish"""
        if deployment_config is None:
            deployment_config = {}
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_deployments (
                version_id, environment, deployed_at, deployed_by,
                deployment_config, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (version_id, environment, datetime.now(), deployed_by,
              json.dumps(deployment_config), 'deployed'))
        
        deployment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.logger.info(f"Model deployed: {version_id} to {environment}")
        return deployment_id
        
    def create_ab_test(self, test_name: str, model_a_version_id: str, model_b_version_id: str,
                      traffic_split: float, created_by: str) -> int:
        """A/B test yaratish"""
        if not (0 < traffic_split < 1):
            raise ValueError("Traffic split must be between 0 and 1")
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_ab_tests (
                test_name, model_a_version_id, model_b_version_id,
                traffic_split, start_time, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (test_name, model_a_version_id, model_b_version_id,
              traffic_split, datetime.now(), 'running'))
        
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.logger.info(f"A/B test created: {test_name}")
        return test_id
        
    def complete_ab_test(self, test_id: int, results: Dict[str, Any]) -> bool:
        """A/B test natijalarini saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE model_ab_tests
            SET status = ?, end_time = ?, results = ?
            WHERE id = ?
        ''', ('completed', datetime.now(), json.dumps(results), test_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if updated:
            self.logger.info(f"A/B test completed: {test_id}")
            
        return updated
        
    def rollback_model(self, version_id: str, target_version_id: str, rolled_back_by: str) -> bool:
        """Modelni rollback qilish"""
        current_version = self.get_model_version(version_id)
        target_version = self.get_model_version(target_version_id)
        
        if not current_version or not target_version:
            return False
            
        if not target_version.rollback_available:
            return False
            
        # Avval current versiyani archived qilish
        if not self.update_version_status(version_id, 'archived', rolled_back_by):
            return False
            
        # Target versiyani active qilish
        if not self.update_version_status(target_version_id, 'active', rolled_back_by):
            # Rollback
            self.update_version_status(version_id, current_version.status, 'rollback')
            return False
            
        # Deployment rollback
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_deployments (
                version_id, environment, deployed_at, deployed_by,
                deployment_config, status, rollback_version_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (target_version_id, 'production', datetime.now(), rolled_back_by,
              json.dumps({'rollback_from': version_id}), 'deployed', version_id))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Model rolled back: {version_id} -> {target_version_id}")
        return True
        
    def get_deployment_history(self, version_id: str) -> List[Dict[str, Any]]:
        """Deployment tarixini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM model_deployments
            WHERE version_id = ?
            ORDER BY deployed_at DESC
        ''', (version_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        deployments = []
        columns = [description[0] for description in cursor.description]
        for row in rows:
            deployment = dict(zip(columns, row))
            deployment['deployment_config'] = json.loads(deployment['deployment_config'])
            deployment['deployed_at'] = datetime.fromisoformat(deployment['deployed_at'])
            deployments.append(deployment)
            
        return deployments
        
    def _add_audit_log(self, version_id: str, user: str, action: str):
        """Audit log qo'shish"""
        # Bu yerda audit log ni ma'lumotlar bazasiga qo'shish mumkin
        self.logger.info(f"Audit: {version_id} - {user} - {action}")
        
    def list_models(self) -> List[str]:
        """Mavjud modellarni ro'yxatini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT model_name FROM model_versions ORDER BY model_name')
        models = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return models
        
    def get_model_summary(self, model_name: str) -> Dict[str, Any]:
        """Model versiyalari xulosasi"""
        versions = self.get_model_versions(model_name)
        
        summary = {
            'model_name': model_name,
            'total_versions': len(versions),
            'active_versions': len([v for v in versions if v.status == 'active']),
            'deprecated_versions': len([v for v in versions if v.status == 'deprecated']),
            'latest_version': versions[0] if versions else None,
            'versions': [asdict(v) for v in versions]
        }
        
        return summary

class ModelRegistryManager:
    """Model registry boshqaruvchisi"""
    
    def __init__(self, registry_path: str = "models/registry"):
        self.registry = ModelVersionRegistry(registry_path)
        self.logger = logging.getLogger(__name__)
        
    def create_model(self, model_name: str, model_type: str, framework: str = "sklearn"):
        """Yangi model yaratish"""
        # Create placeholder model file
        placeholder_path = "models/placeholder.pkl"
        os.makedirs(os.path.dirname(placeholder_path), exist_ok=True)
        
        # Create a simple placeholder model
        if sklearn:
            if model_type == "classification":
                from sklearn.linear_model import LogisticRegression
                placeholder_model = LogisticRegression()
                placeholder_model.fit([[0, 0], [1, 1]], [0, 1])  # Dummy fit
            else:
                from sklearn.linear_model import LinearRegression
                placeholder_model = LinearRegression()
                placeholder_model.fit([[0, 0], [1, 1]], [0, 1])  # Dummy fit
        else:
            # Simple placeholder without sklearn
            placeholder_model = {"type": "placeholder", "model_type": model_type}
            
        # Save placeholder model
        with open(placeholder_path, 'wb') as f:
            pickle.dump(placeholder_model, f)
        
        # Default metadata yaratish
        metadata = ModelMetadata(
            hyperparameters={},
            training_config={},
            data_info={},
            model_architecture={},
            performance_history=[],
            audit_log=[],
            dependencies=[],
            deployment_info={},
            explainability_info={}
        )
        
        # Default performance metrics
        performance_metrics = {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0
        }
        
        # Modelni ro'yxatdan o'tkazish
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version = f"1.0.0_{timestamp}"
        
        version_id = self.registry.register_model(
            model_name=model_name,
            version=version,
            model_path=placeholder_path,
            metadata=metadata,
            created_by="system",
            framework=framework,
            architecture=model_type,
            description=f"Initial version of {model_name}",
            performance_metrics=performance_metrics
        )
        
        return version_id
        
    def update_model_version(self, model_name: str, new_version: str, 
                           model_path: str, performance_metrics: Dict[str, float],
                           updated_by: str, description: str = "") -> str:
        """Model versiyasini yangilash"""
        
        # Oldingi versiyani olish
        previous_versions = self.registry.get_model_versions(model_name)
        parent_version = previous_versions[0] if previous_versions else None
        
        # Metadata yaratish
        metadata = ModelMetadata(
            hyperparameters={},
            training_config={},
            data_info={},
            model_architecture={},
            performance_history=[],
            audit_log=[],
            dependencies=[],
            deployment_info={},
            explainability_info={}
        )
        
        # Modelni ro'yxatdan o'tkazish
        version_id = self.registry.register_model(
            model_name=model_name,
            version=new_version,
            model_path=model_path,
            metadata=metadata,
            created_by=updated_by,
            framework=parent_version.framework if parent_version else "sklearn",
            architecture=parent_version.architecture if parent_version else "default",
            description=description,
            parent_version=parent_version.version_id if parent_version else None,
            performance_metrics=performance_metrics
        )
        
        # Avvalgi versiyalarni deprecated qilish
        for version in previous_versions:
            if version.version_id != version_id:
                self.registry.update_version_status(version.version_id, 'deprecated', updated_by)
                
        return version_id
    
    def get_model_summary(self, model_name: str) -> Dict[str, Any]:
        """Model versiyalari xulosasi"""
        return self.registry.get_model_summary(model_name)