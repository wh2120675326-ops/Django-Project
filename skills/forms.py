from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Skill, Review


def style_fields(form):
    """Apply Bootstrap classes in one place to keep templates small."""
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['title', 'category', 'description', 'exchange', 'location']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(choices=[(n, f'{n} / 5') for n in range(5, 0, -1)], coerce=int)

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share what was helpful about this skill…'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_fields(self)
