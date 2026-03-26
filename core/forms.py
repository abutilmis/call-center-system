from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Entity, CorrectionRequest, KnowledgeBase, Announcement

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

class AgentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = 'agent'
        if commit:
            user.save()
        return user