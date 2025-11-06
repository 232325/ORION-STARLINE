"""
Orion Starline Kubernetes Konfiguratsiyasi
==========================================

Bu fayl Kubernetes orqali kontainerizatsiya va orchestration
uchun zarur konfiguratsiyalarni o'z ichiga oladi.
"""

import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class DeploymentStrategy(Enum):
    """Joylashtirish strategiyasi"""
    ROLLING_UPDATE = "RollingUpdate"
    RECREATE = "Recreate"
    BLUE_GREEN = "BlueGreen"
    CANARY = "Canary"


@dataclass
class ResourceLimits:
    """Resurs limitlari"""
    cpu: str = "500m"
    memory: str = "512Mi"
    ephemeral_storage: str = "1Gi"


@dataclass
class ResourceRequests:
    """Resurs so'rovlari"""
    cpu: str = "100m"
    memory: str = "128Mi"
    ephemeral_storage: str = "100Mi"


@dataclass
class ContainerConfig:
    """Konteyner konfiguratsiyasi"""
    name: str
    image: str
    ports: List[int] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    volume_mounts: List[Dict[str, str]] = field(default_factory=list)
    health_check: Optional[Dict[str, Any]] = None
    resources: ResourceLimits = field(default_factory=ResourceLimits)
    security_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VolumeConfig:
    """Volume konfiguratsiyasi"""
    name: str
    size: str
    storage_class: str = "ssd"
    access_modes: List[str] = field(default_factory=lambda: ["ReadWriteOnce"])


@dataclass
class ScalingConfig:
    """Masshtab konfiguratsiyasi"""
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    scale_down_stabilization_window: int = 300  # 5 daqiqa
    scale_up_stabilization_window: int = 0


