from django.utils import timezone
from irasusapp.models import Crmuser
from .models import Swapstation
from user_management.models import Organisation, OrganisationPermission, OrganisationProfile, Role,Settings
from .forms import UserCreatedByAdmin, OrgasationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from db_connect import sql_query,inset_into_db,getOrgUserInfo,orgProfileAddData,getOrgProfiles,organisationmultiplePermission,insertIntoOrgnisationPermission,removeUserFromOrg ,getOrgInfobyEmail
from common import successAndErrorMessages

#This Function Used to Add User.
def addUser(request):

    form = UserCreatedByAdmin()
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return render(request,'user_management_templates/user_add.html',{"IsAdmin":request.session.get("IsAdmin")})

    if request.method == "POST":
        form = UserCreatedByAdmin(request.POST)
        if form.is_valid():
            form.save()
    context = { 'form': form,"IsAdmin":request.session.get("IsAdmin") }
    return render(request,'user_management_templates/user_add.html',context)

#This function used for Listing of users.
def getUser(request):
    if request.method == "GET":
        if(request.session.get("IsAdmin")):
            data = list(Crmuser.objects.values())
        else:
            data=list(Crmuser.objects.filter(email=request.session.get("email")).values())
    contex = {'user_data' : data ,"IsAdmin":request.session.get("IsAdmin")}
    return render(request, 'user_management_templates/get_userdata.html',contex)

#This function will update Users.
def updateUser(request,id):
    pi =list(Crmuser.objects.filter(pk=id).values())
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return render(request,'user_management_templates/update_user.html',{ 'form': pi,"IsAdmin":request.session.get("IsAdmin") })

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        # last_login = request.POST.get('lastlogin')
        isactive = request.POST.get('is_active')
        if isactive == 'on':
            isactive = True
        else:
            isactive = False
        Crmuser.objects.filter(email=id).update(username=username,email=email,contact=contact,is_active=isactive, updated_at = timezone.now())
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateUser'])
        pi=[{"email":email ,"username":username, "contact":contact, "is_active": isactive }]
        return render(request,'user_management_templates/update_user.html',{ 'form': pi,"IsAdmin":request.session.get("IsAdmin") })

    pi =list(Crmuser.objects.filter(pk=id).values())
    return render(request,'user_management_templates/update_user.html',{ 'form': pi,"IsAdmin":request.session.get("IsAdmin")  })

#Delete records from User table.
def deleteUser(request, id):
    try:
        pi = Crmuser.objects.get(pk=id)
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:getdata')

        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeUser'])
            return redirect('user_management:getdata')
        context = {'item': pi,"IsAdmin":request.session.get("IsAdmin")} 
        return render(request, "delete.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


#This Function Used to Add Organisation.
def addOrganisation(request):
    form = OrgasationForm()
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect("user_management:listorg")

    if request.method == "POST":
        form = OrgasationForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect("user_management:listorg")
    context = { 'form': form }
    messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['createOrganisation'])
    return render(request,'add_organisation.html',context)

#Listing of Organisation.
def listOrganisation(request):
    if request.method == "GET":
        print(request.session.get('IsAdmin'))
        if(request.session.get('IsAdmin')):
            data = Organisation.objects.filter().values()

        else:
            filterData=getOrgInfobyEmail(request.session.get('email'))
            data=[]
            for i in filterData:
                data=data + list(Organisation.objects.filter(serial_number=i).values())
    contex = {'organisation_data' : data,"IsAdmin":request.session.get('IsAdmin')}
    return render(request, 'list_organisation_data.html',contex)

#This function will update Organisation.
def updateOranisation(request,id):
    global listuser
    if request.method == 'POST':
        role=request.POST.get("role_name")
        pi = Organisation.objects.get(pk=id)
        roles = Role.objects.filter(org_id=id)
        check_boxes = request.POST.getlist('checkedvalue')
        inset_into_db(check_boxes,id,role,True)
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
        'role' : roles,
        "IsAdmin":request.session.get("IsAdmin")
    }
    messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateOrganisation'])
    return render(request,'update_organisation.html',context)

