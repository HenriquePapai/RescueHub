#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-rescuehub}"

GENERATED_DIR=".local/kind"
ENCRYPTION_CONFIG="${GENERATED_DIR}/encryption-config.yaml"
KIND_CONFIG="${GENERATED_DIR}/kind-secure-cluster.yaml"

mkdir -p "${GENERATED_DIR}"

if [[ ! -f "${ENCRYPTION_CONFIG}" ]]; then
  ENCRYPTION_KEY="$(head -c 32 /dev/urandom | base64)"

  cat > "${ENCRYPTION_CONFIG}" <<EOF
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: "${ENCRYPTION_KEY}"
      - identity: {}
EOF

  echo "Arquivo de criptografia criado em: ${ENCRYPTION_CONFIG}"
else
  echo "Usando arquivo de criptografia existente: ${ENCRYPTION_CONFIG}"
fi

ENCRYPTION_CONFIG_ABS="$(realpath "${ENCRYPTION_CONFIG}")"

cat > "${KIND_CONFIG}" <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraMounts:
      - hostPath: ${ENCRYPTION_CONFIG_ABS}
        containerPath: /etc/kubernetes/encryption-config.yaml
        readOnly: true
kubeadmConfigPatches:
  - |
    apiVersion: kubeadm.k8s.io/v1beta4
    kind: ClusterConfiguration
    apiServer:
      extraArgs:
        - name: encryption-provider-config
          value: /etc/kubernetes/encryption-config.yaml
      extraVolumes:
        - name: encryption-config
          hostPath: /etc/kubernetes/encryption-config.yaml
          mountPath: /etc/kubernetes/encryption-config.yaml
          readOnly: true
          pathType: File
EOF

echo "Arquivo kind gerado em: ${KIND_CONFIG}"

if kind get clusters | grep -qx "${CLUSTER_NAME}"; then
  echo "Removendo cluster kind existente: ${CLUSTER_NAME}"
  kind delete cluster --name "${CLUSTER_NAME}"
fi

echo "Criando cluster kind seguro: ${CLUSTER_NAME}"
kind create cluster --name "${CLUSTER_NAME}" --config "${KIND_CONFIG}"

echo ""
echo "Cluster criado com encryption-provider-config habilitado."
echo ""
kubectl config current-context
kubectl get nodes
