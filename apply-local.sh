#!/usr/bin/env bash
set -euo pipefail

kubectl apply -f k8s/00-config/
kubectl apply -f k8s/10-database/

kubectl -n rescuehub rollout status statefulset/postgres --timeout=180s

# Job é imutável. Remove o anterior para permitir reexecução segura.
kubectl -n rescuehub delete job django-migrate --ignore-not-found=true
kubectl apply -f k8s/30-jobs/
kubectl -n rescuehub wait --for=condition=complete job/django-migrate --timeout=180s

kubectl apply -f k8s/20-application/
kubectl -n rescuehub rollout status deployment/rescuehub-web --timeout=180s

kubectl apply -f k8s/25-gateway/
kubectl -n rescuehub rollout status deployment/api-gateway --timeout=180s

echo ""
echo "Aplicação pronta com API Gateway. Teste com:"
echo "kubectl -n rescuehub port-forward service/api-gateway 8000:8000"
echo "Depois acesse: http://localhost:8000"
echo ""
echo "Para depurar o Django diretamente, use:"
echo "kubectl -n rescuehub port-forward service/rescuehub-web 8001:8000"
