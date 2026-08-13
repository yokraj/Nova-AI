"""Kubernetes Generator drafts native Deployment, Service, Secret, Ingress, and HPA manifests.
"""

from typing import Dict, Any, List

class KubernetesGenerator:
    """Generates standard Kubernetes YAML configurations for application deployment."""

    def generate_manifests(self, name: str, port: int, env_vars: List[str]) -> Dict[str, str]:
        """Returns map of manifest filenames to YAML content."""
        name_clean = name.lower().replace("_", "-").replace(" ", "-")
        manifests = {}

        # 1. ConfigMap
        cm_data = "\n".join([f"  {var}: \"placeholder_value\"" for var in env_vars])
        manifests["configmap.yaml"] = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {name_clean}-config
data:
{cm_data}
"""

        # 2. Secrets
        sec_data = "\n".join([f"  {var}: \"PLACEHOLDER_BASE64\"" for var in env_vars if "key" in var.lower() or "secret" in var.lower() or "password" in var.lower()])
        if not sec_data:
            sec_data = "  DB_PASSWORD: \"PLACEHOLDER_BASE64\""
        manifests["secrets.yaml"] = f"""apiVersion: v1
kind: Secret
metadata:
  name: {name_clean}-secrets
type: Opaque
data:
{sec_data}
"""

        # 3. Deployment
        manifests["deployment.yaml"] = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name_clean}
  labels:
    app: {name_clean}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {name_clean}
  template:
    metadata:
      labels:
        app: {name_clean}
    spec:
      containers:
      - name: app
        image: {name_clean}:latest
        ports:
        - containerPort: {port}
        envFrom:
        - configMapRef:
            name: {name_clean}-config
        - secretRef:
            name: {name_clean}-secrets
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 5
          periodSeconds: 10
"""

        # 4. Service
        manifests["service.yaml"] = f"""apiVersion: v1
kind: Service
metadata:
  name: {name_clean}
spec:
  selector:
    app: {name_clean}
  ports:
    - protocol: TCP
      port: 80
      targetPort: {port}
  type: ClusterIP
"""

        # 5. Ingress
        manifests["ingress.yaml"] = f"""apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {name_clean}-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {name_clean}
            port:
              number: 80
"""

        # 6. HPA
        manifests["hpa.yaml"] = f"""apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {name_clean}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {name_clean}
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
"""

        return manifests
