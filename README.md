# RescueHub
O RescueHub é uma plataforma web para a gestão de abrigos de animais, projetada para automatizar fluxos de adoção de cães e gatos. O sistema utiliza uma arquitetura de microsserviços para escalabilidade e disponibilidade. O projeto é feito com uma interface Django que se comunica via API Gateway com serviços independentes de Autenticação, Animais, Catálogo e Adoções, todos isolados em contêineres Docker.

---

# Instalação e Execução
## 1. Clonar o repositório:
git clone https://github.com/HenriquePapai/RescueHub

## 2. Subir os serviços:
   docker-compose up --build
   docker-compose exec web python manage.py migrate

## 3. Acessar o serviço:
   http://127.0.0.1:8000/
