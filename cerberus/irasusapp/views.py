""" 
   - This Modules is develop for Registration, Login, Battery_management,
   Microsoft signup functions, Vehicle_management, Geofencing,
   Driver_management, Generate_CSV.

"""
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
import json
import csv
from django.utils import timezone
from irasusapp.graph_helper import get_user
# from .mixins import MessageHandler
from .forms import CreateUserForm
from .models import Crmuser, BatteryDetail,Vehicle
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password 
# from irasusapp.auth_helper import getSignInFlow, getTokenFromCode,getToken,getMsalApp,removeUserAndToken, storeUser
from db_connect import listAssignedBatteryVehicle,assignedVehicleToOrganisation,getOrgAssignedVehicle,removeAssignedVehiclefromOrganisation,listAssignedVehicleToUser,removeUserVehicle,images_display
from django.contrib.gis.geos import Point,Polygon
from django.apps import apps
from base64 import b64encode
import requests
import json
from django.db.models import F, Q
from common import successAndErrorMessages

format='%Y-%m-%d'


def dashboard(request):
    return render(request,'dashboard.html')

# This Function is Used for register.
def register(request):
    if request.method == 'POST':
        # username = request.POST.get('username')
        email = request.POST.get('email')
        # contact = request.POST.get('contact')
        user_password = request.POST.get('password')
        password_conformation = request.POST.get('password_conformation')

        if user_password == password_conformation:
            password = make_password(user_password)
            password_conformation = password
            if Crmuser.objects.filter(email=email).exists():
                messages.warning(request,successAndErrorMessages()['emailTaken'])
                return redirect('register')
            else:
                user = Crmuser.objects.create_user(email=email, password=password, password_conformation=password_conformation)
                user.save() 
                messages.success(request,successAndErrorMessages()['singupMessage'])
                return render(request, 'login.html')
        else:
            messages.error(request,successAndErrorMessages()['passwordNotMatched'])
            return redirect('register')
    else:
        return render(request, 'register.html')

#This Function is Used for Login.
def loginPage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        crmuser = Crmuser.get_user_by_email(email)
        if crmuser:
            print(password, check_password(password,crmuser.password))
            flag = check_password(password,crmuser.password)
            if flag:
                messages.info(request,successAndErrorMessages()['loginMessage'])
                return redirect('home')     
            else:
                messages.info(request, successAndErrorMessages()['loginErrorMessage'])
                return redirect('login')
        else:
            messages.info(request, successAndErrorMessages()['userNotFound'])

    return render(request,'login.html')  

#This Function is used for Logout.
def logoutUser(request):
    logout(request)
    messages.warning(request, successAndErrorMessages()['logout'])
    return redirect('login')

#Adding battery details to Battery table.
def batteryDetails(request):
    try:
        serial_num = request.POST.get('battery_serial_num')
        if BatteryDetail.objects.filter(battery_serial_num=serial_num):
            messages.warning('Details Already Added')

        if request.method == "POST":
            formData = BatteryDetail.objects.create(
                model_name = request.POST['model_name'],
                battery_serial_num = request.POST['battery_serial_num'],
                battery_type = request.POST['battery_type'],
                bms_type = request.POST['bms_type'],
                iot_type = request.POST['iot_type'],
                iot_imei_number = request.POST['iot_imei_number'],
                sim_number = request.POST['sim_number'],
                warrenty_start_date = request.POST['warrenty_start_date'],
                warrenty_duration = request.POST['warrenty_duration'],
                assigned_owner = request.POST['assigned_owner'],
                status = request.POST['status'],
                battery_cell_chemistry = request.POST['battery_cell_chemistry'],
                battery_pack_nominal_voltage = request.POST['battery_pack_nominal_voltage'],
                battery_pack_nominal_charge_capacity = request.POST['battery_pack_nominal_charge_capacity'],
                charging_status = request.POST['charging_status']
            )
            formData.save()
            messages.info(request, successAndErrorMessages()['addBattery'])
        return render(request,'dashboard.html')
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])

