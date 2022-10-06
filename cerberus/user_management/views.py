from irasusapp.models import Crmuser
from user_management.models import Organisation, OrganisationProfile
from .forms import OrganisationProfileForm, UserCreatedByAdmin, OrgasationForm,UserRole
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.

def addUser(request):
    form = UserCreatedByAdmin()
    if request.method == "POST":
        form = UserCreatedByAdmin(request.POST)
        if form.is_valid():
            form.save()
    context = { 'form': form }
    return render(request,'user_management_templates/user_add.html',context)


def getUser(request):
    if request.method == "GET":
        data = list(Crmuser.objects.values())
        print(data, "[][][][][][][][")
    contex = {'user_data' : data }
    return render(request, 'user_management_templates/get_userdata.html',contex)


def updateUser(request,id):
    if request.method == 'POST':
        print("IF IN THIS CONDITION ")
        pi = Crmuser.objects.get(pk=id)
        fm = UserCreatedByAdmin(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
    else:
        pi = Crmuser.objects.get(pk=id)
        fm = UserCreatedByAdmin(instance=pi)
    return render(request,'user_management_templates/update_user.html',{'form': fm})


def deleteUser(request, id):
    try:
        pi = Crmuser.objects.get(pk=id)
        if request.method == 'POST':
            print("IF IN THE POST")
            pi.delete()
            return redirect('user_management:getdata')
        context = {}
        return render(request, "user_management_templates/get_userdata.html", context)
    except Exception as e:
        print("Error While deleting Record",e)

def addOrganisation(request):
    form = OrgasationForm()
    if request.method == "POST":
        form = OrgasationForm(request.POST)
        if form.is_valid():
            form.save()
    context = { 'form': form }
    return render(request,'add_organisation.html',context)


def listOrganisation(request):
    if request.method == "GET":
        data = list(Organisation.objects.values())
    contex = {'organisation_data' : data }
    return render(request, 'list_organisation_data.html',contex)


def updateOranisation(request,id):
    if request.method == 'POST':
        print("IF IN THIS CONDITION ")
        pi = Organisation.objects.get(pk=id)
        fm = OrgasationForm(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
    else:
        pi = Organisation.objects.get(pk=id)
        fm = OrgasationForm(instance=pi)
    return render(request,'update_organisation.html',{'form': fm})


def deleteOraganisation(request, id):
    try:
        pi = Organisation.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            return redirect('user_management:listorg')
        return render(request, "list_organisation_data.html", {})
    except Exception as e:
        print("Error While deleting Record",e)


def addOrganisationProfile(request):
    form = OrganisationProfileForm()
    if request.method == "POST":
        form = OrganisationProfileForm(request.POST)
        if form.is_valid():
            form.save()
    context = { 'organisation_profile': form }
    return render(request,'add_organisation_profile.html',context)

def listOrganisationProfile(request):
    if request.method == "GET":
        data = list(OrganisationProfile.objects.values())
    contex = {'organisation_profile_data' : data }
    return render(request, 'list_organisation_data.html',contex)

def addUserRole(request):
    form = UserRole()
    if request.method == "POST":
        form = UserRole(request.POST)
        if form.is_valid():
            form.save()
    context = { 'form': form }
    return render(request,'user_management_templates/add_user_role.html',context)
