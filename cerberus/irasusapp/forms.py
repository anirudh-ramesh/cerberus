from .models import BatteryDetail, Crmuser, Vehicle
from django import forms
from django.contrib.auth.forms import UserCreationForm

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = Crmuser
        fields = ['username','email','contact','password','password_conformation']

class BatteryDetailsFrom(forms.ModelForm):
    class Meta:
        model = BatteryDetail
        fields = ['model_name','battery_serial_num','battery_type','bms_type','iot_type',
                  'iot_imei_number','sim_number','warrenty_start_date','warrenty_duration',
                  'assigned_owner','status','battery_cell_chemistry','battery_pack_nominal_voltage',
                  'battery_pack_capacity','charging_status']
    def __init__(self, *args, **kwargs):
        super(BatteryDetailsFrom,self).__init__(*args, **kwargs)
        self.fields['status'].empty_label = "Select"
        self.fields['model_name'].empty_label = "Select"
        self.fields['bms_type'].empty_label = "Select"
        self.fields['battery_serial_num'].required = True

class VehicleDetailsForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_model_name','chasis_number',
        'configuration','vehicle_choice','vehicle_iot_imei_number',
        'vehicle_iot_imei_number','vehicle_sim_number','vehicle_warrenty_start_date',
        'vehicle_warrenty_end_date','assigned_owner','insurance_start_date','insurance_end_date']