from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import date

from .models import Event, RSVP
from .serializers import EventSerializer, RSVPSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only the creator may edit/delete an event. Others can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'created_by_id', None) == getattr(request.user, 'id', None)


class EventViewSet(viewsets.ModelViewSet):
    """
    /api/events/        GET list (public + your private)
    /api/events/{id}/   GET detail
                        PUT/PATCH/DELETE (owner only)
    """
    serializer_class = EventSerializer
    permission_classes = [IsOwnerOrReadOnly]

    filterset_fields = ['is_private', 'date']
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['date', 'time', 'title']

    def get_queryset(self):
        user = self.request.user
        base = Event.objects.all()
        if user.is_authenticated:
            return base.filter(Q(is_private=False) | Q(created_by=user)).order_by('date', 'time')
        return base.filter(is_private=False).order_by('date', 'time')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='rsvp')
    def rsvp(self, request, pk=None):
        """
        Toggle RSVP (join/leave) for the current user.
        POST /api/events/{id}/rsvp/
        """
        event = self.get_object()
        obj, created = RSVP.objects.get_or_create(event=event, user=request.user)
        if not created:
            obj.delete()
            return Response({"status": "unrsvped"}, status=status.HTTP_200_OK)
        return Response({"status": "rsvped"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny], url_path='attendees')
    def attendees(self, request, pk=None):
        """
        GET /api/events/{id}/attendees/
        """
        event = self.get_object()
        names = list(event.rsvps.select_related('user').values_list('user__username', flat=True))
        return Response({"count": len(names), "usernames": names})


class RSVPViewSet(viewsets.ModelViewSet):
    """
    (Optional) Direct CRUD for RSVP if you need it:
    /api/rsvps/
    """
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RSVP.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