#Listing of battery details table.
def getBatteryDetails(request):
    cahis_id=""
    try:
        if request.method == "GET":
            data = list(BatteryDetail.objects.values())
            cahis_id = str(request.get_full_path()).split("=").pop()

        # ASSIGNED BATTERY TO VEHICLE
        if request.method == "POST":
            vehicle_id = str(request.get_full_path()).split("?").pop()
            cahis_id = vehicle_id.split('&')[0].split("=")[1]
            battery_serial_id = vehicle_id.split('&')[1].split("=")[1]
    
            data = list(BatteryDetail.objects.filter(battery_serial_num=battery_serial_id).values())
            for x in data:
                demo = BatteryDetail.objects.filter(pk=int(x['battery_serial_num'])).update(vehicle_assign_id=str(cahis_id), is_assigned=True)
            return redirect('data')
            
        context = { 'battery_data': data,"cahis_id": cahis_id }
        return render(request, 'battery_details.html',context)
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])

#This Function Will Update_Battery_details/Edit
def updateBatteryDetails(request, id):
    try:
        battery_data = BatteryDetail.objects.filter(battery_serial_num=id).values()
        if request.method == "POST":
            model_name = request.POST.get('model_name')
            battery_serial_num = request.POST.get('battery_serial_num')
            battery_type = request.POST.get('battery_type')
            bms_type = request.POST.get('bms_type')
            iot_type = request.POST.get('iot_type')
            iot_imei_number = request.POST.get('iot_imei_number')
            sim_number = request.POST.get('sim_number')
            warrenty_start_date = datetime.strptime(request.POST.get('warrenty_start_date'),format)
            warrenty_duration = datetime.strptime(request.POST.get('warrenty_duration'),format)
            assigned_owner = request.POST.get('assigned_owner')
            status = request.POST.get('status')
            battery_cell_chemistry = request.POST.get('battery_cell_chemistry')
            battery_pack_nominal_voltage = request.POST.get('battery_pack_nominal_voltage')
            battery_pack_nominal_charge_capacity = request.POST.get('battery_pack_nominal_charge_capacity')
            charging_status = request.POST.get('charging_status')

            BatteryDetail.objects.filter(battery_serial_num=id).update(
            model_name=model_name,battery_serial_num=battery_serial_num,battery_type=battery_type,bms_type=bms_type,
            iot_type=iot_type,iot_imei_number=iot_imei_number,sim_number=sim_number,warrenty_start_date=warrenty_start_date,
            warrenty_duration=warrenty_duration,assigned_owner=assigned_owner,status=status,
            battery_cell_chemistry=battery_cell_chemistry,battery_pack_nominal_voltage=battery_pack_nominal_voltage,
            battery_pack_nominal_charge_capacity=battery_pack_nominal_charge_capacity,
            charging_status=charging_status
            )
            battery_data = [{
                'model_name':model_name,
                'battery_serial_num':battery_serial_num,'battery_type': battery_type,'bms_type': bms_type,
                'iot_type': iot_type,'iot_imei_number': iot_imei_number,'sim_number': sim_number,'warrenty_start_date': warrenty_start_date,
                'warrenty_duration': warrenty_duration,'assigned_owner': assigned_owner,'status': status,
                'battery_cell_chemistry': battery_cell_chemistry,'battery_pack_nominal_voltage': battery_pack_nominal_voltage,
                'battery_pack_nominal_charge_capacity' : battery_pack_nominal_charge_capacity,
                'charging_status': charging_status
                }]
            messages.info(request, successAndErrorMessages()['updateBatteryDetails'])
            return render(request,'update_battery_details.html', {'form': battery_data })

        battery_data = list(BatteryDetail.objects.filter(battery_serial_num=id).values())
        return render(request,'update_battery_details.html',{'form': battery_data})
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])
    
#Delete records from Battery table.
def deleteRecord(request,id):
    try:
        pi = BatteryDetail.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.success(request, successAndErrorMessages()['removeBatteryDetails'])
            return redirect('data')
        context = {}
        return render(request, "battery_details.html", context)
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])


# def login_with_phone_num(request):
#     if request.method == "POST":
#         phone_number = request.POST.get("phone_number")
#         userphone = Crmuser.objects.filter(contact = phone_number)
#         if not userphone:
#             return redirect('register')
        
