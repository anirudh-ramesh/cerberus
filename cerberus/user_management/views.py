from irasusapp.models import Crmuser
from user_management.models import Organisation, OrganisationProfile, Role
from .forms import OrganisationProfileForm, UserCreatedByAdmin, OrgasationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from db_connect import sql_query,inset_into_db,getOrgUserInfo

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
    contex = {'user_data' : data }
    return render(request, 'user_management_templates/get_userdata.html',contex)


def updateUser(request,id):
    if request.method == 'POST':
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
        data = Organisation.objects.values()
        student = Organisation.objects.filter(serial_number="16")
        orgProfile=Organisation.organisation_profile.through.objects.values_list()
    contex = {'organisation_data' : data,'orgProfile': orgProfile }
    return render(request, 'list_organisation_data.html',contex)


def updateOranisation(request,id):
    global listuser
    if request.method == 'POST':
        role=request.POST.get("role_name")
        # list(Role.objects.filter(roles=request.POST.get("role_name")).values())
        pi = Organisation.objects.get(pk=id)
        roles = Role.objects.filter(org_id=id)
        check_boxes = request.POST.getlist('checkedvalue')
        inset_into_db(check_boxes,id,role)
        fm = OrgasationForm(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
        listuser = sql_query(id)    
    else:
        pi = Organisation.objects.get(pk=id)
        fm = OrgasationForm(instance=pi)
        listuser = sql_query(id)
        roles = Role.objects.filter(org_id=id)
        print(listuser)

    context = {
        'form': fm,
        'listuser': listuser,
        'role' : roles
    } 
    return render(request,'update_organisation.html',context)


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

def createUserRole(request,id):
    if request.method == "POST":
        role_name=request.POST.get("roles")
        permission=request.POST.get("permission")
        print(role_name,permission)
        if Role.objects.filter(roles=role_name).exists():
            messages.info(request,'Role is already taken! try another one')
        else:
            form = Role.objects.create(roles=role_name,name=permission,select=True,org_id=id)
            form.save()
    return render(request,'user_management_templates/add_user_role.html')

def listRole(request):
    user_roles = []
    if request.method == "GET":
        roledata = list(Role.objects.values())
    if request.method == "POST":
        id_list = request.POST.getlist('boxes')
        #Uncheck All Events
        Role.objects.update(select=False)
        #Update the Database
        for x in id_list:
            Role.objects.filter(pk=int(x)).update(select=True)

        data = list(Role.objects.values())
        for value in data:
            if value['select'] == True:
                user_roles.append(value)
            else:
                messages.info(request,'No data found')
        return user_roles       
    context = { 'roledata' : roledata }
    return render(request,'user_management_templates/list_role.html',context)



def updateRole(request,id):
    if request.method == 'POST':
        pi = Role.objects.get(pk=id)
        fm = Role(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
    else:
        pi = Role.objects.get(pk=id)
        fm = Role(pi)
    return render(request,'user_management_templates/update_role.html',{'form': fm})

def deleteRole(request,id):
    try:
        pi = Role.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            return redirect('user_management:getrole')

        context={}
        return render(request, "user_management_templates/list_role.html", context)
    except Exception as e:
        print("Error While deleting Record",e)


def listedUserRole(request):
    try:
        user_multiple_role = listRole(request)

        context = {
            'user_role': user_multiple_role
        }
        return render(request,"user_management_templates/user_multiple_role.html",context)        
    except Exception as e:
        print("Error While deleting Record",e)


def orgUserinfo(request,id):
    try:
        if request.method == "GET":
            user_multiple_role = getOrgUserInfo(id)
            data = Organisation.objects.get(pk=id)

        context = {
            'user_org_list': user_multiple_role,
            'data':data
        }
        return render(request,"user_management_templates/user_org_list.html",context)        
    except Exception as e:
        print("Error While deleting Record",e)


