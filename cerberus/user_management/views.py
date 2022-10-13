from django.utils import timezone
from irasusapp.models import Crmuser
from user_management.models import Organisation, OrganisationProfile, Role
from .forms import OrganisationProfileForm, UserCreatedByAdmin, OrgasationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from db_connect import sql_query,inset_into_db,getOrgUserInfo,orgProfileAddData,getOrgProfiles,organisationmultiplePermission,insertIntoOrgnisationPermission

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
    pi =list(Crmuser.objects.filter(pk=id).values())
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        contact = request.POST['contact']
        # last_login = request.POST['lastlogin']
        isactive = request.POST.get('is_active')
        if isactive == 'on':
            isactive = True
        else:
            isactive = False
        Crmuser.objects.filter(email=id).update(username=username,email=email,contact=contact,is_active=isactive, updated_at = timezone.now())
        pi=[{"email":email ,"username":username, "contact":contact, "is_active": isactive }]
        return render(request,'user_management_templates/update_user.html',{ 'form': pi })

    pi =list(Crmuser.objects.filter(pk=id).values())
    return render(request,'user_management_templates/update_user.html',{ 'form': pi })


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
        data = Organisation.objects.filter(is_active=True).values()
    contex = {'organisation_data' : data }
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


def addOrganisationProfile(request,id):
    if request.method == "POST":
        formData = OrganisationProfile.objects.create(
            battery_pack_manufacture = request.POST['battery_pack_manufacture'],
            battery_pack_distributor = request.POST['battery_pack_distributor'],
            battery_pack_sub_distributor = request.POST['battery_pack_sub_distributor'],
            battery_pack_financier = request.POST['battery_pack_financier'],
            battery_pack_owner = request.POST['battery_pack_owner'],
            battery_pack_operator = request.POST['battery_pack_operator'],
            vehical_manufacture = request.POST['vehical_manufacture'],
            vehical_distributor = request.POST['vehical_distributor'],
            vehical_sub_distributor = request.POST['vehical_sub_distributor'],
            vehical_retailer = request.POST['vehical_retailer'],
            vehical_financier = request.POST['vehical_financier'],
            vehical_owner = request.POST['vehical_owner'],
            vehical_operator = request.POST['vehical_operator'],
            battrey_swap_satation_manufacture = request.POST['battrey_swap_satation_manufacture'],
            battrey_swap_satation_distributor = request.POST['battrey_swap_satation_distributor'],
            battrey_swap_satation_sub_distributor = request.POST['battrey_swap_satation_sub_distributor'],
            battrey_swap_satation_financier = request.POST['battrey_swap_satation_financier'],
            battrey_swap_satation_owner = request.POST['battrey_swap_satation_owner'],
            battrey_swap_satation_operator = request.POST['battrey_swap_satation_operator']
        )
        formData.save()
        orgProfileAddData(id,formData.id)
    return render(request,'add_organisation_profile.html')

def listOrganisationProfile(request,id):
    if request.method == "GET":
        data = getOrgProfiles(id)
    contex = {'organisation_profile_data' : data }
    return render(request, 'list_organisation_profile.html',contex)

def createUserRole(request,id):
    if request.method == "POST":
        role_name=request.POST.get("roles")
        permission=request.POST.get("permission")
        data= insertIntoOrgnisationPermission(permission,role_name,id)
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
    role_data = list(Role.objects.filter(pk=id).values())
    if request.method == "POST":
        role = request.POST['roles']
        name = request.POST['name']
        print(name,role)
        data = Role.objects.filter(id=id).update(roles=role, name= name)
        role_data = [{"roles": role,"name": name}]
        return render(request,'user_management_templates/update_role.html',{'form': role_data})

    role_data =list(Role.objects.filter(pk=id).values())
    return render(request,'user_management_templates/update_role.html',{'form': role_data})

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
            orgprofiledata = getOrgProfiles(id)
            multipleOrg_role = organisationmultiplePermission(id)
            roles = list(Role.objects.filter(org_id=id).values())

        context = {
            'user_org_list': user_multiple_role,
            'data':data,
            'orgprofiledata': orgprofiledata,
            'roles': roles,
            'multipleOrg_role': multipleOrg_role
        }
        return render(request,"user_management_templates/user_org_list.html",context)        
    except Exception as e:
        print("Error While deleting Record",e)