#         userphone[0].otp = random.randint(100000, 999999)
#         userphone[0].save()

#         message_handler = MessageHandler(userphone, userphone[0].otp).send_otp_on_phone()
#         return redirect('otp')

# def userOtp(request):
#     return render(request, 'otp.html')


# MICROSOFT-LOGIN PART.
def home(request):
    context = intialize_context(request)
    return render(request, 'dashboard.html',context)


def intialize_context(request):
    context={}
    error = request.session.pop('flash_error',None)

    if error != None:
        context['errors'] = []
    context['errors'].append(error)

    context['user'] = request.session.get('user',{'is_authenticated':False})
    return context

#SignIn for Microsoft
# def signIn(request):
#     flow = getSignInFlow()
#     try:
#         request.session['auth_flow'] = flow
#     except Exception as e:
#         print(e)
#     return HttpResponseRedirect(flow['auth_uri'])

# #Sign Out for Microsoft
# def signOut(request):
#     removeUserAndToken(request)
#     return redirect('login')

# def callBack(request):
#     result = getTokenFromCode(request)
#     user = get_user(result['access_token'])
#     storeUser(request,user)
#     return redirect('home')


# def userSignin(request):
#     if request.method == "POST":
#         form = CreateUserForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         CreateUserForm()
#     context = { 'form': form }
#     return render(request, 'login.html', context)


#Adding vehicle to the Vehicle table
def addVehicleDetails(request):
    try: 
        if request.method == "POST":
            formData = Vehicle.objects.create(
                vehicle_model_name = request.POST.get('vehicle_model_name'),
                chasis_number = request.POST.get('chasis_number'),
                configuration = request.POST.get('configuration'),
                vehicle_choice = request.POST.get('vehicle_choice'),
                vehicle_iot_imei_number = request.POST.get('vehicle_iot_imei_number'),
                vehicle_sim_number = request.POST.get('vehicle_sim_number'),
                vehicle_warrenty_start_date = datetime.strptime(request.POST.get('vehicle_warrenty_start_date'), format),
                vehicle_warrenty_end_date = datetime.strptime(request.POST.get('vehicle_warrenty_end_date'), format),
                assigned_owner = request.POST.get('assigned_owner'),
                insurance_start_date = datetime.strptime(request.POST.get('insurance_start_date'), format),
                insurance_end_date = datetime.strptime(request.POST.get('insurance_start_date'), format)
            )
            formData.save()
            messages.success(request, successAndErrorMessages()['addVehicle'])
        return render(request,'add_vehicle_details.html')
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])

#Listing of vehile.
def getVehicleDetails(request):
    try:
        assigned_to_user = str(request.get_full_path()).split("?").pop()
        serial_number = assigned_to_user.split("=").pop()
        email_id = assigned_to_user.split("=").pop()
        if request.method == "GET":
            vehicle_data = list(Vehicle.objects.values())
        
        #Assigned Vehicle To User
        if request.method == "POST":
            assigned_to_user = str(request.get_full_path()).split("?").pop()
            serial_number = assigned_to_user.split("&")[0].split("=")[1]
            chasis_number = assigned_to_user.split('&')[1].split("=")[2]

            if serial_number:
                assignedVehicleToOrganisation(serial_number,chasis_number)
                return redirect('user_management:listorg')

            email_id = assigned_to_user.split("&")[0].split("=")[1]
            vehicle_id = assigned_to_user.split('&')[1].split("=")[2]
            vehicle_data= list(Vehicle.objects.filter(chasis_number = vehicle_id).values())
            for x in vehicle_data:
                demo = Vehicle.objects.filter(pk=int(x['chasis_number'])).update(assigned_to_id=str(email_id), vehicle_selected=True)
                messages.info(request, successAndErrorMessages()['addVehicleToUser']) 
                return redirect('getvehicle')

        return render(request, 'list_vehicle_details.html', {'vehicle_data':vehicle_data , 'email_id': email_id , 'serial_number': serial_number})
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])


