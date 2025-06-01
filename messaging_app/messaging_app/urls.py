from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API routes - inclure les routes de l'app chats
    path('api/', include('chats.urls')),
    
    # API Authentication - requis par la vérification
    path('api-auth/', include('rest_framework.urls')),
    
    # Optionnel : route pour la documentation de l'API si vous utilisez DRF
    # path('api/docs/', include_docs_urls(title='Messaging App API')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)