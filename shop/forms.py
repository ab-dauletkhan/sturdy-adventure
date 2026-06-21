import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import City
from .json_translations import t

_INPUT = 'w-full px-4 py-3 border border-q-border rounded text-sm text-q-black bg-white focus:outline-none focus:border-q-amber focus:ring-1 focus:ring-q-amber transition-colors'
_SELECT = 'w-full px-4 py-3 border border-q-border rounded text-sm text-q-black bg-white focus:outline-none focus:border-q-amber focus:ring-1 focus:ring-q-amber transition-colors'
_TEXTAREA = 'w-full px-4 py-3 border border-q-border rounded text-sm text-q-black bg-white focus:outline-none focus:border-q-amber focus:ring-1 focus:ring-q-amber transition-colors resize-none'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': _INPUT}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = t('form.email')
        self.fields['email'].error_messages.update({
            'required': t('error.email_required'),
            'invalid': t('error.email_invalid'),
        })
        self.fields['username'].label = t('form.username')
        self.fields['username'].widget.attrs.update({'class': _INPUT})
        self.fields['username'].error_messages.update({
            'required': t('error.username_required'),
            'unique': t('error.username_taken'),
            'invalid': t('error.username_invalid'),
        })
        self.fields['password1'].label = t('form.password')
        self.fields['password1'].widget.attrs.update({'class': _INPUT})
        self.fields['password1'].error_messages.update({
            'required': t('error.password_required'),
        })
        self.fields['password2'].label = t('form.password_confirm')
        self.fields['password2'].widget.attrs.update({'class': _INPUT})
        self.fields['password2'].error_messages.update({
            'required': t('error.password_confirm_required'),
            'password_mismatch': t('error.password_mismatch'),
        })

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        username = self.cleaned_data.get('username')
        if username and username in password:
            raise forms.ValidationError(t('error.password_like_username'))
        if len(password) < 8:
            raise forms.ValidationError(t('error.password_too_short'))
        return password


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = t('form.username')
        self.fields['username'].widget.attrs.update({'class': _INPUT})
        self.fields['username'].error_messages.update({
            'required': t('error.username_required'),
        })
        self.fields['password'].label = t('form.password')
        self.fields['password'].widget.attrs.update({'class': _INPUT})
        self.fields['password'].error_messages.update({
            'required': t('error.password_required'),
        })
        self.error_messages.update({
            'invalid_login': t('error.login_invalid'),
            'inactive': t('error.account_inactive'),
        })


class CheckoutForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': _INPUT}),
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=forms.Select(attrs={'class': _SELECT}),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': _TEXTAREA, 'rows': 3}),
    )
    use_bonus_points = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': _INPUT, 'placeholder': '0', 'id': 'use_bonus_points'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = t('form.first_name')
        self.fields['first_name'].error_messages['required'] = t('error.first_name_required')
        self.fields['last_name'].label = t('form.last_name')
        self.fields['last_name'].error_messages['required'] = t('error.last_name_required')
        self.fields['phone'].label = t('form.phone')
        self.fields['phone'].error_messages['required'] = t('error.phone_required')
        self.fields['city'].label = t('form.city')
        self.fields['city'].empty_label = t('form.city_select')
        self.fields['city'].error_messages['required'] = t('error.city_required')
        self.fields['address'].label = t('form.address')
        self.fields['address'].error_messages['required'] = t('error.address_required')
        self.fields['use_bonus_points'].label = t('form.bonus_points')
        self.fields['use_bonus_points'].help_text = t('form.bonus_help')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        pattern = r'^(\+7|8)[\s\-]?\(?7\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError(t('error.phone_invalid'))
        return phone

    def clean_use_bonus_points(self):
        points = self.cleaned_data.get('use_bonus_points')
        if points is None:
            return 0
        if points < 0:
            raise forms.ValidationError(t('error.negative_number'))
        return points


class CommentForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': _TEXTAREA, 'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = t('form.comment')
        self.fields['text'].widget.attrs['placeholder'] = t('form.comment_placeholder')
        self.fields['text'].error_messages['required'] = t('error.comment_required')