#This function will Update Vehicle Table.
def updateVehicleDetails(request,id):
    try:
        update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())

        if request.method == "POST":
            vehicle_model_name = request.POST.get('vehicle_model_name')
            chasis_number = request.POST.get('chasis_number')
            configuration = request.POST.get('configuration')
            vehicle_choice = request.POST.get('vehicle_choice')
            vehicle_iot_imei_number = request.POST.get('vehicle_iot_imei_number')
            vehicle_sim_number = request.POST.get('vehicle_sim_number')
            vehicle_warrenty_start_date = datetime.strptime(request.POST.get('vehicle_warrenty_start_date'), format)
            vehicle_warrenty_end_date = datetime.strptime(request.POST.get('vehicle_warrenty_end_date'), format)
            assigned_owner = request.POST.get('assigned_owner')
            insurance_start_date = datetime.strptime(request.POST.get('insurance_start_date'), format)
            insurance_end_date = datetime.strptime(request.POST.get('insurance_start_date'), format)

            data = Vehicle.objects.filter(chasis_number=id).update(
                vehicle_model_name=vehicle_model_name, chasis_number=chasis_number,
                configuration=configuration,vehicle_choice=vehicle_choice,
                vehicle_iot_imei_number=vehicle_iot_imei_number,vehicle_sim_number=vehicle_sim_number,
                vehicle_warrenty_start_date=vehicle_warrenty_start_date,vehicle_warrenty_end_date=vehicle_warrenty_end_date,
                assigned_owner=assigned_owner,insurance_start_date=insurance_start_date,
                insurance_end_date=insurance_end_date
            )

            update_vehicle = [{
                'vehicle_model_name':vehicle_model_name,
                'chasis_number':chasis_number,'vehicle_choice': vehicle_choice,
                'vehicle_iot_imei_number': vehicle_iot_imei_number,
                'configuration': configuration,'vehicle_sim_number': vehicle_sim_number,
                'vehicle_warrenty_start_date': vehicle_warrenty_start_date,
                'vehicle_warrenty_end_date': vehicle_warrenty_end_date,'assigned_owner': assigned_owner,
                'insurance_start_date': insurance_start_date,
                'insurance_end_date': insurance_end_date
            }]
            messages.info(request, successAndErrorMessages()['updateVehicle'])
            return render(request,'update_vehicle.html',{'update_vehicle_data': update_vehicle })

        update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())
        return render(request,'update_vehicle.html',{'update_vehicle_data': update_vehicle })
    except Exception as error:
        return messages.warning(request, successAndErrorMessages()['internalError']) 

#Delete records from Vehicle table.
def deleteVehicleRecord(request,id):
    try:
        pi = Vehicle.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.info(request, successAndErrorMessages()['removeVehicle'])
            return redirect('getvehicle')
        context = {}
        return render(request, "list_vehicle_details.html", context)
    except Exception as e:
        print("Error While deleting Record",e)
        return messages.error(request, successAndErrorMessages()['internalError'])

#Assigned BatteryList
def assignedBatteryList(request,id):
    try:
        if request.method == "GET":
            data = listAssignedBatteryVehicle(id)

        # Remove battery from vehicle.
        if request.method == "POST": 
            data = listAssignedBatteryVehicle(id)
            assigned_vehicle_battery = Vehicle.objects.filter(chasis_number=id)
            for x in data:
                data = BatteryDetail.objects.filter(pk=x['battery_serial_num']).update(vehicle_assign_id=None, is_assigned=False)

        context = {
            'assigned_battery_list' : data
        }
        return render(request, 'list_assigned_battery.html',context)
    except Exception as e:
        return messages.error(request, successAndErrorMessages()['internalError'])


#Assigned vehicle to org
def assignedOrgVehicleList(request,id):
    try:
        org_vehicle_list = getOrgAssignedVehicle(id)
            
        #Remove vehicle from Organisation
        if request.method == "POST":
            assigned_vehicle = str(request.get_full_path()).split("?").pop()
            vehicle_id = assigned_vehicle.split("&")[0].split("=")[1]
            remove_org_vehicle = removeAssignedVehiclefromOrganisation(id,vehicle_id)
            return redirect('user_management:listorg')
                
        return render(request, 'list_organisation_vehicle.html',{'org_vehicle_list': org_vehicle_list})
    except Exception as e:
        return messages.error(request, successAndErrorMessages()['internalError'])

