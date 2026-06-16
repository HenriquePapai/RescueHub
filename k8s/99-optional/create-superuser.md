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
