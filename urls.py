from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('events/', include('events.urls')),
    path('comments/', include('comments.urls')),
    path('api/', include('events.api_urls')),   # <-- we’ll create this file
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),

# ok even if empty
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
