# RescueHub com API Gateway próprio em Django

Esta versão adiciona um **API Gateway próprio**, também em Django, separado da aplicação principal.

## Arquitetura

```text
Navegador
   |
   v
Ingress Controller
   |
   v
Ingress rescuehub-ingress
   |
   v
Service api-gateway
   |
   v
Pod API Gateway Django
   |
   v
Service rescuehub-web
   |
   v
Pod Django RescueHub
   |
   v
Service postgres
   |
   v
Pod Postgres
```

## O que foi adicionado

```text
gateway/                         # Novo projeto Django usado como API Gateway
Dockerfile.gateway.k8s           # Imagem Docker do Gateway
k8s/25-gateway/                  # Deployment, Service e ConfigMap do Gateway
k8s/40-ingress/40-django-ingress.yaml  # Ingress apontando para api-gateway
apply-ingress.sh                 # Aplica a regra de Ingress
```

## O que foi alterado

### `app/rescuehub/settings.py`

O `settings.py` da aplicação principal foi ajustado para ler estas configurações por variável de ambiente:

```text
DEBUG
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
```

Também foram adicionados:

```python
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

Isso permite que o Django principal funcione corretamente atrás do API Gateway e do Ingress.

### `k8s/40-ingress/40-django-ingress.yaml`

Antes, o Ingress apontava diretamente para:

```text
rescuehub-web
```

Agora ele aponta para:

```text
api-gateway
```

Assim o tráfego externo passa pelo Gateway antes de chegar ao Django principal.

## Como rodar com kind no Codespaces

### 1. Criar o cluster, caso ainda não exista

```bash
kind create cluster --name rescuehub
kubectl get nodes
```

### 2. Buildar as duas imagens

```bash
docker build -t rescuehub-web:local -f Dockerfile.k8s .
docker build -t rescuehub-gateway:local -f Dockerfile.gateway.k8s .
```

### 3. Carregar as imagens no kind

```bash
kind load docker-image rescuehub-web:local --name rescuehub
kind load docker-image rescuehub-gateway:local --name rescuehub
```

### 4. Subir a estrutura principal

```bash
bash apply-local.sh
```

Esse script sobe:

```text
00-config
10-database
30-jobs
20-application
25-gateway
```

### 5. Testar pelo API Gateway

```bash
kubectl -n rescuehub port-forward service/api-gateway 8000:8000
```

Acesse:

```text
http://localhost:8000
```

No GitHub Codespaces, abra a porta `8000` na aba **Ports**.

### 6. Testar o healthcheck do Gateway

```text
http://localhost:8000/gateway/health/
```

Você deve receber uma resposta JSON parecida com:

```json
{
  "ok": true,
  "service": "rescuehub-api-gateway",
  "backend_base_url": "http://rescuehub-web:8000"
}
```

## Como aplicar o Ingress

O Ingress já está configurado para apontar para o Service `api-gateway`.

```bash
bash apply-ingress.sh
```

Importante: o Ingress só recebe tráfego externo se existir um **Ingress Controller** no cluster, como NGINX Ingress Controller.

## Criar superusuário

O superusuário continua sendo criado no Django principal, não no Gateway:

```bash
kubectl -n rescuehub exec -it deploy/rescuehub-web -- python app/manage.py createsuperuser
```

## Ver logs

Gateway:

```bash
kubectl -n rescuehub logs deploy/api-gateway
```

Django principal:

```bash
kubectl -n rescuehub logs deploy/rescuehub-web
```

Postgres:

```bash
kubectl -n rescuehub logs statefulset/postgres
```

## Atualizar depois de alterar código

Se alterar o Django principal:

```bash
docker build -t rescuehub-web:local -f Dockerfile.k8s .
kind load docker-image rescuehub-web:local --name rescuehub
kubectl -n rescuehub rollout restart deployment/rescuehub-web
```

Se alterar o Gateway:

```bash
docker build -t rescuehub-gateway:local -f Dockerfile.gateway.k8s .
kind load docker-image rescuehub-gateway:local --name rescuehub
kubectl -n rescuehub rollout restart deployment/api-gateway
```

## Observação didática

Este Gateway foi implementado como um proxy didático em Django. Ele recebe a requisição, registra o encaminhamento e repassa para o Django principal pelo Service interno `rescuehub-web`.

Em produção, seria mais comum usar um gateway dedicado, como Kong, NGINX, Traefik, APISIX ou Envoy, mas para a atividade da faculdade esta implementação deixa explícito que existe um serviço próprio atuando como API Gateway.
