# Make Form for Registration

from django import forms 
from .models import Account, UserProfile


# ============================================================================================
    # inheret forms.modelform

class RegistrationForm(forms.ModelForm):
    # create new field to input user detials
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        
        # Give CSS Class to form
        'class': 'form-control',}))
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'}))

    class Meta:
        model = Account
        # fields are referring to fields in ACCOUNTS/MODELS.PY -> classs account(abstract_base_user)
        # username is not here because it will be auto generated using email id
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']
        
       
       
    # ================== 
    # Check if password and refilled password are same
    def clean(self):
        # superclass will anyways get executed from django site
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # compare passwords, invalid if different
        if password != confirm_password:
            raise forms.ValidationError(
                "Passwords are different!"
            )
    # ==================
    # To avoid time waste of giving CSS class to all particular fields in form. 
    # Create method to give to all fields using init self fields
    def __init__(self, *args, **kwargs): #overwrite functionality of self form
        super(RegistrationForm, self).__init__(*args, **kwargs) 
        
        # list of all fields that need CSS class form-control:
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        
        # attributing class to all fields
        for field in self.fields: #look through all the fields
            self.fields[field].widget.attrs['class'] = 'form-control'

# =======================================================================================

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
