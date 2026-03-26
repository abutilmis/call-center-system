from django import forms
from .models import Entity, CorrectionRequest, KnowledgeBase, Announcement
from django.contrib.auth.forms import UserCreationForm
from .models import User

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
        user.role = 'agent'   # New users are agents by default
        if commit:
            user.save()
        return user
    

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class SupervisorLoginForm(AuthenticationForm):
    """Login form that only accepts the supervisor username."""
    username = forms.CharField(
        widget=forms.HiddenInput(),
        initial='supervisor',
        required=True,
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None or self.user_cache.role != 'supervisor':
                raise forms.ValidationError('Invalid supervisor credentials.', code='invalid_login')
        return self.cleaned_data    

