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
```bash scripts/backup_db.sh
```
## 2. Restaurar um backup:
```bash scripts/restore_db.sh backups/rescuehub_YYYYMMDD_HHMMSS.sql.gz
```
## 3. Backup automático via pipeline:
A cada push, o job Backup - PostgreSQL roda automaticamente após o delivery.
Para acompanhar: GitHub → Actions → run mais recente → Artifacts.
Para disparar manualmente: GitHub → Actions → Projeto → Run workflow.