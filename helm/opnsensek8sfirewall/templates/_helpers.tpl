{{/*
Expand the name of the chart.
*/}}
{{- define "opnsensek8sfirewall.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "opnsensek8sfirewall.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "opnsensek8sfirewall.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "opnsensek8sfirewall.labels" -}}
helm.sh/chart: {{ include "opnsensek8sfirewall.chart" . }}
{{ include "opnsensek8sfirewall.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "opnsensek8sfirewall.selectorLabels" -}}
app.kubernetes.io/name: {{ include "opnsensek8sfirewall.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "opnsensek8sfirewall.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "opnsensek8sfirewall.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
OPNSense API key secret name
*/}}
{{- define "opnsensek8sfirewall.opnsenseApiKey" -}}
{{- if .Values.config.opnsense.apiKey.existingSecret }}
{{- .Values.config.opnsense.apiKey.existingSecret }}
{{- else }}
{{- printf "%s-%s" (include "opnsensek8sfirewall.fullname" .) "opnsense" }}
{{- end }}
{{- end }}

{{/*
OPNSense API secret secret name
*/}}
{{- define "opnsensek8sfirewall.opnsenseApiSecret" -}}
{{- if .Values.config.opnsense.apiSecret.existingSecret }}
{{- .Values.config.opnsense.apiSecret.existingSecret }}
{{- else }}
{{- printf "%s-%s" (include "opnsensek8sfirewall.fullname" .) "opnsense" }}
{{- end }}
{{- end }}
