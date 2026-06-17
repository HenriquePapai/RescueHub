#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f k8s/40-ingress/
kubectl -n rescuehub get ingress

echo ""
echo "Ingress aplicado. Ele aponta para o Service api-gateway."
echo "Se estiver usando kind/Codespaces, você ainda precisa ter um Ingress Controller instalado e exposto."
