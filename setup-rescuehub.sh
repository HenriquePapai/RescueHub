#!/bin/bash

set -e  # Para o script se algum comando falhar

rm -rf ./kind
curl -Lo kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x kind
sudo mv kind /usr/local/bin/kind

# Cria o cluster Kind com as configurações do projeto
./scripts/create-secure-kind-cluster.sh

# Gera a imagem Docker do frontend e backend
docker build -t rescuehub-web:local -f Dockerfile.k8s .

# Gera a imagem Docker do gateway
docker build -t rescuehub-gateway:local -f Dockerfile.gateway.k8s .

# Importa a imagem web para dentro do cluster
kind load docker-image rescuehub-web:local --name rescuehub

# Importa a imagem gateway para dentro do cluster
kind load docker-image rescuehub-gateway:local --name rescuehub

# Cria namespace, deployments, services, secrets etc.
bash apply-local.sh

# Expõe o gateway localmente na porta 8000
kubectl -n rescuehub port-forward service/api-gateway 8000:8000