#Delete records from Organisation.
def deleteOraganisation(request, id):
    try:
        pi = Organisation.objects.get(pk=id)
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:listorg')
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeOrganisation'])
            return redirect('user_management:listorg')
        context = {'delete_organisation' : pi,"IsAdmin":request.session.get("IsAdmin")} 
        return render(request, "delete_organisation.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Adding organisation profile data.
def addOrganisationProfile(request,id):
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('user_management:listorg')
    if request.method == "POST":
        formData = OrganisationProfile.objects.create(
            battery_pack_manufacture = request.POST.get('battery_pack_manufacture'),
            battery_pack_distributor = request.POST.get('battery_pack_distributor'),
            battery_pack_sub_distributor = request.POST.get('battery_pack_sub_distributor'),
            battery_pack_financier = request.POST.get('battery_pack_financier'),
            battery_pack_owner = request.POST.get('battery_pack_owner'),
            battery_pack_operator = request.POST.get('battery_pack_operator'),
            vehical_manufacture = request.POST.get('vehical_manufacture'),
            vehical_distributor = request.POST.get('vehical_distributor'),
            vehical_sub_distributor = request.POST.get('vehical_sub_distributor'),
            vehical_retailer = request.POST.get('vehical_retailer'),
            vehical_financier = request.POST.get('vehical_financier'),
            vehical_owner = request.POST.get('vehical_owner'),
            vehical_operator = request.POST.get('vehical_operator'),
            battrey_swap_satation_manufacture = request.POST.get('battrey_swap_satation_manufacture'),
            battrey_swap_satation_distributor = request.POST.get('battrey_swap_satation_distributor'),
            battrey_swap_satation_sub_distributor = request.POST.get('battrey_swap_satation_sub_distributor'),
            battrey_swap_satation_financier = request.POST.get('battrey_swap_satation_financier'),
            battrey_swap_satation_owner = request.POST.get('battrey_swap_satation_owner'),
            battrey_swap_satation_operator = request.POST.get('battrey_swap_satation_operator')
        )
        formData.save()
        orgProfileAddData(id,formData.id)
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['createOrganisationProfile'])
    return render(request,'add_organisation_profile.html',{ 'id': id ,"IsAdmin":request.session.get("IsAdmin")})

#Listing of organisation profile
def listOrganisationProfile(request,id):
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('user_management:listorg')
    if request.method == "GET":
        data = getOrgProfiles(id)
    contex = {'organisation_profile_data' : data ,"IsAdmin":request.session.get("IsAdmin")}
    return render(request, 'list_organisation_profile.html',contex)


def deleteOraganisationProfile(request, id):
    try:
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:listorg')
        pi = OrganisationProfile.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING,successAndErrorMessages()['removeOrganisationProfile'])
            return redirect('user_management:listorg')
        context = { 'organisation_profile_delete': pi ,"IsAdmin":request.session.get("IsAdmin")}
        return render(request, "delete_organisation_profile.html", context)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#Create a role and inserting into permission organisation 
def createUserRole(request,id):
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('user_management:listorg')
    if request.method == "POST":
        role_name=request.POST.get("roles")
        permission=request.POST.get("permission")
        if Role.objects.filter(roles=role_name).exists():
            get_id=list(Role.objects.filter(roles=role_name).values())
            insertIntoOrgnisationPermission(permission,role_name,get_id[0].get("id"))
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['Role'])

        else:
            form = Role.objects.create(roles=role_name,select=True,org_id=id)
            form.save()
            insertIntoOrgnisationPermission(permission,role_name,form.id)
    return render(request,'user_management_templates/add_user_role.html', {"IsAdmin":request.session.get("IsAdmin")})

#This function is used to get listing role. 
def listRole(request):
    
    user_roles = []
    if request.method == "GET":
        roledata = list(OrganisationPermission.objects.values())
    if request.method == "POST":
        id_list = request.POST.getlist('boxes')
        #Uncheck All Events
        Role.objects.update(select=False)
        #Update the Database
        for x in id_list:
            Role.objects.filter(pk=int(x)).update(select=True)

        data = list(OrganisationPermission.objects.values())
        for value in data:
            if value['select'] == True:
                user_roles.append(value)
            else:
                messages.add_message(request, messages.WARNING, successAndErrorMessages()['dataNotFound'])
        return user_roles       
    context = { 'roledata' : roledata,"IsAdmin":request.session.get("IsAdmin") }
    return render(request,'user_management_templates/list_role.html',context)


#This function will update role.
def updateRole(request,name):
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('user_management:listorg')
    role_data = list(OrganisationPermission.objects.filter(role_id=name).values())
    print(role_data)
    if request.method == "POST":
        role_name = request.POST.get('role_name')
        permission_name = request.POST.get('permission_name')
        OrganisationPermission.objects.filter(role_id=name).update(role_name=role_name,permission_name=permission_name)

        role_data = [{"role_name": role_name, 'permission_name':permission_name }]
        return render(request,'user_management_templates/update_role.html',{'form': role_data,"IsAdmin":request.session.get("IsAdmin"),"role_id":name })
    role_data =list(OrganisationPermission.objects.filter(role_id=name).values())
    return render(request,'user_management_templates/update_role.html',{'form': role_data,"IsAdmin":request.session.get("IsAdmin"),"role_id":name})

