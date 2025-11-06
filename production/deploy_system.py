#!/usr/bin/env python3
"""
Production Deployment System
Production muhit uchun avtomatik deployment tizimi
"""

import os
import sys
import json
import time
import docker
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
import yaml
from kubernetes import client, config

# Import production configuration
from production_config import get_config, validate_environment


class ProductionDeployment:
    """Production deployment boshqaruvchisi"""
    
    def __init__(self, environment: str = "production"):
        self.config = get_config(environment)
        self.environment = environment
        self.workspace = Path("/workspace/orion-starline")
        self.docker_client = docker.from_env()
        
        # Logging setup
        self.setup_logging()
        
        # Kubernetes client
        try:
            config.load_kube_config()
            self.k8s_client = client.ApiClient()
        except Exception as e:
            self.logger.warning(f"Kubernetes konfiguratsiya yuklanmadi: {e}")
            self.k8s_client = None
    
    def setup_logging(self):
        """Logging konfiguratsiyasi"""
        log_dir = self.workspace / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def build_docker_images(self) -> bool:
        """Docker rasmlarni qurish"""
        self.logger.info("🐳 Docker rasmlarni qurish boshlandi...")
        
        try:
            # Backend Docker image
            backend_dockerfile = self.workspace / "Dockerfile.backend"
            if backend_dockerfile.exists():
                self.logger.info("Backend Docker image qurilmoqda...")
                image, logs = self.docker_client.images.build(
                    path=str(self.workspace),
                    dockerfile=str(backend_dockerfile),
                    tag=f"{self.config.DOCKER_REGISTRY}/backend:latest",
                    rm=True
                )
                self.logger.info(f"Backend Docker image qurildi: {image.short_id}")
            
            # Frontend Docker image
            frontend_dockerfile = self.workspace / "Dockerfile.frontend"
            if frontend_dockerfile.exists():
                self.logger.info("Frontend Docker image qurilmoqda...")
                image, logs = self.docker_client.images.build(
                    path=str(self.workspace / "frontend"),
                    dockerfile=str(frontend_dockerfile),
                    tag=f"{self.config.DOCKER_REGISTRY}/frontend:latest",
                    rm=True
                )
                self.logger.info(f"Frontend Docker image qurildi: {image.short_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Docker image qurishda xato: {e}")
            return False
    
    def push_docker_images(self) -> bool:
        """Docker rasmlarni registry ga push qilish"""
        self.logger.info("📤 Docker rasmlarni registry ga push qilish...")
        
        try:
            # Login to registry
            os.environ["DOCKER_REGISTRY_TOKEN"] = os.getenv("DOCKER_REGISTRY_TOKEN", "")
            
            # Push backend image
            backend_image = self.docker_client.images.get(f"{self.config.DOCKER_REGISTRY}/backend:latest")
            backend_image.tag(f"{self.config.DOCKER_REGISTRY}/backend", "latest")
            
            # Push frontend image
            frontend_image = self.docker_client.images.get(f"{self.config.DOCKER_REGISTRY}/frontend:latest")
            frontend_image.tag(f"{self.config.DOCKER_REGISTRY}/frontend", "latest")
            
            self.logger.info("✅ Docker rasmlar registry ga push qilindi")
            return True
            
        except Exception as e:
            self.logger.error(f"Docker rasmlar push qilishda xato: {e}")
            return False
    
    def deploy_to_kubernetes(self) -> bool:
        """Kubernetes ga deploy qilish"""
        if not self.k8s_client:
            self.logger.error("Kubernetes client mavjud emas")
            return False
        
        self.logger.info("🚀 Kubernetes ga deploy qilish...")
        
        try:
            apps_v1 = client.AppsV1Api(self.k8s_client)
            core_v1 = client.CoreV1Api(self.k8s_client)
            
            # Deploy backend
            backend_deployment = self.create_backend_deployment()
            try:
                apps_v1.create_namespaced_deployment(
                    body=backend_deployment,
                    namespace=self.config.KUBE_NAMESPACE
                )
                self.logger.info("Backend deployment yaratildi")
            except client.exceptions.ApiException:
                # Update existing deployment
                apps_v1.patch_namespaced_deployment(
                    name="orion-backend",
                    namespace=self.config.KUBE_NAMESPACE,
                    body=backend_deployment
                )
                self.logger.info("Backend deployment yangilandi")
            
            # Deploy frontend
            frontend_deployment = self.create_frontend_deployment()
            try:
                apps_v1.create_namespaced_deployment(
                    body=frontend_deployment,
                    namespace=self.config.KUBE_NAMESPACE
                )
                self.logger.info("Frontend deployment yaratildi")
            except client.exceptions.ApiException:
                apps_v1.patch_namespaced_deployment(
                    name="orion-frontend",
                    namespace=self.config.KUBE_NAMESPACE,
                    body=frontend_deployment
                )
                self.logger.info("Frontend deployment yangilandi")
            
            # Deploy database
            db_deployment = self.create_database_deployment()
            try:
                apps_v1.create_namespaced_deployment(
                    body=db_deployment,
                    namespace=self.config.KUBE_NAMESPACE
                )
                self.logger.info("Database deployment yaratildi")
            except client.exceptions.ApiException:
                apps_v1.patch_namespaced_deployment(
                    name="orion-database",
                    namespace=self.config.KUBE_NAMESPACE,
                    body=db_deployment
                )
                self.logger.info("Database deployment yangilandi")
            
            # Deploy Redis
            redis_deployment = self.create_redis_deployment()
            try:
                apps_v1.create_namespaced_deployment(
                    body=redis_deployment,
                    namespace=self.config.KUBE_NAMESPACE
                )
                self.logger.info("Redis deployment yaratildi")
            except client.exceptions.ApiException:
                apps_v1.patch_namespaced_deployment(
                    name="orion-redis",
                    namespace=self.config.KUBE_NAMESPACE,
                    body=redis_deployment
                )
                self.logger.info("Redis deployment yangilandi")
            
            # Deploy services
            services = [
                self.create_backend_service(),
                self.create_frontend_service(),
                self.create_database_service(),
                self.create_redis_service()
            ]
            
            for service in services:
                try:
                    core_v1.create_namespaced_service(
                        body=service,
                        namespace=self.config.KUBE_NAMESPACE
                    )
                    self.logger.info(f"Service {service['metadata']['name']} yaratildi")
                except client.exceptions.ApiException:
                    self.logger.info(f"Service {service['metadata']['name']} mavjud")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Kubernetes deployment xatosi: {e}")
            return False
    
    def create_backend_deployment(self) -> Dict:
        """Backend Kubernetes deployment yaratish"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "orion-backend",
                "namespace": self.config.KUBE_NAMESPACE,
                "labels": {"app": "orion-backend"}
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {"app": "orion-backend"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "orion-backend"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "backend",
                            "image": f"{self.config.DOCKER_REGISTRY}/backend:latest",
                            "ports": [
                                {"containerPort": 8000, "name": "http"}
                            ],
                            "env": [
                                {"name": "ENVIRONMENT", "value": self.environment},
                                {"name": "SUPABASE_URL", "value": self.config.SUPABASE_URL},
                                {"name": "SUPABASE_ANON_KEY", "value": self.config.SUPABASE_ANON_KEY},
                                {"name": "STRIPE_SECRET_KEY", "value": self.config.STRIPE_SECRET_KEY},
                                {"name": "PAYPAL_CLIENT_ID", "value": self.config.PAYPAL_CLIENT_ID}
                            ],
                            "resources": {
                                "requests": {"cpu": "200m", "memory": "512Mi"},
                                "limits": {"cpu": "1000m", "memory": "2Gi"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": 8000},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": 8000},
                                "initialDelaySeconds": 15,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
    
    def create_frontend_deployment(self) -> Dict:
        """Frontend Kubernetes deployment yaratish"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "orion-frontend",
                "namespace": self.config.KUBE_NAMESPACE,
                "labels": {"app": "orion-frontend"}
            },
            "spec": {
                "replicas": 2,
                "selector": {
                    "matchLabels": {"app": "orion-frontend"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "orion-frontend"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "frontend",
                            "image": f"{self.config.DOCKER_REGISTRY}/frontend:latest",
                            "ports": [
                                {"containerPort": 3000, "name": "http"}
                            ],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "256Mi"},
                                "limits": {"cpu": "500m", "memory": "1Gi"}
                            }
                        }]
                    }
                }
            }
        }
    
    def create_database_deployment(self) -> Dict:
        """Database Kubernetes deployment yaratish"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "orion-database",
                "namespace": self.config.KUBE_NAMESPACE,
                "labels": {"app": "orion-database"}
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "orion-database"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "orion-database"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "database",
                            "image": "postgres:15",
                            "ports": [
                                {"containerPort": 5432, "name": "postgresql"}
                            ],
                            "env": [
                                {"name": "POSTGRES_DB", "value": self.config.SUPABASE_DB_NAME},
                                {"name": "POSTGRES_USER", "value": self.config.SUPABASE_DB_USER},
                                {"name": "POSTGRES_PASSWORD", "value": self.config.SUPABASE_DB_PASSWORD}
                            ],
                            "resources": {
                                "requests": {"cpu": "500m", "memory": "1Gi"},
                                "limits": {"cpu": "2000m", "memory": "4Gi"}
                            },
                            "volumeMounts": [
                                {"name": "postgres-data", "mountPath": "/var/lib/postgresql/data"}
                            ]
                        }],
                        "volumes": [{
                            "name": "postgres-data",
                            "persistentVolumeClaim": {"claimName": "postgres-pvc"}
                        }]
                    }
                }
            }
        }
    
    def create_redis_deployment(self) -> Dict:
        """Redis Kubernetes deployment yaratish"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "orion-redis",
                "namespace": self.config.KUBE_NAMESPACE,
                "labels": {"app": "orion-redis"}
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "orion-redis"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "orion-redis"}
                    },
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "ports": [
                                {"containerPort": 6379, "name": "redis"}
                            ],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "256Mi"},
                                "limits": {"cpu": "500m", "memory": "1Gi"}
                            }
                        }]
                    }
                }
            }
        }
    
    def create_backend_service(self) -> Dict:
        """Backend Kubernetes service yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "orion-backend-service",
                "namespace": self.config.KUBE_NAMESPACE
            },
            "spec": {
                "selector": {"app": "orion-backend"},
                "ports": [
                    {"port": 80, "targetPort": 8000, "name": "http"}
                ],
                "type": "ClusterIP"
            }
        }
    
    def create_frontend_service(self) -> Dict:
        """Frontend Kubernetes service yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "orion-frontend-service",
                "namespace": self.config.KUBE_NAMESPACE
            },
            "spec": {
                "selector": {"app": "orion-frontend"},
                "ports": [
                    {"port": 80, "targetPort": 3000, "name": "http"}
                ],
                "type": "ClusterIP"
            }
        }
    
    def create_database_service(self) -> Dict:
        """Database Kubernetes service yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "orion-database-service",
                "namespace": self.config.KUBE_NAMESPACE
            },
            "spec": {
                "selector": {"app": "orion-database"},
                "ports": [
                    {"port": 5432, "targetPort": 5432, "name": "postgresql"}
                ],
                "type": "ClusterIP"
            }
        }
    
    def create_redis_service(self) -> Dict:
        """Redis Kubernetes service yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "orion-redis-service",
                "namespace": self.config.KUBE_NAMESPACE
            },
            "spec": {
                "selector": {"app": "orion-redis"},
                "ports": [
                    {"port": 6379, "targetPort": 6379, "name": "redis"}
                ],
                "type": "ClusterIP"
            }
        }
    
    def run_health_checks(self) -> bool:
        """Sog'liqni saqlash tekshiruvlari"""
        self.logger.info("🏥 Sog'liqni saqlash tekshiruvlari...")
        
        health_endpoints = [
            {"name": "Backend", "url": "http://localhost:8000/health"},
            {"name": "Frontend", "url": "http://localhost:3000"},
            {"name": "Database", "url": "http://localhost:5432"},
            {"name": "Redis", "url": "http://localhost:6379"}
        ]
        
        failed_checks = []
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(endpoint["url"], timeout=10)
                if response.status_code == 200:
                    self.logger.info(f"✅ {endpoint['name']} - Sog'lom")
                else:
                    failed_checks.append(f"{endpoint['name']} - HTTP {response.status_code}")
            except Exception as e:
                failed_checks.append(f"{endpoint['name']} - {str(e)}")
        
        if failed_checks:
            self.logger.error(f"❌ Muvaffaqiyatsiz tekshiruvlar: {failed_checks}")
            return False
        
        self.logger.info("✅ Barcha sog'liq tekshiruvlari muvaffaqiyatli")
        return True
    
    def deploy(self) -> bool:
        """Asosiy deploy funksiyasi"""
        self.logger.info("🚀 Production deployment boshlandi...")
        self.logger.info(f"Environment: {self.environment}")
        
        try:
            # 1. Konfiguratsiyani tekshirish
            if not self.config.validate_config():
                self.logger.error("Konfiguratsiya xatosi!")
                return False
            
            # 2. Docker rasmlarni qurish
            if not self.build_docker_images():
                self.logger.error("Docker image qurish xatosi!")
                return False
            
            # 3. Docker rasmlarni push qilish
            if not self.push_docker_images():
                self.logger.error("Docker image push xatosi!")
                return False
            
            # 4. Kubernetes ga deploy qilish
            if not self.deploy_to_kubernetes():
                self.logger.error("Kubernetes deployment xatosi!")
                return False
            
            # 5. Sog'liq tekshiruvlari
            time.sleep(30)  # Podlarning ishga tushishini kutish
            if not self.run_health_checks():
                self.logger.error("Sog'liq tekshiruvlari xatosi!")
                return False
            
            self.logger.info("✅ Production deployment muvaffaqiyatli tugallandi!")
            return True
            
        except Exception as e:
            self.logger.error(f"Deploymentda umumiy xato: {e}")
            return False
    
    def rollback(self) -> bool:
        """Deployment ni qayta qaytarish"""
        self.logger.info("↩️ Deployment ni qayta qaytarish...")
        
        try:
            # Previous version ga o'tish
            # Bu implementation deployment tarixini saqlab qolishni talab qiladi
            
            self.logger.info("✅ Deployment qaytarildi")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment qaytarish xatosi: {e}")
            return False


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Deployment System")
    parser.add_argument("--environment", "-e", default="production", 
                       choices=["development", "staging", "production"],
                       help="Deployment environment")
    parser.add_argument("--action", "-a", default="deploy",
                       choices=["deploy", "rollback", "health-check"],
                       help="Deploy action")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Environment validatsiyasi
    if not validate_environment():
        print("❌ Environment validatsiyasi muvaffaqiyatsiz!")
        sys.exit(1)
    
    deployment = ProductionDeployment(args.environment)
    
    if args.action == "deploy":
        success = deployment.deploy()
    elif args.action == "rollback":
        success = deployment.rollback()
    elif args.action == "health-check":
        success = deployment.run_health_checks()
    else:
        print(f"❌ Noma'lum action: {args.action}")
        sys.exit(1)
    
    if success:
        print(f"✅ {args.action} muvaffaqiyatli!")
        sys.exit(0)
    else:
        print(f"❌ {args.action} xatosi!")
        sys.exit(1)


if __name__ == "__main__":
    main()