from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ---------- upload paths ----------
def event_cover_upload(instance, filename):
    # /media/events/covers/<user_id>/<filename>
    return f"events/covers/{instance.created_by_id}/{filename}"

def event_gallery_upload(instance, filename):
    # /media/events/gallery/<event_id>/<filename>
    return f"events/gallery/{instance.event_id}/{filename}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    # use a tidy cover path; keep nullable
    image = models.ImageField(upload_to=event_cover_upload, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events_created')

    class Meta:
        ordering = ["date", "time"]  # default listing order

    def __str__(self):
        return f"{self.title} — {self.date}"

    # Convenience helpers (handy in templates/views)
    @property
    def attendee_count(self):
        return self.rsvps.count()

    @property
    def is_upcoming(self):
        from datetime import date
        return self.date >= date.today()

    def can_view(self, user):
        """Only creator + public viewers for private events."""
        if not self.is_private:
            return True
        return user.is_authenticated and (user == self.created_by)


class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} RSVP'd to {self.event.title}"


class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=event_gallery_upload)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Photo for {self.event.title}"

    # Enforce max 5 photos per event
    def clean(self):
        if not self.pk and self.event.images.count() >= 5:
            raise ValidationError("You can upload at most 5 photos per event.")

    def save(self, *args, **kwargs):
        self.full_clean()  # runs clean() above
        return super().save(*args, **kwargs)
