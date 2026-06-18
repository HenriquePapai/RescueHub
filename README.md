# RescueHub
O RescueHub é uma plataforma web para a gestão de abrigos de animais, projetada para automatizar fluxos de adoção de cães e gatos. O sistema utiliza uma arquitetura de microsserviços para escalabilidade e disponibilidade. O projeto é feito com uma interface Django que se comunica via API Gateway com serviços independentes de Autenticação, Animais, Catálogo e Adoções.

---

# Instalação e Execução
## 1. Clonar o repositório:
```bash
git clone https://github.com/HenriquePapai/RescueHub
```
## 2. Subir os serviços:
```bash
docker-compose up --build
```
## 3. Acessar o serviço:
```bash
http://127.0.0.1:8000/
```
## 4. Para criar um super usuário:
```
docker exec -it rescuehub_web python app/manage.py createsuperuser
```
# Backup e Restauração
## 1. Backup manual:
```bash
scripts/backup_db.sh
```
## 2. Restaurar um backup:
```bash
scripts/restore_db.sh backups/rescuehub_YYYYMMDD_HHMMSS.sql.gz
```

---

# Criar superusuário no Kubernetes

Depois que o Deployment estiver rodando:

```bash
kubectl -n rescuehub get pods
```

Pegue o nome do pod Django e rode:

```bash
kubectl -n rescuehub exec -it deploy/rescuehub-web -- python app/manage.py createsuperuser
```

Para listar usuários:

```bash
kubectl -n rescuehub exec -it deploy/rescuehub-web -- python app/manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); print(list(User.objects.values('id','username','is_superuser','role')))"
```
