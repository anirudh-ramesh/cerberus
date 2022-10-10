import sys
sys.path.append(".")
from django import forms
from irasusapp.models import Crmuser
from user_management.models import Organisation,OrganisationProfile,Role



class UserCreatedByAdmin(forms.ModelForm):
    class Meta:
        model = Crmuser
        fields = ['username','email','contact','password','password_conformation']


class OrgasationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ['serial_number','organisation_name','created_at','is_active']

class OrganisationProfileForm(forms.ModelForm):
    class Meta:
        model = OrganisationProfile
        fields = [
            'battery_pack_manufacture','battery_pack_distributor','battery_pack_sub_distributor',
            'battery_pack_financier','battery_pack_owner','battery_pack_operator','vehical_manufacture',
            'vehical_distributor','vehical_sub_distributor','vehical_sub_distributor',
            'vehical_sub_distributor','vehical_retailer','vehical_financier',
            'vehical_owner','vehical_operator','battrey_swap_satation_manufacture',
            'battrey_swap_satation_distributor','battrey_swap_satation_sub_distributor',
            'battrey_swap_satation_financier','battrey_swap_satation_owner',
            'battrey_swap_satation_operator'
        ]

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['roles','name','select','org_id']
        labels = {
            'roles':'Role Name',
            'name':'Permission',
        }
        def __init__(self, *args, **kwargs):
            super(Role,self).__init__(*args, **kwargs)
            self.fields['select'].empty_label = "select"