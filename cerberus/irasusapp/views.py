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
# from .mixins import MessageHandler
from .models import Crmuser, BatteryDetail, IotDevices,Vehicle,Geofence
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password 
# from irasusapp.auth_helper import getSignInFlow, getTokenFromCode,getToken,getMsalApp,removeUserAndToken, storeUser
from db_connect import listAssignedBatteryVehicle,assignedVehicleToOrganisation,getOrgAssignedVehicle,removeAssignedVehiclefromOrganisation,listAssignedVehicleToUser,removeUserVehicle,images_display ,iotDevice
from django.contrib.gis.geos import Point,Polygon
from base64 import b64encode
import requests
from urllib import parse
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
                messages.add_message(request,messages.WARNING, successAndErrorMessages()['emailTaken'])
                return redirect('register')
            else:
                user = Crmuser.objects.create_user(email=email, password=password, password_conformation=password_conformation)
                user.save()
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['singupMessage'])
                return redirect('login')
        else:
            messages.add_message(request,messages.WARNING, successAndErrorMessages()['passwordNotMatched'])
            return redirect('register')
    else:
        return render(request, 'register.html')

#This Function is Used for Login.
def loginPage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        print(email)
        password = request.POST.get('password')
        print(password)
        crmuser = Crmuser.get_user_by_email(email)
        if crmuser:
            print(password, check_password(password,crmuser.password))
            flag = check_password(password,crmuser.password)
            print(flag)
            if flag:
                # messages.add_message(request,messages.INFO,successAndErrorMessages()['loginMessage'])
                return render(request,'dashboard.html',{'email': email})     
            else:
                messages.add_message(request, messages.INFO, successAndErrorMessages()['loginErrorMessage'])
                return redirect('login')
        else:
            messages.add_message(request, messages.INFO, successAndErrorMessages()['userNotFound'])
            return redirect('login')

    return render(request,'login.html')  

#This Function is used for Logout.
def logoutUser(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['logout'])
    return redirect('login')


#Adding battery details to Battery table.
def batteryDetails(request):
    try:
        serial_num = request.POST.get('battery_serial_num')
        if BatteryDetail.objects.filter(battery_serial_num=serial_num):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['alreadyAdded'])
            return render(request,'add_battery_details.html')
        else:
            if request.method == "POST":
                formData = BatteryDetail.objects.create(
                    model_name = request.POST.get('model_name'),
                    battery_serial_num = request.POST.get('battery_serial_num'),
                    battery_type = request.POST.get('battery_type'),
                    bms_type = request.POST.get('bms_type'),
                    iot_type = request.POST.get('iot_type'),
                    # iot_imei_number = request.POST.get('iot_imei_number'),
                    sim_number = request.POST.get('sim_number'),
                    warrenty_start_date = request.POST.get('warrenty_start_date'),
                    warrenty_duration = request.POST.get('warrenty_duration'),
                    assigned_owner = request.POST.get('assigned_owner'),
                    status = request.POST.get('status'),
                    battery_cell_chemistry = request.POST.get('battery_cell_chemistry'),
                    battery_pack_nominal_voltage = request.POST.get('battery_pack_nominal_voltage'),
                    battery_pack_nominal_charge_capacity = request.POST.get('battery_pack_nominal_charge_capacity'),
                    charging_status = request.POST.get('charging_status')
                )
                formData.save()
                messages.add_message(request, messages.INFO, successAndErrorMessages()['addBattery'])
            return render(request,'add_battery_details.html')
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

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
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

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
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateBatteryDetails'])
            return render(request,'update_battery_details.html', {'form': battery_data })

        battery_data = list(BatteryDetail.objects.filter(battery_serial_num=id).values())
        return render(request,'update_battery_details.html',{'form': battery_data})
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Delete records from Battery table.
def deleteRecord(request, id):
    try:
        pi = BatteryDetail.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeBatteryDetails'])
            return redirect('data')
        context = {'item': pi} 
        return render(request, "delete_battery_data.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


def addIotDevice(request):
    try:
        iot_imei_number = request.POST.get('imei_number')
        if IotDevices.objects.filter(imei_number = iot_imei_number):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['alreadyAdded'])
            return render(request,'add_IOT_devices.html')
        else:
            if request.method == "POST":
                formData = IotDevices.objects.create(
                    imei_number = request.POST.get('imei_number'),
                    hardware_version = request.POST.get('hardware_version'),
                    firmware_version = request.POST.get('firmware_version'),
                )
                formData.save()
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['deivceAdded'])
            return render(request,'add_IOT_devices.html')
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


