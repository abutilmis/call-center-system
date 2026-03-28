from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Entity, KnowledgeBase, Announcement

class EntityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select rounded-pill px-4'})
            else:
                field.widget.attrs.update({'class': 'form-control rounded-pill px-4'})

    class Meta:
        model = Entity
        fields = [
            'entity_type', 'name', 'phone', 'phone2', 'phone3', 'city', 'woreda', 'region',
            'location', 'registration_id', 'tvet_type', 'labor_id', 'additional_info'
        ]
        widgets = {
            'additional_info': forms.Textarea(attrs={'rows': 3, 'class': 'form-control rounded-4 px-4'}),
        }



class KnowledgeBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select rounded-pill px-4'})
            else:
                field.widget.attrs.update({'class': 'form-control rounded-pill px-4'})

    class Meta:
        model = KnowledgeBase
        fields = ['question', 'answer', 'category']

class AnnouncementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control rounded-pill px-4'})

    class Meta:
        model = Announcement
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control rounded-4 px-4'}),
        }

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
from django import forms

class AgencyUploadForm(forms.Form):
    file = forms.FileField(
        label='Excel file',
        help_text='Upload an Excel (.xlsx) file with columns: Name, Phone1, Phone2, City, Woreda'
    )    
class OSSCUploadForm(forms.Form):
    file = forms.FileField(
        label='Excel file',
        help_text='Upload an Excel (.xlsx) file with columns: Region, Zone/City, Woreda/Sub-City, OSSC Name'
    )    

class TVETUploadForm(forms.Form):
    file = forms.FileField(
        label='Excel file',
        help_text='Upload an Excel (.xlsx) file with columns: Institution Name, Region, Zone/ Town/ Sub city, Woreda, Type, labor id, phone no, phone no2, phone no3, Position'
    )