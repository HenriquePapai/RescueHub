from django.urls import path, re_path

from proxy.views import gateway_health, proxy_to_backend


urlpatterns = [
    path("gateway/health/", gateway_health, name="gateway-health"),
    re_path(r"^(?P<path>.*)$", proxy_to_backend, name="proxy-to-backend"),
]