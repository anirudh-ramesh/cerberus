from django.db import models
import datetime


#ORGANISATION-PROFILE TABLE
class OrganisationProfile(models.Model):
    battery_pack_manufacture = models.CharField(max_length=225,default='')
    battery_pack_distributor = models.CharField(max_length=225,default='')
    battery_pack_sub_distributor = models.CharField(max_length=100,default='')
    battery_pack_financier = models.CharField(max_length=100,default='')
    battery_pack_owner = models.CharField(max_length=100,default='')
    battery_pack_operator = models.CharField(max_length=100,default='')
    vehical_manufacture = models.CharField(max_length=100,default='')
    vehical_distributor = models.CharField(max_length=100,default='')
    vehical_sub_distributor = models.CharField(max_length=100,default='')
    vehical_retailer = models.CharField(max_length=100,default='')
    vehical_financier = models.CharField(max_length=100,default='')
    vehical_owner = models.CharField(max_length=100,default='')
    vehical_operator = models.CharField(max_length=100,default='')
    battrey_swap_satation_manufacture = models.CharField(max_length=100,default='')
    battrey_swap_satation_distributor = models.CharField(max_length=100,default='')
    battrey_swap_satation_sub_distributor = models.CharField(max_length=100,default='')
    battrey_swap_satation_financier = models.CharField(max_length=100,default='')
    battrey_swap_satation_owner = models.CharField(max_length=100,default='')
    battrey_swap_satation_operator = models.CharField(max_length=100,default='')

    def __str__(self):
        return self.battery_pack_manufacture

#ROLE TABLE
class Role(models.Model):
    roles= models.CharField(max_length= 225, default='')
    select = models.BooleanField(default=False)
    org_id = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.roles.upper()

#ORGANISATION TABLE
class Organisation(models.Model):
    serial_number = models.CharField(max_length=100, default='',primary_key=True)
    organisation_name = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=datetime.datetime.now)
    is_active = models.BooleanField(default=True)
    organisation_profile = models.ManyToManyField(OrganisationProfile)
    vehicle_assign = models.ManyToManyField("irasusapp.Vehicle")
    
    def __str__(self):
        return self.organisation_name

#ORGANISATION-PERMISSION
class OrganisationPermission(models.Model):
    permission_name = models.CharField(max_length=225, default='')
    role_id = models.IntegerField(blank=True, default='')
    role_name = models.CharField(max_length=225, default='')

    def __str__(self):
        return self.role_name.upper()

DOOR_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
)

CHARGE_SPECIFICATION = (
    ('58V 15A', '58V 15A'),
    ('66V 12A', '66V 12A')
)

ASSIGN_OWNER = (
    ('LEAP', 'leap'),
    ('CACTUS', 'cactus')
)

#SWAP-STATION TABLE
class Swapstation(models.Model):
    swap_station_name = models.CharField(max_length=225, default='', blank=True)
    imei_number = models.CharField(max_length=225, default='', blank=True, primary_key=True)
    number_of_doors = models.CharField(max_length=225, blank=True)
    charge_specification = models.CharField(max_length=225, blank=True, choices=CHARGE_SPECIFICATION)
    location= models.CharField(max_length=1000,blank=True)
    assigned_owner = models.CharField(max_length=225,blank=True,choices=ASSIGN_OWNER)
    status = models.CharField(max_length=225,default='', blank=True, null=True)
    assigned_fleet_owner = models.CharField(max_length=225,blank=True,null=True)
    battery_swap = models.ForeignKey("irasusapp.BatteryDetail",default=None,on_delete=models.CASCADE, null=True, blank=True)

class Settings(models.Model):
    module_name = models.CharField(max_length=225, blank=True, null=True)
    
class userSettings(models.Model):
    module_name = models.CharField(max_length=225, blank=True, null=True)
    user = models.ForeignKey("irasusapp.Crmuser",default=None,on_delete=models.CASCADE, null=True, blank=True)
    module_status = models.BooleanField(default=True, null=True)