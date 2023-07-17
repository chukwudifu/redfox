from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view


schema_view = get_schema_view(
   openapi.Info(
      title="Whack a blob API",
      default_version='v1',
      description="API doc",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


@api_view(('GET',))
def health_check(request: HttpRequest):
    return Response()



urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/documentation/',
         schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('healthcheck', health_check),

    path('whack-a-blob/', include('whack_blob.urls')),

    path('users/', include('users.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
