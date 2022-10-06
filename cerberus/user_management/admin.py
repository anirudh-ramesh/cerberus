from django.contrib import admin
from .models import Organisation, OrganisationProfile, Role
# Register your models here.


admin.site.register(Organisation)
admin.site.register(OrganisationProfile)
admin.site.register(Role)