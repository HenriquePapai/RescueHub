# Instalação
## 1. Clonar o repositório:
   git clone https://github.com/HenriquePapai/RescueHub

## 2. Instalar as dependências:
   pip install -r requirements.txt

## 3. Subir os serviços:
   docker-compose up --build
   docker-compose exec web python manage.py migrate

## 4. Acessar o serviço:
   http://127.0.0.1:8000/
