import sys
sys.path.append(".")
from django import forms
from irasusapp.models import Crmuser


class UserCreatedByAdmin(forms.ModelForm):
    class Meta:
        model = Crmuser
        fields = ['username','email','contact','password','password_conformation']