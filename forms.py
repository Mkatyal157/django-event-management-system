from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'image', 'is_private']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_private':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

# ---- allow multiple files ----
class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

class EventImagesForm(forms.Form):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False,
        help_text='Upload up to 5 photos (JPEG/PNG).'
    )
