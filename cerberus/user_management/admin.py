from django.contrib import admin
from .models import Organisation, OrganisationProfile, Role,OrganisationPermission

admin.site.register(Organisation)
admin.site.register(OrganisationProfile)
admin.site.register(Role)
admin.site.register(OrganisationPermission)