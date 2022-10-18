from django.db import models
import datetime


# Create your models here.

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


class Role(models.Model):
    roles= models.CharField(max_length= 225, default='')
    select = models.BooleanField(default=False)
    org_id = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.roles.upper()

class Organisation(models.Model):
    serial_number = models.CharField(max_length=100, default='',primary_key=True)
    organisation_name = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=datetime.datetime.now)
    is_active = models.BooleanField(default=True)
    organisation_profile = models.ManyToManyField(OrganisationProfile)
    
    def __str__(self):
        return self.organisation_name


class OrganisationPermission(models.Model):
    permission_name = models.CharField(max_length=225, default='')
    role_id = models.IntegerField(blank=True, default='')
    role_name = models.CharField(max_length=225, default='')

    def __str__(self):
        return self.role_name.upper()
    