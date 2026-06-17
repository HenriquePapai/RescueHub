import logging
from http.cookies import SimpleCookie

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)


ALLOWED_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
}


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


REQUEST_HEADERS_TO_SKIP = HOP_BY_HOP_HEADERS | {
    "content-length",
    "host",
}


RESPONSE_HEADERS_TO_SKIP = HOP_BY_HOP_HEADERS | {
    "content-length",
    "content-encoding",
    "set-cookie",
}


def gateway_health(request):
    return JsonResponse(
        {
            "ok": True,
            "service": "rescuehub-api-gateway",
            "backend_base_url": settings.BACKEND_BASE_URL,
        }
    )


def build_backend_url(path="", query_string=""):
    backend_base_url = settings.BACKEND_BASE_URL.rstrip("/")
    clean_path = (path or "").lstrip("/")

    url = f"{backend_base_url}/{clean_path}"

    if query_string:
        url = f"{url}?{query_string}"

    return url


def get_original_host(request):
    return (
        request.headers.get("X-Forwarded-Host")
        or request.headers.get("Host")
        or request.get_host()
    )


def get_original_proto(request):
    proto = (
        request.headers.get("X-Forwarded-Proto")
        or ("https" if request.is_secure() else "http")
    )

    if "," in proto:
        proto = proto.split(",")[0].strip()

    return proto


def copy_request_headers(request):
    """
    Copia os headers recebidos pelo Gateway para o backend principal.

    Importante:
    - O header Cookie é preservado como veio do navegador.
    - Não usamos cookies=request.COOKIES no requests.request.
    - Isso evita inconsistência entre csrfmiddlewaretoken e csrftoken.
    """
    headers = {}

    for key, value in request.headers.items():
        key_lower = key.lower()

        if key_lower in REQUEST_HEADERS_TO_SKIP:
            continue

        headers[key] = value

    original_host = get_original_host(request)
    original_proto = get_original_proto(request)

    remote_addr = request.META.get("REMOTE_ADDR", "")
    previous_forwarded_for = request.headers.get("X-Forwarded-For")

    if previous_forwarded_for:
        forwarded_for = f"{previous_forwarded_for}, {remote_addr}"
    else:
        forwarded_for = remote_addr

    headers["Host"] = original_host
    headers["X-Forwarded-Host"] = original_host
    headers["X-Forwarded-Proto"] = original_proto
    headers["X-Forwarded-For"] = forwarded_for

    return headers


def rewrite_location_header(location, request):
    if not location:
        return location

    backend_base_url = settings.BACKEND_BASE_URL.rstrip("/")

    if not location.startswith(backend_base_url):
        return location

    original_proto = get_original_proto(request)
    original_host = get_original_host(request)
    external_base_url = f"{original_proto}://{original_host}"

    return location.replace(backend_base_url, external_base_url, 1)


def extract_set_cookie_headers(backend_response):
    raw_headers = getattr(getattr(backend_response, "raw", None), "headers", None)

    if raw_headers is not None:
        if hasattr(raw_headers, "getlist"):
            return raw_headers.getlist("Set-Cookie")

        if hasattr(raw_headers, "get_all"):
            return raw_headers.get_all("Set-Cookie") or []

    set_cookie = backend_response.headers.get("Set-Cookie")

    if set_cookie:
        return [set_cookie]

    return []


def copy_response_cookies(backend_response, response):
    """
    Copia Set-Cookie do Django principal para o navegador.

    Isso é importante para sessão, login e csrftoken.
    """
    for set_cookie_header in extract_set_cookie_headers(backend_response):
        cookie = SimpleCookie()

        try:
            cookie.load(set_cookie_header)
        except Exception:
            logger.warning("Não foi possível processar Set-Cookie: %s", set_cookie_header)
            continue

        for name, morsel in cookie.items():
            max_age = morsel["max-age"] or None

            if max_age is not None:
                try:
                    max_age = int(max_age)
                except ValueError:
                    max_age = None

            response.set_cookie(
                key=name,
                value=morsel.value,
                max_age=max_age,
                expires=morsel["expires"] or None,
                path=morsel["path"] or "/",
                domain=morsel["domain"] or None,
                secure=bool(morsel["secure"]),
                httponly=bool(morsel["httponly"]),
                samesite=morsel["samesite"] or None,
            )

# deepcode ignore CSRF: Validacao de CSRF e feita no Django
@csrf_exempt
def proxy_to_backend(request, path=""):
    """
    Proxy reverso transparente.

    O Gateway não valida o CSRF da aplicação principal.
    Ele apenas encaminha a requisição.

    Quem valida o CSRF continua sendo o Django principal.
    """
    if request.method not in ALLOWED_METHODS:
        return JsonResponse(
            {
                "ok": False,
                "error": "method_not_allowed",
                "method": request.method,
            },
            status=405,
        )

    backend_url = build_backend_url(
        path=path,
        query_string=request.META.get("QUERY_STRING", ""),
    )

    headers = copy_request_headers(request)

    try:
        backend_response = requests.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            data=request.body,
            allow_redirects=False,
            timeout=getattr(settings, "BACKEND_TIMEOUT", 30),
        )
    except requests.RequestException as exc:
        logger.exception("Erro ao encaminhar requisição para o backend: %s", exc)

        return JsonResponse(
            {
                "ok": False,
                "error": "backend_unavailable",
                "detail": str(exc),
            },
            status=502,
        )

# deepcode ignore XSS: O conteudo ja vem sanitizado do backend
    response = HttpResponse(
        content=backend_response.content,
        status=backend_response.status_code,
    )

    for header_name, header_value in backend_response.headers.items():
        header_lower = header_name.lower()

        if header_lower in RESPONSE_HEADERS_TO_SKIP:
            continue

        if header_lower == "location":
            header_value = rewrite_location_header(header_value, request)

        response[header_name] = header_value

    copy_response_cookies(backend_response, response)

    response["X-RescueHub-Gateway"] = "django-gateway"

    return response