#Delete records from Organisation permission.
def deleteRole(request,id):
    try:
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:listorg')
        pi = OrganisationPermission.objects.get(role_id=id)
        if "deleteUser" in request.get_full_path():
            pi.delete()
            return redirect('user_management:listorg')

        context={"IsAdmin":request.session.get("IsAdmin")}
        return render(request, "user_management_templates/list_role.html", context)
    except Exception as e:
        print(e)
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#This function is used for listing user role.
def listedUserRole(request):
    try:
        user_multiple_role = listRole(request)

        context = {
            'user_role': user_multiple_role,
            "IsAdmin":request.session.get("IsAdmin")
        }
        return render(request,"user_management_templates/user_multiple_role.html",context)        
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#Get Organisation Details.
def orgUserinfo(request,id):
    try:
        if request.method == "GET":
            user_multiple_role = getOrgUserInfo(id)
            data = Organisation.objects.get(pk=id)
            org_profile_data = getOrgProfiles(id)
            multiple_org_role = organisationmultiplePermission(id)
            roles = list(Role.objects.filter(org_id=id).values())

        if "removeUser" in request.get_full_path():
            removeUserFromOrg(False,id,str(request.get_full_path()).split("=")[1].split("&action")[0])
            
        context = {
            'user_org_list': user_multiple_role,
            'data':data,
            'orgprofiledata': org_profile_data,
            'roles': roles,
            'multipleOrg_role': multiple_org_role,
            "IsAdmin":request.session.get("IsAdmin")
        }
        return render(request,"user_management_templates/user_org_list.html",context)        
    except Exception as e:
        print(e)
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#This function is used for adding swap station data.
def addSwapStation(request): 
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('home')
    if request.method == "POST":
        formData = Swapstation.objects.create(
            swap_station_name = request.POST.get('swap_station_name'),
            imei_number = request.POST.get('imei_number'),
            number_of_doors = request.POST.get('number_of_doors'),
            charge_specification = request.POST.get('charge_specification'),
            configuration = request.POST.get('configuration'),
            assigned_owner = request.POST.get('assigned_owner'),
            status = request.POST.get('status'),
            assigned_fleet_owner = request.POST.get('assigned_fleet_owner'),
        )
        formData.save()
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['createSwapStation'])
    return render(request,'add_swapstation.html', {"IsAdmin":request.session.get("IsAdmin")})

#Listing swap station data.
def listSwapstation(request):
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('home')
    if request.method == "GET":
        data = list(Swapstation.objects.values())
    contex = {'swap_station_data' : data,"IsAdmin":request.session.get("IsAdmin") }
    return render(request, 'list_swapstation_data.html',contex)

#This function is used to update swap station data.
def updateSwapstationDetails(request,id):
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('home')
    update_swapstation = list(Swapstation.objects.filter(imei_number=id).values())

    if request.method == "POST":
        swap_station_name = request.POST.get('swap_station_name')
        imei_number = request.POST.get('imei_number')
        number_of_doors = request.POST.get('number_of_doors')
        charge_specification = request.POST.get('charge_specification')
        configuration = request.POST.get('configuration')
        assigned_owner = request.POST.get('assigned_owner')
        status = request.POST.get('status')
        assigned_fleet_owner = request.POST.get('assigned_fleet_owner')

        data = Swapstation.objects.filter(imei_number=id).update(
            swap_station_name=swap_station_name, imei_number=imei_number,
            number_of_doors=number_of_doors,charge_specification=charge_specification,
            configuration=configuration,assigned_owner=assigned_owner,
            status=status,assigned_fleet_owner=assigned_fleet_owner,
        )

        update_swapstation = [{
            'swap_station_name':swap_station_name,
            'imei_number':imei_number,'number_of_doors': number_of_doors,
            'charge_specification': charge_specification,
            'configuration': configuration,'assigned_owner': assigned_owner,
            'status': status,
            'assigned_fleet_owner': assigned_fleet_owner,
        }]

        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateSwapStation'])
        return render(request,'update_swap_station.html',{'update_swap_station_data': update_swapstation,"IsAdmin":request.session.get("IsAdmin") })

    update_swapstation = list(Swapstation.objects.filter(imei_number=id).values())
    return render(request,'update_swap_station.html',{'update_swap_station_data': update_swapstation,"IsAdmin":request.session.get("IsAdmin") })

#delete records from swap station table.
def deleteSwapStation(request,id):
    try:
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('home')
        pi = Swapstation.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeSwapStation'])
            return redirect('user_management:listswap')
        context={'delete_swap_station': pi,"IsAdmin":request.session.get("IsAdmin")}
        messages.info(request, successAndErrorMessages()['removeSwapStation'])
        return render(request, 'delete_swapstation_data.html', context)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

def moduleSettings(request):
    module_data=''
    res={"module": [] , 'status': [],"IsAdmin":request.session.get("IsAdmin")}
    if request.method == "GET":
        module_data = Settings.objects.values()
        res['module'] = module_data
        res['status'] = True
        print(module_data)
    context = res
    return render (request, 'settings.html',context)