from django import forms
from .models import Entity, CorrectionRequest, KnowledgeBase, Announcement

class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        fields = ['entity_type', 'name', 'phone', 'location', 'registration_id', 'additional_info']
        widgets = {
            'additional_info': forms.Textarea(attrs={'rows': 3}),
        }

class CorrectionRequestForm(forms.ModelForm):
    class Meta:
        model = CorrectionRequest
        fields = ['entity', 'field_to_correct', 'old_value', 'new_value']

class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ['question', 'answer', 'category']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'description']