from django.utils import timezone
from irasusapp.models import Crmuser
from .models import Swapstation
from user_management.models import Organisation, OrganisationPermission, OrganisationProfile, Role,Settings,userSettings
from .forms import UserCreatedByAdmin, OrgasationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from urllib import parse
from db_connect import sql_query,inset_into_db,getOrgUserInfo,orgProfileAddData,getOrgProfiles,organisationmultiplePermission,insertIntoOrgnisationPermission,removeUserFromOrg ,getOrgInfobyEmail
from common import successAndErrorMessages,UserPermission,permission
from django.contrib.auth.hashers import make_password, check_password


#This Function Used to Add User.
def addUser(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    form = UserCreatedByAdmin()
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return render(request,'user_management_templates/user_add.html',{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin")})
    
    if request.method == "POST":
        if Crmuser.objects.filter(email=request.POST.get("email")).exists():
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['emailTaken'])
            return render(request,'user_management_templates/user_add.html',{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin")})
        user_name = request.POST.get('username')
        new_data = request.POST.get("email")
        user_type= request.POST.get("user_type")
        password = request.POST.get('password')
        contact = request.POST.get('contact')
        is_admin=False
        if(request.POST.get("user_type") == "Admin"):
            is_admin=True
        form = Crmuser.objects.create(email=new_data,contact=contact,username= user_name, password=make_password(password),user_type=user_type,is_admin=is_admin,created_by=request.session.get("user_type"),created_id=request.session.get("email"))
        form.save()
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['userCreate'])
        return redirect('user_management:demo')
    context = {"newuserPermission":newuserPermission, 'form': form,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission }
    return render(request,'user_management_templates/user_add.html',context)

#This function used for Listing of users.
def getUser(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if request.method == "GET":
        if(request.session.get("IsAdmin")):
            data = list(Crmuser.objects.values())
        else:
            data=list(Crmuser.objects.filter(email=request.session.get("email")).values())
    contex = {"newuserPermission":newuserPermission,'user_data' : data ,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission}
    return render(request, 'user_management_templates/get_userdata.html',contex)

#This function will update Users.
def updateUser(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    pi =list(Crmuser.objects.filter(pk=id).values())
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return render(request,'user_management_templates/update_user.html',{"newuserPermission":newuserPermission, 'form': pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission })

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
        pi=[{"email":email ,"username":username, "contact":contact, "is_active": isactive,'UserPermission':userPermission }]
        return render(request,'user_management_templates/update_user.html',{"newuserPermission":newuserPermission, 'form': pi,"IsAdmin":request.session.get("IsAdmin") })

    pi =list(Crmuser.objects.filter(pk=id).values())
    return render(request,'user_management_templates/update_user.html',{"newuserPermission":newuserPermission, 'form': pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission  })

#Delete records from User table.
def deleteUser(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        pi = Crmuser.objects.get(pk=id)
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:getdata')

        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeUser'])
            return redirect('user_management:getdata')
        context = {"newuserPermission":newuserPermission,'item': pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission} 
        return render(request, "delete.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


#This Function Used to Add Organisation.
def addOrganisation(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    form = OrgasationForm()
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect("user_management:listorg")

    if request.method == "POST":
        form = OrgasationForm(request.POST)
        if Organisation.objects.filter(serial_number=form.data['serial_number']).exists():
            messages.add_message(request, messages.WARNING,"Organisation already exists.") 
            return redirect('user_management:addorg')
        
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['createOrganisation'])
        return redirect("user_management:addorg")
    context = {"newuserPermission":newuserPermission, 'form': form,'UserPermission':userPermission }

    return render(request,'add_organisation.html',context)

#Listing of Organisation.
def listOrganisation(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if request.method == "GET":
        print(request.session.get('IsAdmin'))
        if(request.session.get('IsAdmin')):
            data = Organisation.objects.filter().values()

        else:
            filterData=getOrgInfobyEmail(request.session.get('email'))
            data=[]
            for i in filterData:
                data=data + list(Organisation.objects.filter(serial_number=i).values())
    contex = {"newuserPermission":newuserPermission,'organisation_data' : data,"IsAdmin":request.session.get('IsAdmin'),'UserPermission':userPermission}
    return render(request, 'list_organisation_data.html',contex)

#This function will update Organisation.
def updateOranisation(request,id):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        userPermission=UserPermission(request,request.session.get("IsAdmin"))
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
            "IsAdmin":request.session.get("IsAdmin"),
            'UserPermission':userPermission,
            "newuserPermission":newuserPermission
        }
        # messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateOrganisation'])
        return render(request,'update_organisation.html',context)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#Delete records from Organisation.
def deleteOraganisation(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        pi = Organisation.objects.get(pk=id)
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:listorg')
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeOrganisation'])
            return redirect('user_management:listorg')
        context = {"newuserPermission":newuserPermission,'delete_organisation' : pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission} 
        return render(request, "delete_organisation.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Adding organisation profile data.
def addOrganisationProfile(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

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
    return render(request,'add_organisation_profile.html',{"newuserPermission":newuserPermission, 'id': id ,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

#Listing of organisation profile
def listOrganisationProfile(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('user_management:listorg')
    if request.method == "GET":
        data = getOrgProfiles(id)
    contex = {"newuserPermission":newuserPermission,'organisation_profile_data' : data ,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission }
    return render(request, 'list_organisation_profile.html',contex)


def deleteOraganisationProfile(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:listorg')

        #GETTING ORGNISATION ID FROM LIST_ORGNISATION_PROFILE_PAGE
        url_path = request.get_full_path()
        parse.urlsplit(url_path)
        parse.parse_qs(parse.urlsplit(url_path).query)
        dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(url_path).query))
        
        pi = OrganisationProfile.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING,successAndErrorMessages()['removeOrganisationProfile'])
            context={'id' : dictinary_obj['org_id'],"newuserPermission":newuserPermission }
            return redirect('user_management:orgprofiles', context['id'])

        context = {"newuserPermission":newuserPermission, 'organisation_profile_delete': pi ,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission, 'org_id': dictinary_obj['org_id']}
        return render(request, "delete_organisation_profile.html", context)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#Create a role and inserting into permission organisation 
def createUserRole(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

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
    return render(request,'user_management_templates/add_user_role.html', {"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

#This function is used to get listing role. 
def listRole(request):
    newuserPermission=permission(request.session.get("user_type"))
   
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
    context = { "newuserPermission":newuserPermission,'roledata' : roledata,"IsAdmin":request.session.get("IsAdmin") }
    return render(request,'user_management_templates/list_role.html',context)


#This function will update role.
def updateRole(request,name):
    newuserPermission=permission(request.session.get("user_type"))

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
        return render(request,'user_management_templates/update_role.html',{"newuserPermission":newuserPermission,'form': role_data,"IsAdmin":request.session.get("IsAdmin"),"role_id":name })
    role_data =list(OrganisationPermission.objects.filter(role_id=name).values())
    return render(request,'user_management_templates/update_role.html',{"newuserPermission":newuserPermission,'form': role_data,"IsAdmin":request.session.get("IsAdmin"),"role_id":name})

#Delete records from Organisation permission.
def deleteRole(request,id):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('user_management:listorg')
        pi = OrganisationPermission.objects.get(role_id=id)
        if "deleteUser" in request.get_full_path():
            pi.delete()
            return redirect('user_management:listorg')

        context={"IsAdmin":request.session.get("IsAdmin"),"newuserPermission":newuserPermission,}
        return render(request, "user_management_templates/list_role.html", context)
    except Exception as e:
        print(e)
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#This function is used for listing user role.
def listedUserRole(request):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        user_multiple_role = listRole(request)

        context = {
            'user_role': user_multiple_role,
            "IsAdmin":request.session.get("IsAdmin"),
            "newuserPermission":newuserPermission,
        }
        return render(request,"user_management_templates/user_multiple_role.html",context)        
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#Get Organisation Details.
def orgUserinfo(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

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
            "IsAdmin":request.session.get("IsAdmin"),
            'UserPermission':userPermission,
            "newuserPermission":newuserPermission,
        }
        return render(request,"user_management_templates/user_org_list.html",context)        
    except Exception as e:
        print(e)
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

#This function is used for adding swap station data.
def addSwapStation(request): 
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('home')
    if request.method == "POST":
        if Swapstation.objects.filter(imei_number=request.POST.get('imei_number')).exists():
            messages.add_message(request, messages.WARNING,"Details Already Added for this Swap-station Imei number, try with another one.") 
            return redirect('user_management:addswap')
        formData = Swapstation.objects.create(
            swap_station_name = request.POST.get('swap_station_name'),
            imei_number = request.POST.get('imei_number'),
            number_of_doors = request.POST.get('number_of_doors'),
            charge_specification = request.POST.get('charge_specification'),
            location= request.POST.get('Location'),
            assigned_owner = request.POST.get('assigned_owner'),
            status = request.POST.get('status'),
            assigned_fleet_owner = request.POST.get('assigned_fleet_owner'),
        )
        formData.save()
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['createSwapStation'])
    return render(request,'add_swapstation.html', {"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

#Listing swap station data.
def listSwapstation(request):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        userPermission=UserPermission(request,request.session.get("IsAdmin"))
        # if(request.session.get("IsAdmin") == False):
        #     messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        #     return redirect('home')
        if request.method == "GET":
            data = list(Swapstation.objects.values())
        contex = {"newuserPermission":newuserPermission,'swap_station_data' : data,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveSwapStation":Swapstation.objects.filter(status="Active").count(),"InActiveSwapStation":Swapstation.objects.filter(status="Inactive").count() }
        return render(request, 'list_swapstation_data.html',contex)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])


#Get active and deactive swap station data.
def getActiveAndDeactive(request):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        userPermission=UserPermission(request,request.session.get("IsAdmin"))
        assigned_vehicle = request.get_full_path()
        parse.urlsplit(assigned_vehicle)
        parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
        dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('home')
        if request.method == "GET":
            data = list(Swapstation.objects.filter(status=dictinary_obj.get('action')).values())
        contex = {"newuserPermission":newuserPermission,'swap_station_data' : data is not [] and data or None,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission, "action":dictinary_obj.get('action') }
        return render(request, 'swapstation_list_by_status.html',contex)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])



#This function is used to update swap station data.
def updateSwapstationDetails(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('home')
    update_swapstation = list(Swapstation.objects.filter(imei_number=id).values())

    if request.method == "POST":
        swap_station_name = request.POST.get('swap_station_name')
        imei_number = request.POST.get('imei_number')
        number_of_doors = request.POST.get('number_of_doors')
        charge_specification = request.POST.get('charge_specification')
        assigned_owner = request.POST.get('assigned_owner')
        status = request.POST.get('status')
        assigned_fleet_owner = request.POST.get('assigned_fleet_owner')
        location= request.POST.get('Location')

        Swapstation.objects.filter(imei_number=id).update(
            swap_station_name=swap_station_name, imei_number=imei_number,
            number_of_doors=number_of_doors,charge_specification=charge_specification,
            assigned_owner=assigned_owner,
            status=status,assigned_fleet_owner=assigned_fleet_owner,
            location=location
        )

        update_swapstation = [{
            'swap_station_name':swap_station_name,
            'imei_number':imei_number,'number_of_doors': number_of_doors,
            'charge_specification': charge_specification,
            'location': location,'assigned_owner': assigned_owner,
            'status': status,
            'assigned_fleet_owner': assigned_fleet_owner,
        }]

        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateSwapStation'])
        return render(request,'update_swap_station.html',{"newuserPermission":newuserPermission,'update_swap_station_data': update_swapstation,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission })

    update_swapstation = list(Swapstation.objects.filter(imei_number=id).values())
    return render(request,'update_swap_station.html',{"newuserPermission":newuserPermission,'update_swap_station_data': update_swapstation,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission })

#delete records from swap station table.
def deleteSwapStation(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if(request.session.get("IsAdmin") == False):
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
            return redirect('home')
        pi = Swapstation.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeSwapStation'])
            return redirect('user_management:listswap')
        context={"newuserPermission":newuserPermission,'delete_swap_station': pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission}
        messages.info(request, successAndErrorMessages()['removeSwapStation'])
        return render(request, 'delete_swapstation_data.html', context)
    except Exception as e:
        return messages.add_message(request,messages.WARNING, successAndErrorMessages()['internalError'])

def moduleSettings(request):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        res={"module": [],"module_on":[],"IsAdmin":request.session.get("IsAdmin")}
        module_name = request.GET.get("id")
        if request.method == "GET":
            userPermission=UserPermission(request)
            res['module'] = userPermission["module"]   
            if(module_name):
                data=list(userSettings.objects.filter(user_id=request.session.get("email"),module_name=module_name).values())
                if len(data):
                    if(data[0]["module_status"] == True):
                        userSettings.objects.filter(module_name=module_name,user_id=request.session.get("email")).update(module_status=False,module_name=module_name,user_id=request.session.get("email"))
                        return redirect('user_management:setting')
                    else:
                        userSettings.objects.filter(module_name=module_name,user_id=request.session.get("email")).update(module_status=True,module_name=module_name,user_id=request.session.get("email"))
                        return redirect('user_management:setting')
                user_data = userSettings.objects.create(module_status=False,module_name=module_name,user_id=request.session.get("email"))
                user_data.save()
        res["UserPermission"]=UserPermission(request,True) 
        res["newuserPermission"]=newuserPermission     
        context = res

        return render (request, 'settings.html',context)
    except Exception as e:
        return render (request, 'dashboard.html')