def listIotDevice(request):
    try:
        if request.method == "GET":
            iotdevicedata = list(IotDevices.objects.values())
            batteryWithIotDevice = iotDevice(iotdevicedata)

            #REMOVE BATTERY TO IOT-DEVICE
            if ("action" in request.get_full_path()):
                get_full_path = str(request.get_full_path()).split("?").pop()
                imei_number =get_full_path.split("&action")[0].split("=")[1]
                BatteryDetail.objects.filter(iot_imei_number_id=imei_number).update(iot_imei_number_id=None)
                messages.add_message(request, messages.DANGER, successAndErrorMessages()['removeDeviceFromBattery'])
                return redirect('listdevice')
        return render(request, 'list_IOT_devices.html',{ 'iot_device_data': batteryWithIotDevice })
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

def updateIOTDevice(request,id):
    try:
        update_iot_device = list(IotDevices.objects.filter(imei_number=id).values())
        if request.method == "POST":
            imei_number = request.POST.get('imei_number')
            hardware_version = request.POST.get('hardware_version')
            firmware_version = request.POST.get('firmware_version')
            
            data = IotDevices.objects.filter(imei_number=id).update(
                imei_number=imei_number, hardware_version=hardware_version,
                firmware_version=firmware_version
            )
            update_iot_device = [{
                'imei_number':imei_number,
                'hardware_version':hardware_version,
                'firmware_version': firmware_version,
            }]
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['deviceUpdate'])
            return render(request,'update_IOT_device.html',{'update_IOT_data': update_iot_device })

        update_iot_device = list(IotDevices.objects.filter(imei_number=id).values())
        return render(request,'update_IOT_device.html',{'update_IOT_data': update_iot_device })
    except Exception as error:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

def deleteIOTDeviceRecord(request,id):
    try:
        pi = IotDevices.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeDevice'])
            return redirect('listdevice')
        context={"iot_device": pi }
        return render(request, 'delete_iot_device.html', context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

def assignedIotDeviceToBattery(request):
    
    obj = BatteryDetail.objects.all()
    get_full_path = str(request.get_full_path()).split("?").pop()
    if("action" in get_full_path):
        print(get_full_path.split("&action")[0].split("="))
    
    #ASSIGN BATTERY TO IOT-DEVICE
    if request.method == "POST":
        if("action" in get_full_path and "add" in get_full_path):
            print("action")
            get_full_path = str(request.get_full_path()).split("?").pop()
            imei_number =get_full_path.split("&action")[0].split("=")[1]
            battery_serial_number = request.POST.get('name_of_select')

            already_assign = list(BatteryDetail.objects.filter(battery_serial_num = battery_serial_number).values())
            for x in already_assign:
                if x['iot_imei_number_id'] is not None:
                    messages.add_message(request, messages.WARNING, successAndErrorMessages()['deviceAlreadyAdded'])
                    return redirect('iotdevice')
                else:
                    assignData=BatteryDetail.objects.filter(pk=battery_serial_number).update(iot_imei_number_id=imei_number)
                    messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['deviceAddToBattery'])
                    return redirect('iotdevice')
    context = { 'assinged_iot_device': obj }
    return render(request,'assigned_iot_device_to_battery.html', context)

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
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['addVehicle'])
        return render(request,'add_vehicle_details.html')
    except Exception as e:
        return messages.warning(request, messages.ERROR, successAndErrorMessages()['internalError'])

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
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['addVehicleToUser'])
                return redirect('getvehicle')

        return render(request, 'list_vehicle_details.html', {'vehicle_data':vehicle_data , 'email_id': email_id , 'serial_number': serial_number})
    except Exception as e:
        return messages.warning(request, messages.ERROR,successAndErrorMessages()['internalError'])


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
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateVehicle'])
            return render(request,'update_vehicle.html',{'update_vehicle_data': update_vehicle })

        update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())
        return render(request,'update_vehicle.html',{'update_vehicle_data': update_vehicle })
    except Exception as error:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])

