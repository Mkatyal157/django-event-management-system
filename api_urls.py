from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import EventViewSet, RSVPViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='api-events')
router.register(r'rsvps', RSVPViewSet, basename='api-rsvps')

urlpatterns = [
    path('', include(router.urls)),
]
