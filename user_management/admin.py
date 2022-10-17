from django.contrib import admin
from .models import Organisation, OrganisationProfile
# Register your models here.


admin.site.register(Organisation)
admin.site.register(OrganisationProfile)