class KubernetesManifestGenerator:
    """Kubernetes manifestlarini yaratish uchun generator"""
    
    def __init__(self, namespace: str = "orion-starline"):
        self.namespace = namespace
        self.manifests: List[Dict[str, Any]] = []
    
    def generate_namespace(self) -> Dict[str, Any]:
        """Namespace yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "app": "orion-starline",
                    "version": "v1.0"
                }
            }
        }
    
    def generate_configmap(self, name: str, data: Dict[str, str]) -> Dict[str, Any]:
        """ConfigMap yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline"
                }
            },
            "data": data
        }
    
    def generate_secret(self, name: str, secret_data: Dict[str, str]) -> Dict[str, Any]:
        """Secret yaratish"""
        import base64
        
        encoded_data = {}
        for key, value in secret_data.items():
            encoded_data[key] = base64.b64encode(value.encode()).decode()
        
        return {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline"
                }
            },
            "type": "Opaque",
            "data": encoded_data
        }
    
    def generate_pvc(self, volume_config: VolumeConfig) -> Dict[str, Any]:
        """PersistentVolumeClaim yaratish"""
        return {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": volume_config.name,
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline"
                }
            },
            "spec": {
                "accessModes": volume_config.access_modes,
                "storageClassName": volume_config.storage_class,
                "resources": {
                    "requests": {
                        "storage": volume_config.size
                    }
                }
            }
        }
    
    def generate_deployment(
        self, 
        name: str, 
        container_config: ContainerConfig,
        scaling_config: ScalingConfig,
        strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE
    ) -> Dict[str, Any]:
        """Deployment yaratish"""
        
        containers = [{
            "name": container_config.name,
            "image": container_config.image,
            "ports": [{"containerPort": port} for port in container_config.ports],
            "env": [{"name": k, "value": v} for k, v in container_config.env_vars.items()],
            "volumeMounts": container_config.volume_mounts,
            "resources": {
                "requests": {
                    "cpu": "100m",
                    "memory": "128Mi"
                },
                "limits": {
                    "cpu": container_config.resources.cpu,
                    "memory": container_config.resources.memory
                }
            },
            "livenessProbe": container_config.health_check or {
                "httpGet": {
                    "path": "/health",
                    "port": container_config.ports[0] if container_config.ports else 8080
                },
                "initialDelaySeconds": 30,
                "periodSeconds": 10
            },
            "readinessProbe": {
                "httpGet": {
                    "path": "/ready",
                    "port": container_config.ports[0] if container_config.ports else 8080
                },
                "initialDelaySeconds": 5,
                "periodSeconds": 5
            }
        }]
        
        pod_spec = {
            "containers": containers,
            "securityContext": {
                "runAsNonRoot": True,
                "runAsUser": 1000,
                "fsGroup": 2000
            },
            "restartPolicy": "Always"
        }
        
        if container_config.volume_mounts:
            pod_spec["volumes"] = [{"name": vol["name"], "persistentVolumeClaim": {"claimName": vol["name"]}} for vol in container_config.volume_mounts]
        
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline",
                    "component": name
                }
            },
            "spec": {
                "replicas": scaling_config.min_replicas,
                "selector": {
                    "matchLabels": {
                        "app": "orion-starline",
                        "component": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "orion-starline",
                            "component": name
                        }
                    },
                    "spec": pod_spec
                },
                "strategy": {
                    "type": strategy.value,
                    "rollingUpdate": {
                        "maxSurge": "25%",
                        "maxUnavailable": "25%"
                    } if strategy == DeploymentStrategy.ROLLING_UPDATE else {}
                }
            }
        }
        
        return deployment
    
    def generate_service(
        self, 
        name: str, 
        ports: List[Dict[str, int]], 
        service_type: str = "ClusterIP"
    ) -> Dict[str, Any]:
        """Service yaratish"""
        
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline"
                }
            },
            "spec": {
                "type": service_type,
                "selector": {
                    "app": "orion-starline",
                    "component": name.replace("-service", "")
                },
                "ports": ports
            }
        }
    
    def generate_hpa(
        self, 
        name: str, 
        scaling_config: ScalingConfig
    ) -> Dict[str, Any]:
        """HorizontalPodAutoscaler yaratish"""
        
        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{name}-hpa",
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline"
                }
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": name
                },
                "minReplicas": scaling_config.min_replicas,
                "maxReplicas": scaling_config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": scaling_config.target_cpu_utilization
                            }
                        }
                    },
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "memory",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": scaling_config.target_memory_utilization
                            }
                        }
                    }
                ],
                "behavior": {
                    "scaleDown": {
                        "stabilizationWindowSeconds": scaling_config.scale_down_stabilization_window
                    },
                    "scaleUp": {
                        "stabilizationWindowSeconds": scaling_config.scale_up_stabilization_window
                    }
                }
            }
        }
    
    def generate_ingress(
        self, 
        name: str, 
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ingress yaratish"""
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": "orion-starline"
                },
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
                    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true"
                }
            },
            "spec": {
                "tls": [
                    {
                        "hosts": ["orion-starline.example.com"],
                        "secretName": "orion-starline-tls"
                    }
                ],
                "rules": rules
            }
        }


class OrionStarlineK8sGenerator:
    """Orion Starline uchun Kubernetes konfiguratsiyasini yaratish"""
    
    def __init__(self):
        self.generator = KubernetesManifestGenerator()
    
    def generate_auth_service_k8s(self) -> Dict[str, Any]:
        """Auth service uchun Kubernetes manifest"""
        
        container_config = ContainerConfig(
            name="auth-service",
            image="orion-starline/auth-service:latest",
            ports=[8001],
            env_vars={
                "JWT_SECRET": "from-secret",
                "DATABASE_URL": "postgresql://user:pass@postgres:5432/auth_db",
                "REDIS_URL": "redis://redis:6379"
            },
            resources=ResourceLimits(cpu="500m", memory="512Mi"),
            health_check={
                "httpGet": {"path": "/health", "port": 8001},
                "initialDelaySeconds": 30,
                "periodSeconds": 10
            }
        )
        
        scaling_config = ScalingConfig(
            min_replicas=3,
            max_replicas=10,
            target_cpu_utilization=60
        )
        
        deployment = self.generator.generate_deployment(
            "auth-service", 
            container_config, 
            scaling_config
        )
        
        service = self.generator.generate_service(
            "auth-service",
            [{"port": 80, "targetPort": 8001, "name": "http"}]
        )
        
        hpa = self.generator.generate_hpa("auth-service", scaling_config)
        
        return {
            "deployment": deployment,
            "service": service,
            "hpa": hpa
        }
    
    def generate_trading_service_k8s(self) -> Dict[str, Any]:
        """Trading service uchun Kubernetes manifest"""
        
        container_config = ContainerConfig(
            name="trading-service",
            image="orion-starline/trading-service:latest",
            ports=[8002],
            env_vars={
                "MARKET_DATA_API": "http://market-data-service:8003",
                "REDIS_URL": "redis://redis:6379",
                "DATABASE_URL": "postgresql://user:pass@postgres:5432/trading_db"
            },
            resources=ResourceLimits(cpu="1", memory="1Gi"),
            health_check={
                "httpGet": {"path": "/health", "port": 8002},
                "initialDelaySeconds": 45,
                "periodSeconds": 10
            }
        )
        
        scaling_config = ScalingConfig(
            min_replicas=5,
            max_replicas=20,
            target_cpu_utilization=70
        )
        
        deployment = self.generator.generate_deployment(
            "trading-service", 
            container_config, 
            scaling_config
        )
        
        service = self.generator.generate_service(
            "trading-service",
            [{"port": 80, "targetPort": 8002, "name": "http"}]
        )
        
        hpa = self.generator.generate_hpa("trading-service", scaling_config)
        
        return {
            "deployment": deployment,
            "service": service,
            "hpa": hpa
        }
    
    def generate_market_data_service_k8s(self) -> Dict[str, Any]:
        """Market Data service uchun Kubernetes manifest"""
        
        container_config = ContainerConfig(
            name="market-data-service",
            image="orion-starline/market-data-service:latest",
            ports=[8003],
            env_vars={
                "MARKET_DATA_PROVIDER": "external-api",
                "REDIS_CACHE_TTL": "300",
                "DATABASE_URL": "postgresql://user:pass@postgres:5432/market_data_db"
            },
            resources=ResourceLimits(cpu="500m", memory="1Gi"),
            health_check={
                "httpGet": {"path": "/health", "port": 8003},
                "initialDelaySeconds": 30,
                "periodSeconds": 15
            }
        )
        
        scaling_config = ScalingConfig(
            min_replicas=2,
            max_replicas=8,
            target_cpu_utilization=65
        )
        
        deployment = self.generator.generate_deployment(
            "market-data-service", 
            container_config, 
            scaling_config
        )
        
        service = self.generator.generate_service(
            "market-data-service",
            [{"port": 80, "targetPort": 8003, "name": "http"}]
        )
        
        hpa = self.generator.generate_hpa("market-data-service", scaling_config)
        
        return {
            "deployment": deployment,
            "service": service,
            "hpa": hpa
        }
    
    def generate_database_k8s(self) -> Dict[str, Any]:
        """Database service uchun Kubernetes manifest"""
        
        # PostgreSQL Deployment
        postgres_container = ContainerConfig(
            name="postgres",
            image="postgres:15-alpine",
            ports=[5432],
            env_vars={
                "POSTGRES_DB": "orion_starline",
                "POSTGRES_USER": "orion_user",
                "POSTGRES_PASSWORD": "secure_password"
            },
            resources=ResourceLimits(cpu="2", memory="4Gi"),
            volume_mounts=[{"name": "postgres-storage", "mountPath": "/var/lib/postgresql/data"}]
        )
        
        postgres_volume = VolumeConfig(
            name="postgres-storage",
            size="100Gi",
            storage_class="ssd"
        )
        
        postgres_deployment = self.generator.generate_deployment(
            "postgres",
            postgres_container,
            ScalingConfig(min_replicas=1, max_replicas=1)
        )
        
        postgres_service = self.generator.generate_service(
            "postgres",
            [{"port": 5432, "targetPort": 5432, "name": "postgres"}]
        )
        
        postgres_pvc = self.generator.generate_pvc(postgres_volume)
        
        # Redis Deployment
        redis_container = ContainerConfig(
            name="redis",
            image="redis:7-alpine",
            ports=[6379],
            env_vars={},
            resources=ResourceLimits(cpu="500m", memory="1Gi"),
            health_check={
                "exec": {"command": ["redis-cli", "ping"]},
                "initialDelaySeconds": 10,
                "periodSeconds": 5
            }
        )
        
        redis_volume = VolumeConfig(
            name="redis-storage",
            size="10Gi",
            storage_class="fast-ssd"
        )
        
        redis_deployment = self.generator.generate_deployment(
            "redis",
            redis_container,
            ScalingConfig(min_replicas=1, max_replicas=1)
        )
        
        redis_service = self.generator.generate_service(
            "redis",
            [{"port": 6379, "targetPort": 6379, "name": "redis"}]
        )
        
        redis_pvc = self.generator.generate_pvc(redis_volume)
        
        return {
            "postgres": {
                "deployment": postgres_deployment,
                "service": postgres_service,
                "pvc": postgres_pvc
            },
            "redis": {
                "deployment": redis_deployment,
                "service": redis_service,
                "pvc": redis_pvc
            }
        }
    
    def generate_ingress_k8s(self) -> Dict[str, Any]:
        """Ingress konfiguratsiyasi"""
        
        rules = [
            {
                "host": "orion-starline.example.com",
                "http": {
                    "paths": [
                        {
                            "path": "/api/auth",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "auth-service",
                                    "port": {"number": 80}
                                }
                            }
                        },
                        {
                            "path": "/api/trading",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "trading-service",
                                    "port": {"number": 80}
                                }
                            }
                        },
                        {
                            "path": "/api/market-data",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": "market-data-service",
                                    "port": {"number": 80}
                                }
                            }
                        }
                    ]
                }
            }
        ]
        
        return self.generator.generate_ingress("orion-starline-ingress", rules)
    
    def generate_configmap_k8s(self) -> Dict[str, Any]:
        """ConfigMap yaratish"""
        
        config_data = {
            "LOG_LEVEL": "info",
            "METRICS_ENABLED": "true",
            "TRACING_ENABLED": "true",
            "RATE_LIMIT": "1000",
            "CACHE_TTL": "300",
            "HEALTH_CHECK_INTERVAL": "30"
        }
        
        return self.generator.generate_configmap("orion-starline-config", config_data)
    
    def generate_secrets_k8s(self) -> Dict[str, Any]:
        """Secrets yaratish"""
        
        secret_data = {
            "jwt-secret": "your-jwt-secret-key-here",
            "database-password": "secure-db-password",
            "redis-password": "secure-redis-password",
            "api-keys": "external-api-keys-json"
        }
        
        return self.generator.generate_secret("orion-starline-secrets", secret_data)
    
    def generate_full_k8s_manifest(self) -> str:
        """To'liq Kubernetes manifestini yaratish"""
        
        manifests = []
        
        # Namespace
        manifests.append(self.generator.generate_namespace())
        
        # ConfigMap
        manifests.append(self.generator.generate_configmap_k8s())
        
        # Secrets
        manifests.append(self.generator.generate_secrets_k8s())
        
        # Database
        db_configs = self.generate_database_k8s()
        for component in ["postgres", "redis"]:
            manifests.append(db_configs[component]["pvc"])
            manifests.append(db_configs[component]["deployment"])
            manifests.append(db_configs[component]["service"])
        
        # Services
        auth_k8s = self.generate_auth_service_k8s()
        trading_k8s = self.generate_trading_service_k8s()
        market_data_k8s = self.generate_market_data_service_k8s()
        
        for service_config in [auth_k8s, trading_k8s, market_data_k8s]:
            manifests.append(service_config["deployment"])
            manifests.append(service_config["service"])
            manifests.append(service_config["hpa"])
        
        # Ingress
        manifests.append(self.generate_ingress_k8s())
        
        return yaml.dump_all(manifests, default_flow_style=False, sort_keys=False)


# Monitoring va observability
class MonitoringK8sConfig:
    """Monitoring uchun Kubernetes konfiguratsiyasi"""
    
    @staticmethod
    def generate_prometheus_config() -> str:
        """Prometheus konfiguratsiyasi"""
        prometheus_config = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: orion-starline
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    scrape_configs:
      - job_name: 'orion-starline-services'
        kubernetes_sd_configs:
          - role: endpoints
            namespaces:
              names:
                - orion-starline
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
"""
        return prometheus_config
    
    @staticmethod
    def generate_grafana_dashboard_config() -> str:
        """Grafana dashboard konfiguratsiyasi"""
        return """
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: orion-starline
data:
  orion-starline-overview.json: |
    {
      "dashboard": {
        "id": null,
        "title": "Orion Starline Overview",
        "tags": ["orion-starline", "trading"],
        "timezone": "browser",
        "panels": [
          {
            "id": 1,
            "title": "Service Health",
            "type": "stat",
            "targets": [
              {
                "expr": "up{job=\"orion-starline-services\"}",
                "legendFormat": "{{instance}}"
              }
            ]
          },
          {
            "id": 2,
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total{job=\"orion-starline-services\"}[5m])",
                "legendFormat": "{{service}}"
              }
            ]
          }
        ]
      }
    }
"""


if __name__ == "__main__":
    # Demo - Kubernetes manifestlarini yaratish
    print("🚀 Orion Starline Kubernetes Konfiguratsiyasi")
    print("=" * 50)
    
    generator = OrionStarlineK8sGenerator()
    
    # To'liq manifest yaratish
    full_manifest = generator.generate_full_k8s_manifest()
    
    print("✅ To'liq Kubernetes manifest yaratildi!")
    print(f"📄 Manifest uzunligi: {len(full_manifest)} belgi")
    
    # Faylga saqlash
    with open("/workspace/orion-starline/infrastructure/kubernetes-manifest.yaml", "w") as f:
        f.write(full_manifest)
    
    print("💾 Manifest faylga saqlandi: kubernetes-manifest.yaml")
    
    # Monitoring konfiguratsiyasini yaratish
    monitoring = MonitoringK8sConfig()
    prometheus_config = monitoring.generate_prometheus_config()
    
    with open("/workspace/orion-starline/infrastructure/prometheus-config.yaml", "w") as f:
        f.write(prometheus_config)
    
    print("📊 Prometheus konfiguratsiyasi yaratildi!")
    print("🎉 Demo tugallandi!")