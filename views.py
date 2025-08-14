# events/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages  # ✅ flash messages
from datetime import date

from .models import Event, RSVP, EventImage
from .forms import EventForm, EventImagesForm


def event_list(request):
    # public events + your own private ones
    qs = (
        Event.objects.filter(Q(is_private=False) | Q(created_by=request.user))
        if request.user.is_authenticated
        else Event.objects.filter(is_private=False)
    )

    q = request.GET.get('q')
    when = request.GET.get('when')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(location__icontains=q))
    if when == 'upcoming':
        qs = qs.filter(date__gte=date.today())
    elif when == 'past':
        qs = qs.filter(date__lt=date.today())

    qs = qs.order_by('date', 'time')
    return render(request, 'events/event_list.html', {'events': qs, 'today': date.today()})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def create_event(request):
    """
    Create event + optionally upload up to 5 gallery photos.
    Shows success/error banners.
    """
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        images_form = EventImagesForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()

            # Save up to 5 uploaded images
            for f in request.FILES.getlist('images')[:5]:
                EventImage.objects.create(event=event, image=f)

            messages.success(request, "🎉 Event saved successfully.")
            return redirect('event_detail', event_id=event.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EventForm()
        images_form = EventImagesForm()

    return render(request, 'events/event_form.html', {'form': form, 'images_form': images_form})


@login_required
def update_event(request, event_id):
    """
    Edit event + allow adding more photos, capped at 5 total.
    Shows success/error banners.
    """
    event = get_object_or_404(Event, id=event_id, created_by=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST or None, request.FILES or None, instance=event)
        images_form = EventImagesForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            form.save()

            # Respect 5-photo cap
            remaining = max(0, 5 - event.images.count())
            for f in request.FILES.getlist('images')[:remaining]:
                EventImage.objects.create(event=event, image=f)

            messages.success(request, "✅ Event updated.")
            return redirect('event_detail', event_id=event.id)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = EventForm(instance=event)
        images_form = EventImagesForm()

    return render(request, 'events/event_form.html', {'form': form, 'images_form': images_form})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f"🗑️ Deleted “{title}”.")
        return redirect('event_list')
    return render(request, 'events/confirm_delete.html', {'event': event})


@login_required
def toggle_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
    if created:
        messages.success(request, "✅ You’re attending.")
    else:
        rsvp.delete()
        messages.info(request, "ℹ️ RSVP removed.")
    return redirect('event_detail', event_id=event_id)


# OPTIONAL: allow removing a single gallery photo from an event you own
@login_required
def delete_image(request, event_id, image_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)
    img = get_object_or_404(EventImage, id=image_id, event=event)
    img.delete()
    messages.success(request, "🖼️ Photo removed.")
    return redirect('update_event', event_id=event.id)