#Delete records from Vehicle table.
def deleteVehicleRecord(request,id):
    try:
        pi = Vehicle.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.ERROR, successAndErrorMessages()['removeVehicle'])
            return redirect('getvehicle')
        context = {'vehicle_data' : pi}
        return render(request, "delete_vehicle_data.html", context)
    except Exception as e:
        print("Error While deleting Record",e)
        return messages.error(request, successAndErrorMessages()['internalError'])

#Assigned BatteryList
def assignedBatteryList(request,id):
    try:
        if request.method == "GET":
            print("IN THE GET")
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
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])


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
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])

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
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeVehiclefromUser'])
            return redirect("user_management:getdata")

        return render(request,'list_assigned_vehicle_to_user.html',{'user_vehicle':user_vehicle})
    except Exception as e:
       return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])

#Create Geofencing Locations.
def addgeofenceVehicles(request):
    try:
        polygon_coordinates = []
        longitude_data = []
        latitude_data = []
        if request.method == "POST":
            geoname = request.POST.get('geoname')
            geotype = request.POST.get('geotype')
            description = request.POST.get('description')
            position_add = request.POST.get('pos_address')
            enter_lat =request.POST.get('enter_latitude')
            newdata=json.loads(enter_lat)
            coordinate_data = newdata["features"][0]['geometry']['coordinates']

            if newdata["features"][0]['geometry']['type'] == 'Point':
                longitude = coordinate_data[0]
                latitude = coordinate_data[1]
                location = Point(float(longitude),float(latitude),srid=4326)            
                newdata = Geofence.objects.create(geoname=geoname,geotype=geotype,description=description,enter_latitude=latitude,enter_longitude=longitude,pos_address=position_add,location=location)
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['locationCreate'])
                return redirect('geofence')


            if newdata["features"][0]['geometry']['type'] == 'Polygon':
                coordinate_polygon = newdata["features"][0]['geometry']['coordinates']
                newdata = *((*row,) for row in coordinate_polygon[0]),
                converted_tuple_data = list(newdata)
                for polygon_data in converted_tuple_data:
                    res={}
                    longitude = ((polygon_data[0]),(polygon_data[1]))
                    res['lat'] = polygon_data[1]
                    res['lang'] = polygon_data[0]
                    longitude_data.append(res)
                    latitude = polygon_data[1]
                    latitude_data.append(latitude)
                    polygon_coordinates.append(longitude)
            geofence = Polygon(((polygon_coordinates)),srid=4326)
            print("GEOFENCE", geofence)
            newdata = Geofence.objects.create(geoname=geoname,geotype=geotype, description=description,enter_latitude=longitude_data,pos_address=position_add,geofence=geofence)
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['locationCreate'])
            return redirect('geofence')
        return render(request, 'geolocation_form.html')
    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError']) 

#list Geofencing data
def listgeofenceData(request):
    try:
        if request.method == "GET":
            geofencedata = list(Geofence.objects.values())
        return render(request, 'list_geofence_data.html',{ 'geofencedata': geofencedata })
    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])
   
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
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['addDriver']) 
        return render(request, 'adddriver.html')

    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError']) 

#This function used for listing driver. 
def listAddedDriver(request):
    try:
        if request.method == "GET":
            driverData = images_display()
            print(driverData, "=========>>>")

        context={
                "drivers": driverData
                }
        return render(request, 'list_drivers.html',context)
    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError']) 

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
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateDriver']) 
            return render(request,'update_driver.html',{ 'form': pi })

        return render(request,'update_driver.html',{ 'form': pi })

    except Exception as error:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Delete records of driver.
def deleteDriver(request, id):
    try:
        pi = Crmuser.objects.get(pk=id)
        print(pi)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['removeDriver']) 
            return redirect('getdrivers')
        context = {'delete_driver' : pi}
        return render(request, "delete_driver.html", context)
    except Exception as e:
        print(e)
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])


