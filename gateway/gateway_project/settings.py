from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv('GATEWAY_SECRET_KEY', 'django-insecure-local-gateway-key-change-me')
DEBUG = env_bool('GATEWAY_DEBUG', os.getenv('DEBUG', '1'))

ALLOWED_HOSTS = env_list(
    'GATEWAY_ALLOWED_HOSTS',
    'localhost,127.0.0.1,.app.github.dev,rescuehub.local'
)

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'proxy',
]

# O Gateway não usa CsrfViewMiddleware porque ele não processa os formulários.
# Ele apenas encaminha a requisição para o Django principal, que continua sendo
# responsável por validar sessão, login, CSRF e regras de negócio.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'gateway_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': []},
    },
]

WSGI_APPLICATION = 'gateway_project.wsgi.application'

# O Gateway não precisa de banco para a implementação atual. O SQLite em /tmp
# evita erro caso algum comando do Django consulte DATABASES, sem criar dependência
# com o Postgres da aplicação principal.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'rescuehub_gateway.sqlite3',
    }
}

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/gateway-static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://rescuehub-web:8000').rstrip('/')
GATEWAY_TIMEOUT_SECONDS = int(os.getenv('GATEWAY_TIMEOUT_SECONDS', '30'))

# Permite repassar informações corretas de host/protocolo quando existe Ingress
# antes do Gateway.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Upload de PDF/documentos. Para produção, esse ponto deve ser ajustado com
# streaming/proxy reverso mais robusto.
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
