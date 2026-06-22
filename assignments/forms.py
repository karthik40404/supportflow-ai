from django import forms
from .models import Assignment
from accounts.models import User

class AssignmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(role='employee', is_active=True)
        self.fields['employee'].widget.attrs['class'] = 'form-select'
        self.fields['deadline'].widget = forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
        self.fields['notes'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})

    class Meta:
        model = Assignment
        fields = ['employee', 'deadline', 'notes']