#Assigned vehicle to user
def assignedVehicleToUser(request,id):
    try:
        user_vehicle =""
        if request.method == "GET":
            user_vehicle = listAssignedVehicleToUser(id)

        #Remove Vehicle from User
        if request.method == "POST":
            assigned_vehicle = str(request.get_full_path()).split("?").pop()
            vehicle_id = assigned_vehicle.split("&")[0].split("=")[1]
            user_vehicle = removeUserVehicle(False,vehicle_id)
            messages.warning(request, successAndErrorMessages()['removeVehiclefromUser'])
            return redirect("user_management:getdata")

        return render(request,'list_assigned_vehicle_to_user.html',{'user_vehicle':user_vehicle})
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError']) 

#Create Geofencing Locations.
# def addgeofenceVehicles(request):
#     try:
#         polygon_coordinates = []
#         longitude_data = []
#         latitude_data = []
#         if request.method == "POST":
#             geoname = request.POST.get('geoname')
#             geotype = request.POST.get('geotype')
#             description = request.POST.get('description')
#             position_add = request.POST.get('pos_address')
#             enter_lat =request.POST.get('enter_latitude')
#             newdata=json.loads(enter_lat)
#             coordinate_data = newdata["features"][0]['geometry']['coordinates']

#             if newdata["features"][0]['geometry']['type'] == 'Point':
#                 longitude = coordinate_data[0]
#                 latitude = coordinate_data[1]
#                 location = Point(float(longitude),float(latitude),srid=4326)            
#                 newdata = Geofence.objects.create(geoname=geoname,geotype=geotype,description=description,enter_latitude=latitude,enter_longitude=longitude,pos_address=position_add,location=location)
#                 messages.success(request, successAndErrorMessages()['locationCreate'])
#                 return render(request, 'geolocation_form.html')


#             if newdata["features"][0]['geometry']['type'] == 'Polygon':
#                 coordinate_polygon = newdata["features"][0]['geometry']['coordinates']
#                 newdata = *((*row,) for row in coordinate_polygon[0]),
#                 converted_tuple_data = list(newdata)
#                 for polygon_data in converted_tuple_data:
#                     res={}
#                     longitude = ((polygon_data[0]),(polygon_data[1]))
#                     res['lat'] = polygon_data[1]
#                     res['lang'] = polygon_data[0]
#                     longitude_data.append(res)
#                     latitude = polygon_data[1]
#                     latitude_data.append(latitude)
#                     polygon_coordinates.append(longitude)
#             geofence = Polygon(((polygon_coordinates)),srid=4326)
#             newdata = Geofence.objects.create(geoname=geoname,geotype=geotype, description=description,enter_latitude=longitude_data,pos_address=position_add,geofence=geofence)
#             messages.success(request, successAndErrorMessages()['locationCreate'])
#         return render(request, 'geolocation_form.html')
#     except Exception as e:
#         return messages.warning(request, successAndErrorMessages()['internalError']) 

#list Geofencing data
# def listgeofenceData(request):
#     try:
#         if request.method == "GET":
#             geofencedata = list(Geofence.objects.values())
#         return render(request, 'list_geofence_data.html',{ 'geofencedata': geofencedata })
#     except Exception as e:
#         return messages.warning(request, successAndErrorMessages()['internalError'])
   
#Add driver For Vechicle Module.
def addDriver(request):
    try:
        if request.method == "POST":
            username = request.POST.get('username')
            email = request.POST.get('contact')
            user_type =  request.POST.get('user_type')
            adhar_proof = request.FILES['adhar_card'].file.read()
            pancard_proof = request.FILES['pan_card'].file.read()
            license_proof = request.FILES['driving_license'].file.read()
            is_active = True

            newdata = Crmuser.objects.create(
                username=username,email=email,user_type=user_type,
                adhar_proof=adhar_proof,pancard_proof=pancard_proof,
                license_proof=license_proof,is_active=is_active
            )
            newdata.save()
            messages.success(request, successAndErrorMessages()['addDriver'])
        return render(request, 'adddriver.html')

    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])

