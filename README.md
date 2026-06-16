# RescueHub

O RescueHub é uma plataforma web para a gestão de abrigos de animais, projetada para automatizar fluxos de adoção de cães e gatos. O sistema utiliza uma arquitetura de microsserviços para escalabilidade e disponibilidade. O projeto é feito com uma interface Django que se comunica via API Gateway com serviços independentes de Autenticação, Animais, Catálogo e Adoções.

---

# Instalação e Execução

## 1. Clonar o repositório

```bash
git clone https://github.com/HenriquePapai/RescueHub.git
cd RescueHub
```

## 2. Criar o cluster Kubernetes

```bash
kind create cluster --name rescuehub
```

## 3. Construir a imagem da aplicação

```bash
docker build -t rescue-hub:local -f docker/web/Dockerfile .
```

## 4. Carregar a imagem no cluster

```bash
kind load docker-image rescue-hub:local --name rescuehub
```

## 5. Implantar os componentes

```bash
kubectl apply -f k8s/base/
```

## 6. Verificar a implantação

```bash
kubectl get pods -n rescuehub
```

Todos os pods devem estar em estado `Running`.

## 7. Acessar a aplicação

```bash
kubectl port-forward svc/rescuehub-gateway 8080:8080 -n rescuehub
```

Acesse:

```
http://localhost:8080
```

## 8. Criar superusuário (opcional)

```bash
kubectl exec -it deployment/rescuehub-web -n rescuehub -- python app/manage.py createsuperuser
```

---

# Backup e Restauração

## Backup manual

```bash
scripts/backup_db.sh
```

## Restaurar backup

```bash
scripts/restore_db.sh backups/rescuehub_YYYYMMDD_HHMMSS.sql.gz
```

## Backup automático via pipeline

A cada push, o job de backup do PostgreSQL é executado automaticamente pela pipeline GitHub Actions.

Os artefatos podem ser consultados em:

GitHub → Actions → Workflow Executions → Artifacts

---

# Arquitetura

Cliente → API Gateway (Nginx) → Aplicação Django → PostgreSQL

---

# Segurança

* API Gateway com rate limiting
* Cabeçalhos HTTP de segurança
* Execução de containers sem privilégios de root
* Seccomp RuntimeDefault
* Remoção de capabilities Linux
* Secrets do Kubernetes para credenciais
* Verificações SAST e SCA na pipeline CI/CD