#Generate CSV field vise.
def filedForCSV(request):
    if request.method == "GET":
        files = list(Vehicle.objects.values())
        data= request.POST.getlist('checkedvalue')
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
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

def settings(request):
    return render(request, 'settings.html')

def VCU(request):
    return render(request, 'VCU.html')

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


def battery_pack_menu(request):

    res={"battery_data": [],"filter_data":[], 'batteries':[] , 'session_filter_data':[]}
    demo = BatteryDetail.objects.all()
    
    try:
        charging_status = request.GET.get('charging_status')
        voltage = request.GET.get('battery_pack_nominal_voltage')
        charge_capacity = request.GET.get('battery_pack_nominal_charge_capacity')
        battery_type = request.GET.get('bms_type')
         
        filters = {}
        for key, value in request.GET.items():
            if value != '' and key != "battery_serial_num" :
                filters[key] = value

        if(filters):
            request.session['battery_session_data'] = filters
        favs = request.session.get('battery_session_data')
        res['filter_filed'] = favs is not {} and favs or []
        filters_data = BatteryDetail.objects.filter(**filters).values()
        res['filter_data'] = filters_data


        getData=str(request.get_full_path()) 
        if("battery_serial_num" in getData):
            getData = getData.split("battery_serial_num=")[1]
            filter_battery =  list(BatteryDetail.objects.filter(battery_serial_num=getData).values())
            res['battery_data']=filter_battery
            
            for data in filter_battery:

                if(data["charging_status"] == "FULL CHARGE"):
                    res['battery_data'][0]["charging_status"]="100%"
                elif(data["charging_status"] == "HALF CHARGE"):
                    res['battery_data'][0]["charging_status"]="70%"
                elif(data["charging_status"] == "INITIAL"):
                    res['battery_data'][0]["charging_status"]="50%"
                else:
                    res['battery_data'][0]["charging_status"]="40%"
                      
        context = res
        return render(request, "battery_pack.html",context)
    except Exception as e:
        return render(request, "battery_pack.html")

#Not using now. 
def battery_pack_sub_menu(request):
    query = request.GET.get('q')
    res={"battery_data": [],"filter_data":[]}
    try:
        getData=str(request.get_full_path())
        if("battery_id" in getData):
            getData = getData.split("battery_id=")[1]
            filter_battery =  list(BatteryDetail.objects.filter(battery_serial_num=getData).values())
            res['filter_data']=filter_battery

            for data in filter_battery:

                if(data["charging_status"] == "FULL CHARGE"):
                    res['filter_data'][0]["charging_status"]="100%"
                elif(data["charging_status"] == "HALF CHARGE"):
                     res['filter_data'][0]["charging_status"]="70%"
                elif(data["charging_status"] == "INITIAL"):
                     res['filter_data'][0]["charging_status"]="50%"
                else:
                    res['filter_data'][0]["charging_status"]="40%"
     
        new_arr=[]
        if request.method == "GET":
            battery_data = list(BatteryDetail.objects.values())
            getData=str(request.get_full_path())
            if("battery_id" not in getData):
                for data in battery_data:
                    new_res={}
                    if(data["charging_status"] == "FULL CHARGE"):
                        new_res["charging_status"]="100%"
                    elif(data["charging_status"] == "HALF CHARGE"):
                        new_res["charging_status"]="50%"
                    elif(data["charging_status"] == "INITIAL"):
                        new_res["charging_status"]="70%"
                    else:
                        new_res["charging_status"]="40%"
                    new_res["battery_serial_num"]=data["battery_serial_num"]
                    new_res["battery_pack_nominal_voltage"]=data["battery_pack_nominal_voltage"]
                    new_res["battery_pack_nominal_charge_capacity"]=data["battery_pack_nominal_charge_capacity"]
                    print(new_res)
                    new_arr.append(new_res)
                    res['filter_data']=new_arr
                    break
            res['battery_data']=battery_data
        context = res
        return render(request, "battery_submenu_pack.html", context)
    except Exception as e:
        return render(request, "battery_submenu_pack.html", context)