#This function used for listing driver. 
def listAddedDriver(request):
    try:
        if request.method == "GET":
            driverData = images_display()

        context={
                "drivers": driverData
                }
        return render(request, 'list_drivers.html',context)
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])

# This function will Update Driver
def updateDriver(request,id):
    try:
        if request.method == 'GET':
            pi =list(Crmuser.objects.filter(pk=id).values())
            pi[0]["adhar_proof"]=b64encode(pi[0]['adhar_proof']).decode("utf-8")
            pi[0]["email"]=pi[0]["email"]
            pi[0]["username"]=pi[0]["username"]
            pi[0]["user_type"]=pi[0]["user_type"]
            pi[0]["is_active"]=pi[0]["is_active"]
            pi[0]["pancard_proof"]=b64encode(pi[0]['pancard_proof']).decode("utf-8")
            pi[0]["license_proof"]=b64encode(pi[0]['license_proof']).decode("utf-8")
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            isactive = request.POST.get('is_active')
            user_type = request.POST.get('user_type')
            if isactive == 'on':
                isactive = True
            else:
                isactive = False
            Crmuser.objects.filter(email=id).update(username=username,email=email,is_active=isactive,user_type=user_type,updated_at = timezone.now())
            pi =list(Crmuser.objects.filter(pk=id).values())
            pi[0]["adhar_proof"]=b64encode(pi[0]['adhar_proof']).decode("utf-8")
            pi[0]["email"]=pi[0]["email"]
            pi[0]["username"]=pi[0]["username"]
            pi[0]["user_type"]=pi[0]["user_type"]
            pi[0]["is_active"]=pi[0]["is_active"]
            pi[0]["pancard_proof"]=b64encode(pi[0]['pancard_proof']).decode("utf-8")
            pi[0]["license_proof"]=b64encode(pi[0]['license_proof']).decode("utf-8")
            messages.info(request, successAndErrorMessages()['updateDriver'])
            return render(request,'update_driver.html',{ 'form': pi })

        return render(request,'update_driver.html',{ 'form': pi })

    except Exception as error:
        return messages.warning(request, successAndErrorMessages()['internalError'])

#Delete records of driver.
def deleteDriver(request, id):
    try:
        pi = Crmuser.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.info(request, successAndErrorMessages()['removeDriver'])
            return redirect('getdrivers')
        context = {}
        return render(request, "update_driver.html", context)
    except Exception as e:
        return messages.warning(request, successAndErrorMessages()['internalError'])


#Generate CSV field vise.
def filedForCSV(request):
    if request.method == "GET":
        files = list(Vehicle.objects.values())
        data= request.POST.getlist('checkedvalue')
        messages.info(request, successAndErrorMessages()['csvGenerate'])       
    return render(request, 'generate_csv.html')

#Exporting CSV.
def exportCSV(request):
    try:
        getData=str(request.get_full_path()).split("?selectfield=")
        if(getData[1]):
            getData = getData[1].split("@=")
        filterData=getData

        data = list(Vehicle.objects.filter(
        Q(created_date='2022-11-17') |
        Q(created_date='2022-11-19')
        ).values_list(*filterData))
        tablename = Vehicle._meta.model_name

        file_name = f'{tablename}-' + str(datetime.now().date()) + '.csv'

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')

        response['Content-Disposition'] = f'attachment; filename= {file_name}'

        writer = csv.writer(response)

        headers = []

        for i in getData:
            headers.append(i)

        writer.writerow(headers)

        for i in data:
            writer.writerow(i)
        return response

    except Exception as error:
        return messages.warning(request, successAndErrorMessages()['internalError']) 

#Open swap-station doors.
def swapSatationDoors(request):
    url = "http://216.48.177.157:1880/ss/open_door/"

    imei = request.POST.get('imei')
    doorid = request.POST.get('doorid')

    payload = json.dumps({
    "imei": imei,
    "doorid": doorid
    })

    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    return render(request, "swap_station_door.html", {'response': response}) 