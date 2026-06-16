# Ajuste recomendado no `app/rescuehub/settings.py`

O Kubernetes vai injetar variáveis como `DEBUG`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`, mas o `settings.py` atual ainda mantém alguns valores fixos. Para deixar o projeto mais organizado, troque estes trechos:

```python
DEBUG = True
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://glorious-train-wrv9794w769rcgj95-8000.app.github.dev']
```

por:

```python
DEBUG = os.getenv('DEBUG', '0') == '1'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
```

Também é recomendável adicionar:

```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Para ambiente de faculdade/local, o `runserver` ainda funciona. Para um ambiente mais próximo de produção, configure Gunicorn + WhiteNoise ou NGINX para servir arquivos estáticos.
