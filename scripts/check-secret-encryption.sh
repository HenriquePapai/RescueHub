#!/usr/bin/env bash
set -euo pipefail

TEST_NAMESPACE="encryption-test"
TEST_SECRET="secret1"

echo "Criando namespace e Secret de teste..."

kubectl create namespace "${TEST_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

kubectl -n "${TEST_NAMESPACE}" delete secret "${TEST_SECRET}" --ignore-not-found=true

kubectl -n "${TEST_NAMESPACE}" create secret generic "${TEST_SECRET}" \
  --from-literal=mykey=mydata

ETCD_POD="$(kubectl -n kube-system get pods -l component=etcd -o jsonpath='{.items[0].metadata.name}')"

echo "Pod etcd detectado: ${ETCD_POD}"
echo "Consultando o Secret diretamente no etcd..."

TMP_FILE="$(mktemp)"

kubectl -n kube-system exec "${ETCD_POD}" -- etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get "/registry/secrets/${TEST_NAMESPACE}/${TEST_SECRET}" > "${TMP_FILE}"

if strings "${TMP_FILE}" | grep -q "k8s:enc:aescbc:v1:key1"; then
  echo ""
  echo "OK: Secret encontrado no etcd com prefixo de criptografia aescbc."
else
  echo ""
  echo "ERRO: Não encontrei o prefixo de criptografia no etcd."
  echo "Verifique se o cluster foi criado com scripts/create-secure-kind-cluster.sh."
  echo ""
  echo "Trecho encontrado no etcd:"
  strings "${TMP_FILE}" | head -40
  rm -f "${TMP_FILE}"
  exit 1
fi

rm -f "${TMP_FILE}"

echo ""
echo "Conferindo se a API do Kubernetes ainda consegue ler o Secret normalmente:"
kubectl -n "${TEST_NAMESPACE}" get secret "${TEST_SECRET}" -o yaml