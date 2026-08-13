"""Helm Generator structures configurations into Helm Chart hierarchies.
"""

from typing import Dict

class HelmGenerator:
    """Drafts standard Helm Chart directories and templates."""

    def generate_chart(self, name: str, port: int) -> Dict[str, str]:
        """Returns Helm files layout."""
        name_clean = name.lower().replace("_", "-").replace(" ", "-")

        files = {}
        files["Chart.yaml"] = f"""apiVersion: v2
name: {name_clean}
description: A Helm chart for {name}
type: application
version: 0.1.0
appVersion: "1.0.0"
"""

        files["values.yaml"] = f"""# Default values for {name_clean}.
replicaCount: 2

image:
  repository: {name_clean}
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 80
  targetPort: {port}

ingress:
  enabled: false
  className: ""
  annotations: {{}}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
"""

        files["templates/deployment.yaml"] = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "chart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ include "chart.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "chart.name" . }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.service.targetPort }}
"""

        # Mock helper template
        files["templates/_helpers.tpl"] = """{{/* Expand the name of the chart. */}}
{{- define "chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Create a default fully qualified app name. */}}
{{- define "chart.fullname" -}}
{{- printf "%s" .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
"""

        return files
