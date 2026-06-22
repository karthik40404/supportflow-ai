from django import forms
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of your issue...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Describe your issue in detail...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'category', 'suggested_department']
        widgets = {f: forms.Select(attrs={'class': 'form-select'}) for f in ['status','priority','category','suggested_department']}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a comment...'}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
