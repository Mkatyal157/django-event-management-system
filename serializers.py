from rest_framework import serializers
from django.db.models import Q
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    attendees_count = serializers.IntegerField(source="rsvps.count", read_only=True)
    is_attending = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id","title","description","date","time","location",
            "is_private","attendees_count","is_attending"
        ]

    def get_is_attending(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        return obj.rsvps.filter(user=user).exists()
