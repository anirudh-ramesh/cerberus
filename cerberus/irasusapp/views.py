""" 
   - This Modules is develop for Registration, Login, Battery Management,
   Microsoft signup functions, Vehicle Management, Geofencing,
   Driver Management, Generate Csv, FleetOwner, FleetOperator.

"""
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
import json
import csv
from django.utils import timezone
from irasusapp.vcu_management import *
# from .mixins import MessageHandler
from .models import Crmuser, BatteryDetail, IotDevices,Vehicle,Geofence, Organisation
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
from common import UserPermission, successAndErrorMessages, sendEmail,permission

from irasusapp.fleet_management import *

format='%Y-%m-%d'


def dashboard(request):
    getUserData=list(Crmuser.objects.filter(email=request.session.get('email')).values())
    context={
        "IsAdmin":False
    }
    newuserPermission=permission(getUserData[0]["user_type"])

    if(len(getUserData) != 0):
        context['IsAdmin']= getUserData[0]["is_admin"]
        data=UserPermission(request,getUserData[0]["is_admin"])
        context['UserPermission']=data
        context['email']=request.session.get('email')
        context["newuserPermission"]=newuserPermission
    return render(request,'dashboard.html',context)

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
        password = request.POST.get('password')
        crmuser = Crmuser.get_user_by_email(email)
        if crmuser:
            flag = check_password(password,crmuser.password)
            if flag:
                request.session["email"]=email
                getUserData=list(Crmuser.objects.filter(email=email).values())
                if(len(getUserData) !=0):
                   request.session["IsAdmin"]= getUserData[0]["is_admin"]
                   request.session["user_type"]= getUserData[0]["user_type"]
                   newuserPermission=permission(getUserData[0]["user_type"])
                userPermission=UserPermission(request,request.session.get("IsAdmin"))

                return render(request,'dashboard.html',{'email':email,"IsAdmin": getUserData[0]["is_admin"] ,'UserPermission':userPermission,"newuserPermission":newuserPermission})     
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
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    getOwnerList=list(FleetOwner.objects.all())
    try:
        serial_num = request.POST.get('battery_serial_num')
        if BatteryDetail.objects.filter(battery_serial_num=serial_num).exists():
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['alreadyAddedBattery'])
            return render(request,'add_battery_details.html',{"getOwnerList":getOwnerList,"IsAdmin": request.session.get('IsAdmin'),"newuserPermission":newuserPermission,"userPermission":userPermission})
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
                    battery_pack_capacity = request.POST.get('battery_pack_capacity'),
                    charging_status = request.POST.get('charging_status'),
                    created_by=request.session.get("user_type"),
                    created_id=request.session.get("email")
                )
                formData.save()
                messages.add_message(request, messages.INFO, successAndErrorMessages()['addBattery'])
        return render(request,'add_battery_details.html',{"getOwnerList":getOwnerList,"IsAdmin": request.session.get('IsAdmin'),'UserPermission':userPermission, "ActiveBattery":BatteryDetail.objects.filter(status="IN_VEHICLE").count()+BatteryDetail.objects.filter(status="IN_SWAP_STATION").count(),"DamagedBattery":BatteryDetail.objects.filter(status="DAMAGED").count(),"inActiveBattery":BatteryDetail.objects.filter(status="IDEL").count(),"newuserPermission":newuserPermission })
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Listing of battery details table.
def getBatteryDetails(request):
    cahis_id=""
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    assigned_vehicle = request.get_full_path()
    parse.urlsplit(assigned_vehicle)
    parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
    dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
      
    # if(dictinary_obj.get("cahis_id")):
    #     if(request.session.get("IsAdmin")):
    #         vehicle_data = list(Vehicle.objects.values())
    #     else:
    #         vehicle_data = list(Vehicle.objects.filter(assigned_to_id=request.session.get("email")).values())

    #     return render(request, 'battery_details.html', {'vehicle_data':vehicle_data ,"IsAdmin":request.session.get("IsAdmin"),"ActiveBattery":BatteryDetail.objects.filter(status="in_vehicle").count()+BatteryDetail.objects.filter(status="in_swap_station").count(),"DamagedBattery":BatteryDetail.objects.filter(status="damaged").count(),"inActiveBattery":BatteryDetail.objects.filter(status="idel").count(),'UserPermission':userPermission})

    try:
        if request.method == "GET":
            if(request.session.get("IsAdmin")):
                data = list(BatteryDetail.objects.values())
                cahis_id = str(request.get_full_path()).split("=").pop()
            elif(request.session.get("user_type") in successAndErrorMessages()["fleetType"]):
                data=list(BatteryDetail.objects.filter(assigned_owner=request.session.get("email")).values())
                cahis_id = str(request.get_full_path()).split("=").pop()
                if("FleetOperator" == request.session.get("user_type")):
                    data=list(BatteryDetail.objects.filter(assigned_operator=request.session.get("email")).values())
            else:
                getVehicleData=list(Vehicle.objects.filter(assigned_to_id=request.session.get("email")).values())
                data=[]
                if(len(getVehicleData) != 0):
                    data = list(BatteryDetail.objects.filter(vehicle_assign_id=getVehicleData[0]["chasis_number"]).values())
                    cahis_id = str(request.get_full_path()).split("=").pop()

        # ASSIGNED BATTERY TO VEHICLE
        if "AssignToVehicle" in request.get_full_path():
            vehicle_id = str(request.get_full_path()).split("?").pop()
            cahis_id = vehicle_id.split('&')[0].split("=")[1]
            battery_serial_id = vehicle_id.split('&')[1].split("=")[1]
    
            #IF BATTERY IS ALREADY ASSINGED
            data = list(BatteryDetail.objects.filter(battery_serial_num=battery_serial_id).values())
            if(data[0]["is_assigned"]):
                messages.add_message(request, messages.WARNING, successAndErrorMessages()['addBatteryError'])
                return redirect('data')

            for x in data:
                vehicleName = list(Vehicle.objects.filter(chasis_number=cahis_id).values())
                BatteryDetail.objects.filter(pk=x['battery_serial_num']).update(vehicle_assign_id=str(cahis_id), is_assigned=True)
                sendEmail(request, "Battery Assigned To Vehicle", f"{battery_serial_id} Battery is Assigned To The Vehicle {vehicleName[0]['vehicle_model_name']}")
            return redirect('data')
        context = { 'battery_data': data,"cahis_id": cahis_id, "IsAdmin":request.session.get("IsAdmin") ,"ActiveBattery":BatteryDetail.objects.filter(status="IN_VEHICLE").count()+BatteryDetail.objects.filter(status="IN_SWAP_STATION").count(),"DamagedBattery":BatteryDetail.objects.filter(status="DAMAGED").count(),"inActiveBattery":BatteryDetail.objects.filter(status="IDEL").count(),"newuserPermission":newuserPermission }
        context['UserPermission']=userPermission  

        return render(request, 'battery_details.html',context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#This Function Will Update_Battery_details/Edit
def updateBatteryDetails(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    getOwnerList=list(FleetOwner.objects.all().values())

    try:
        newData=[]
        battery_data = BatteryDetail.objects.filter(battery_serial_num=id).values()
        for data in getOwnerList:
            if(data.get('email') ==battery_data[0]["assigned_owner"]):
                newData.insert(0,data)
            else:
                newData.append(data) 
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
            battery_pack_capacity = request.POST.get('battery_pack_capacity')
            charging_status = request.POST.get('charging_status')

            BatteryDetail.objects.filter(battery_serial_num=id).update(
            model_name=model_name,battery_serial_num=battery_serial_num,battery_type=battery_type,bms_type=bms_type,
            iot_type=iot_type,iot_imei_number=iot_imei_number,sim_number=sim_number,warrenty_start_date=warrenty_start_date,
            warrenty_duration=warrenty_duration,assigned_owner=assigned_owner,status=status,
            battery_cell_chemistry=battery_cell_chemistry,battery_pack_nominal_voltage=battery_pack_nominal_voltage,
            battery_pack_capacity=battery_pack_capacity,
            charging_status=charging_status
            )
            battery_data = [{
                'model_name':model_name,
                'battery_serial_num':battery_serial_num,'battery_type': battery_type,'bms_type': bms_type,
                'iot_type': iot_type,'iot_imei_number': iot_imei_number,'sim_number': sim_number,'warrenty_start_date': warrenty_start_date,
                'warrenty_duration': warrenty_duration,'assigned_owner': assigned_owner,'status': status,
                'battery_cell_chemistry': battery_cell_chemistry,'battery_pack_nominal_voltage': battery_pack_nominal_voltage,
                'battery_pack_capacity' : battery_pack_capacity,
                'charging_status': charging_status
                }]
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateBatteryDetails'])
            return render(request,'update_battery_details.html', {"getOwnerList":newData, "newuserPermission":newuserPermission,'form': battery_data, "IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

        battery_data = list(BatteryDetail.objects.filter(battery_serial_num=id).values())
        return render(request,'update_battery_details.html',{"getOwnerList":newData,"newuserPermission":newuserPermission,'form': battery_data, "IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

def activeBatteryDetails(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            status = "IN_SWAP_STATION"
            invehicle= "IN_VEHICLE"
            inswapStationactiveBattery = list(BatteryDetail.objects.values_list('status').values().filter(status=status))
            inVehicleactiveBattery = list(BatteryDetail.objects.values_list('status').values().filter(status=invehicle))
            total = inswapStationactiveBattery + inVehicleactiveBattery

        context= {
            'UserPermission':userPermission,
            'activeBatteries' : total,
            "IsAdmin":request.session.get("IsAdmin"),
            "newuserPermission":newuserPermission
        }
        return render(request, 'active_battery_details.html',context)
    except Exception as e:
        print(e)

def inactiveBatteryDetails(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            status = "IDEL"
            inActiveBattery = list(BatteryDetail.objects.values_list('status').values().filter(status=status))
            total = inActiveBattery

        context= {
            'UserPermission':userPermission,
            'inactiveBatteries' : total,
            "IsAdmin":request.session.get("IsAdmin"),
            "newuserPermission":newuserPermission
        }
        return render(request, 'inactive_battery_details.html',context)
    except Exception as e:
        print(e)


def damagedBatteryDetails(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            status = "DAMAGED"
            damagedBattery = list(BatteryDetail.objects.values_list('status').values().filter(status=status))

        context= {
            'UserPermission':userPermission,
            'damageBatteries' : damagedBattery,
            "IsAdmin":request.session.get("IsAdmin"),
            "newuserPermission":newuserPermission

        }
        return render(request, 'damaged_battery.html',context)
    except Exception as e:
        print(e)

#Delete records from Battery table.
def deleteRecord(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        print(id)
        pi = BatteryDetail.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeBatteryDetails'])
            return redirect('data')
        context = {'item': pi,"IsAdmin":request.session.get("IsAdmin"),} 
        context['UserPermission']=userPermission,
        context["newuserPermission"]=newuserPermission

        return render(request, "delete_battery_data.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


def addIotDevice(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        iot_imei_number = request.POST.get('imei_number')
        if IotDevices.objects.filter(imei_number = iot_imei_number):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['alreadyAdded'])
            return render(request,'add_IOT_devices.html',{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})
        else:
            if request.method == "POST":
                formData = IotDevices.objects.create(
                    imei_number = request.POST.get('imei_number'),
                    hardware_version = request.POST.get('hardware_version'),
                    firmware_version = request.POST.get('firmware_version'),
                    status = request.POST.get('status'),

                )
                formData.save()
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['deivceAdded'])
            return render(request,'add_IOT_devices.html',{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


def getActiveAnddeactiveIotBystatus(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    assigned_vehicle = request.get_full_path()
    parse.urlsplit(assigned_vehicle)
    parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
    dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
    if(request.session.get("IsAdmin") == False):
        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['AuthError'])
        return redirect('home')
    if request.method == "GET":
        data = list(IotDevices.objects.filter(status=dictinary_obj.get('action')).values())
    contex = {'iot_station_data' : data is not [] and data or None,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission, "action":dictinary_obj.get('action'),"newuserPermission":newuserPermission }
    return render(request, 'iot_list_by_status.html',contex)



def listIotDevice(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            iotdevicedata = list(IotDevices.objects.values())
            batteryWithIotDevice = iotDevice(iotdevicedata)
            if(request.session.get("IsAdmin")):
                #REMOVE BATTERY TO IOT-DEVICE
                if ("action" in request.get_full_path()):
                    get_full_path = str(request.get_full_path()).split("?").pop()
                    imei_number =get_full_path.split("&action")[0].split("=")[1]
                    batteryRemovedFromIot = BatteryDetail.objects.filter(iot_imei_number_id=imei_number).values()
                    sendEmail(request, "Iot Device", f"{batteryRemovedFromIot[0]['battery_serial_num']} Battery is Removed From The Iot Device {imei_number}")
                    batteryRemovedFromIot.update(iot_imei_number_id=None)        
                    messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeDeviceFromBattery'])
                    return redirect('listdevice')
        return render(request, 'list_IOT_devices.html',{"newuserPermission":newuserPermission, 'iot_device_data': batteryWithIotDevice,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,"Activeiot": IotDevices.objects.filter(status="Active").values().count(),"InActiveiot": IotDevices.objects.filter(status="Inactive").values().count()})
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

def updateIOTDevice(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        update_iot_device = list(IotDevices.objects.filter(imei_number=id).values())
        if request.method == "POST":
            imei_number = request.POST.get('imei_number')
            hardware_version = request.POST.get('hardware_version')
            firmware_version = request.POST.get('firmware_version')
            
            IotDevices.objects.filter(imei_number=id).update(
                imei_number=imei_number, hardware_version=hardware_version,
                firmware_version=firmware_version,
                status=request.POST.get('status')
            )
            update_iot_device = [{
                'imei_number':imei_number,
                'hardware_version':hardware_version,
                'firmware_version': firmware_version,
                "status":request.POST.get('status')

            }]
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['deviceUpdate'])
            return render(request,'update_IOT_device.html',{"newuserPermission":newuserPermission,'update_IOT_data': update_iot_device,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission })

        update_iot_device = list(IotDevices.objects.filter(imei_number=id).values())
        return render(request,'update_IOT_device.html',{"newuserPermission":newuserPermission,'update_IOT_data': update_iot_device,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission })
    except Exception as error:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

def deleteIOTDeviceRecord(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        pi = IotDevices.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeDevice'])
            return redirect('listdevice')
        context={"newuserPermission":newuserPermission,"iot_device": pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission }
        return render(request, 'delete_iot_device.html', context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

def assignedIotDeviceToBattery(request):
    try:
        userPermission=UserPermission(request,request.session.get("IsAdmin"))
        newuserPermission=permission(request.session.get("user_type"))

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
                        BatteryDetail.objects.filter(pk=battery_serial_number).update(iot_imei_number_id=imei_number)
                        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['deviceAddToBattery'])
                        sendEmail(request, "Iot Device", f"{battery_serial_number} Battery is Assiged To The Iot Device {imei_number}")
                        return redirect('iotdevice')
        context = {"newuserPermission":newuserPermission, 'assinged_iot_device': obj,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission }
        return render(request,'assigned_iot_device_to_battery.html', context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

def assignedVehicleToDriver(request):
    try:
        userPermission=UserPermission(request,request.session.get("IsAdmin"))
        obj = Vehicle.objects.all()

        #ASSIGN VEHICLE TO DRIVER
        if request.method == "POST":
            assigned_vehicle = request.get_full_path()
            if("action" in assigned_vehicle and "add" in assigned_vehicle):

                parse.urlsplit(assigned_vehicle)
                parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
                dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
                chasis_number = request.POST.get('name_of_select')
                already_assign = list(Crmuser.objects.filter(email = dictinary_obj['email']).values())
                for x in already_assign:
                    
                    if x['vehicle_assigned_id'] is not None:
                        messages.add_message(request, messages.WARNING, successAndErrorMessages()['alreadyVehicleUser'])
                        return redirect('drivervehicle')
                    else:
                        Crmuser.objects.filter(pk=dictinary_obj['email']).update(vehicle_assigned_id = chasis_number)
                        
                        messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['addVehicleToUser'])
                        sendEmail(request, "Iot Device", f"{dictinary_obj['email']} Battery is Assiged To The Iot Device {chasis_number}")
                        return redirect('drivervehicle')
        context = { 'assinged_vehicle': obj,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission }
        return render(request,'assigned_vehicle_to_driver.html', context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

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
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    getFleetId=list(FleetOperator.objects.filter(created_id=request.session.get("email")).values())

    try:
        chasis_number = request.POST.get('chasis_number')
        if Vehicle.objects.filter(chasis_number=chasis_number):
            print("IN THIS CONDITION")
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['alreadyAddedVehicle'])
            return render(request,'add_vehicle_details.html',{"get_FleetId":getFleetId,"newuserPermission":newuserPermission,"IsAdmin": request.session.get('IsAdmin'),'UserPermission':userPermission})

        else:
            if request.method == "POST":
                formData = Vehicle.objects.create(
                    vehicle_model_name = request.POST.get('vehicle_model_name'),
                    chasis_number = request.POST.get('chasis_number'),
                    configuration = request.POST.get('configuration'),
                    vehicle_choice = request.POST.get('vehicle_choice'),
                    vehicle_warrenty_start_date = datetime.strptime(request.POST.get('vehicle_warrenty_start_date'), format),
                    vehicle_warrenty_end_date = datetime.strptime(request.POST.get('vehicle_warrenty_end_date'), format),
                    assigned_operator = request.POST.get('assigned_operator'),
                    insurance_start_date = datetime.strptime(request.POST.get('insurance_start_date'), format),
                    insurance_end_date = datetime.strptime(request.POST.get('insurance_start_date'), format),
                    vehicle_status = request.POST.get('vehicle_status')
                )
                formData.save()
                Vehicle.objects.filter(chasis_number=request.POST.get('chasis_number')).update(created_by=request.session.get("user_type"),created_id=request.session.get("email"))
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['addVehicle'])
            return render(request,'add_vehicle_details.html',{"get_FleetId":getFleetId,"newuserPermission":newuserPermission,'UserPermission':userPermission,"ActiveVehicle":Vehicle.objects.filter(vehicle_status="Active").count(),"InactiveVehicle":Vehicle.objects.filter(vehicle_status="Inactive").count()})
    except Exception as e:
        return messages.warning(request, messages.ERROR, successAndErrorMessages()['internalError'])

#Listing of vehile.
def getVehicleDetails(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    parse.urlsplit(request.get_full_path())
    parse.parse_qs(parse.urlsplit(request.get_full_path()).query)
    dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(request.get_full_path()).query))

    try:
        assigned_to_user = str(request.get_full_path()).split("?").pop()
        serial_number = assigned_to_user.split("=").pop()
        email_id = assigned_to_user.split("=").pop()
        if(request.session.get("IsAdmin")):
            vehicle_data = list(Vehicle.objects.values())
        elif(request.session.get("user_type") in successAndErrorMessages()["fleetType"]):
            vehicle_data=list(Vehicle.objects.filter(created_id=request.session.get("email")).values())
            if("FleetOperator" == request.session.get("user_type")):
                vehicle_data=list(Vehicle.objects.filter(assigned_operator=request.session.get("email")).values())
            if("User" == request.session.get("user_type") or "Driver" == request.session.get("user_type")):
                vehicle_data=list(Crmuser.objects.filter(email=request.session.get("email")).values())
                vehicle_data=list(Vehicle.objects.filter(chasis_number=vehicle_data[0]["vehicle_assigned_id"]))
        else:
            vehicle_data = list(Vehicle.objects.filter(assigned_to_id=request.session.get("email")).values())
                
        #Assigned Vehicle To Organisation
        if("AssignedToOrganisation" in request.get_full_path()):
            assigned_to_user = str(request.get_full_path()).split("?").pop()
            serial_number = assigned_to_user.split("&")[0].split("=")[1]
            assignedToOrg = list(Organisation.objects.filter(serial_number=serial_number).values())
            chasis_number = assigned_to_user.split('&')[1].split("=")[2]
            vehicleName = list(Vehicle.objects.filter(chasis_number=chasis_number).values())

            if(dictinary_obj.get('serial_number') == "/getvehicle"):
                if(request.session.get("IsAdmin")):
                    data = Organisation.objects.values()
                return redirect('user_management:listorg')

            if(assigned_to_user):
                assignedVehicleToOrganisation(serial_number,chasis_number)
                sendEmail(request, "Vehicle Assigned", f"{vehicleName[0]['vehicle_model_name']} Vehicle is Assigned To The Organisation {assignedToOrg[0]['organisation_name']}")
                return redirect('user_management:listorg')

        #Assigned Vehicle To User
        if("AssignedToUser" in request.get_full_path()):
            email_id = assigned_to_user.split("&")[0].split("=")[1]
            vehicle_id = assigned_to_user.split('&')[1].split("=")[2]
            vehicle_data= list(Vehicle.objects.filter(chasis_number = vehicle_id).values())

            #ALREADY ASSINGED VEHICLE
            if Vehicle.objects.filter(assigned_to_id = email_id).values().count():
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['alreadyVehicleUser'])
                return redirect('getvehicle')


            if(dictinary_obj.get('assigned_to_id') == "/getvehicle"):
                if(request.session.get("IsAdmin")):
                    data = list(Crmuser.objects.values())
                else:
                    data=list(Crmuser.objects.filter(email=request.session.get("email")).values())
                return render(request, 'user_management_templates/get_userdata.html', {"newuserPermission":newuserPermission,'user_data' : data,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

            for x in vehicle_data:
                Vehicle.objects.filter(pk=int(x['chasis_number'])).update(assigned_to_id=str(email_id), vehicle_selected=True)
                sendEmail(request, "Vehicle Assigned", f"{vehicle_data[0]['vehicle_model_name']} Vehicle is Assigned To The User {email_id}")
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['addVehicleToUser'])
                return render(request, 'list_vehicle_details.html', {"newuserPermission":newuserPermission,'vehicle_data':list(Vehicle.objects.values()) , 'email_id': email_id , 'serial_number': serial_number,"IsAdmin":request.session.get("IsAdmin"),"ActiveVehicle":Vehicle.objects.filter(vehicle_status="Active").count(),"InactiveVehicle":Vehicle.objects.filter(vehicle_status="Inactive").count(),'UserPermission':userPermission})
        return render(request, 'list_vehicle_details.html', {"newuserPermission":newuserPermission,'vehicle_data':vehicle_data , 'email_id': email_id , 'serial_number': serial_number,"IsAdmin":request.session.get("IsAdmin"),"ActiveVehicle":Vehicle.objects.filter(vehicle_status="Active").count(),"InactiveVehicle":Vehicle.objects.filter(vehicle_status="Inactive").count(),'UserPermission':userPermission})
    except Exception as e:
        print(e, "========E=============")
        return messages.warning(request, messages.ERROR,successAndErrorMessages()['internalError'])


#This function will Update Vehicle Table.
def updateVehicleDetails(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    getFleetId=list(FleetOperator.objects.filter(created_id=request.session.get("email")).values())


    try:
        newData=[]
        #LIST OF FLEET OPERATOR DROP-DOWN
        update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())
        for data in getFleetId:
            if(data.get('email') == update_vehicle[0]["assigned_operator"]):
                newData.insert(0,data)
            else:
                newData.append(data)    
        

        if request.method == "POST":
            vehicle_model_name = request.POST.get('vehicle_model_name')
            chasis_number = request.POST.get('chasis_number')
            configuration = request.POST.get('configuration')
            vehicle_choice = request.POST.get('vehicle_choice')
            vehicle_warrenty_start_date = datetime.strptime(request.POST.get('vehicle_warrenty_start_date'), format)
            vehicle_warrenty_end_date = datetime.strptime(request.POST.get('vehicle_warrenty_end_date'), format)
            insurance_start_date = datetime.strptime(request.POST.get('insurance_start_date'), format)
            insurance_end_date = datetime.strptime(request.POST.get('insurance_start_date'), format)
            vehicle_status = request.POST.get('vehicle_status')

            Vehicle.objects.filter(chasis_number=id).update(
                vehicle_model_name=vehicle_model_name, chasis_number=chasis_number,
                configuration=configuration,vehicle_choice=vehicle_choice,
                vehicle_warrenty_start_date=vehicle_warrenty_start_date,vehicle_warrenty_end_date=vehicle_warrenty_end_date,
                insurance_start_date=insurance_start_date,
                insurance_end_date=insurance_end_date,vehicle_status=vehicle_status,
                assigned_operator= request.POST.get('assigned_operator')
            )

            update_vehicle = [{
                'vehicle_model_name':vehicle_model_name,
                'chasis_number':chasis_number,'vehicle_choice': vehicle_choice,
                'configuration': configuration,
                'vehicle_warrenty_start_date': vehicle_warrenty_start_date,
                'vehicle_warrenty_end_date': vehicle_warrenty_end_date,'assigned_operator': request.POST.get('assigned_operator'),
                'insurance_start_date': insurance_start_date,
                'insurance_end_date': insurance_end_date, 'vehicle_status':vehicle_status
            }]
            #SELECTED FLEET OPERATOR DROP-DOWN VALUE
            update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())
            for data in getFleetId:
                if(data.get('email') == update_vehicle[0]["assigned_operator"]):
                    newData.insert(0,data)
                else:
                    newData.append(data) 
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateVehicle'])
            return render(request,'update_vehicle.html',{"getFleetId":newData,"newuserPermission":newuserPermission,'update_vehicle_data': update_vehicle,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveVehicle":Vehicle.objects.filter(vehicle_status="Active").count(),"InactiveVehicle":Vehicle.objects.filter(vehicle_status="Inactive").count() })

        update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())
        return render(request,'update_vehicle.html',{"getFleetId":newData,"newuserPermission":newuserPermission,'update_vehicle_data': update_vehicle,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveVehicle":Vehicle.objects.filter(vehicle_status="Active").count(),"InactiveVehicle":Vehicle.objects.filter(vehicle_status="Inactive").count() })
    except Exception as error:
        print(error)
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])

#Delete records from Vehicle table.
def deleteVehicleRecord(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        pi = Vehicle.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeVehicle'])
            return redirect('getvehicle')
        context = {"newuserPermission":newuserPermission,'vehicle_data' : pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission}
        return render(request, "delete_vehicle_data.html", context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeVehicle'])


def activeVehicleDetails(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            status = "Active"
            activeVehicle = list(Vehicle.objects.values_list('vehicle_status').values().filter(vehicle_status=status))
            
        context= {
            'UserPermission':userPermission,
            'activeVehicle' : activeVehicle,
            "IsAdmin":request.session.get("IsAdmin"),
            "newuserPermission":newuserPermission
        }
        return render(request, 'active_vehicle_details.html',context)
    except Exception as e:
        print(e)

def inactiveVehicleDetails(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            status = "Inactive"
            inactiveVehicle = list(Vehicle.objects.values_list('vehicle_status').values().filter(vehicle_status=status))
            
        context= {
            'UserPermission':userPermission,
            'inactiveVehicle' : inactiveVehicle,
            "IsAdmin":request.session.get("IsAdmin"),
            "newuserPermission":newuserPermission

        }
        return render(request, 'inactive_vehicle_details.html',context)
    except Exception as e:
        print(e)

#Assigned BatteryList
def assignedBatteryList(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            data = listAssignedBatteryVehicle(id)

        # Remove battery from vehicle.
        assigned_vehicle = request.get_full_path()
        parse.urlsplit(assigned_vehicle)
        parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
        dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
        if "action" in assigned_vehicle:
                print("HERE")
                data = BatteryDetail.objects.filter(battery_serial_num=dictinary_obj['battery_serial_num']).update(vehicle_assign_id=None, is_assigned=False)
                messages.add_message(request, messages.WARNING, successAndErrorMessages()['batteryRemovefrom'])
                return redirect('getvehicle')

        context = {
                        "newuserPermission":newuserPermission,'assigned_battery_list' : data,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveBattery":BatteryDetail.objects.filter(status="IN_VEHICLE").count()+BatteryDetail.objects.filter(status="IN_SWAP_STATION").count(),"DamagedBattery":BatteryDetail.objects.filter(status="DAMAGED").count(),"inActiveBattery":BatteryDetail.objects.filter(status="IDEL").count()
        }
        return render(request, 'list_assigned_battery.html',context)
    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])


#Assigned vehicle to org
def assignedOrgVehicleList(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        org_vehicle_list = getOrgAssignedVehicle(id)
        newdata=org_vehicle_list
        if(request.session.get('IsAdmin') == False):
            newdata=[]
            for i in org_vehicle_list:
                if (i["email"] == request.session.get('email')):
                        newdata.append(i)

        #Remove vehicle from Organisation  
        assigned_vehicle = request.get_full_path()
        if assigned_vehicle:
            parse.urlsplit(assigned_vehicle)
            parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
            dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
            vehicle_id = dictinary_obj
            assignedToOrg = list(Organisation.objects.filter(serial_number=id).values())
            if vehicle_id:
                vehicleName = list(Vehicle.objects.filter(chasis_number= vehicle_id['chasis_number']).values())
                removeAssignedVehiclefromOrganisation(id,vehicle_id['chasis_number'])
                sendEmail(request, "Vehicle Assigned", f"{vehicleName[0]['vehicle_model_name']} Vehicle is Removed From The Organisation {assignedToOrg[0]['organisation_name']}")
                messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['removeVehicle'])
                return render(request, 'list_organisation_vehicle.html',{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission, 'org_id': id })
                
        return render(request, 'list_organisation_vehicle.html',{"newuserPermission":newuserPermission,'org_vehicle_list': org_vehicle_list,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission, 'org_id': id})
    except Exception as e:
        print(e)
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])

#Assigned vehicle to user
def assignedVehicleToUser(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        user_vehicle =""
        if request.method == "GET":
            user_vehicle = listAssignedVehicleToUser(id)

        #Remove Vehicle from User
        assigned_vehicle = request.get_full_path()
        if ("action" in assigned_vehicle):
            parse.urlsplit(assigned_vehicle)
            parse.parse_qs(parse.urlsplit(assigned_vehicle).query)
            dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(assigned_vehicle).query))
            user_vehicle = removeUserVehicle(False,dictinary_obj['chasis_number'])
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['removeVehiclefromUser'])
            return redirect("user_management:getdata")

        return render(request,'list_assigned_vehicle_to_user.html',{"newuserPermission":newuserPermission,'user_vehicle':user_vehicle,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveBattery":BatteryDetail.objects.filter(status="in_vehicle").count()+BatteryDetail.objects.filter(status="in_swap_station").count(),"DamagedBattery":BatteryDetail.objects.filter(status="damaged").count(),"inActiveBattery":BatteryDetail.objects.filter(status="idel").count()})
    except Exception as e:
       return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError'])

#Create Geofencing Locations.
def addgeofenceVehicles(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

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
                res={}
                res['lat'] = coordinate_data[1]
                res['lng'] = coordinate_data[0]
                longitude_data.append(res)
                longitude = coordinate_data[0]
                latitude = coordinate_data[1]
                location = Point(float(longitude),float(latitude),srid=4326)            
                newdata = Geofence.objects.create(geoname=geoname,geotype=geotype,description=description,enter_latitude=longitude_data,enter_longitude=longitude,pos_address=position_add,location=location)
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
                    res['lng'] = polygon_data[0]
                    longitude_data.append(res)
                    latitude = polygon_data[1]
                    latitude_data.append(latitude)
                    polygon_coordinates.append(longitude)
            geofence = Polygon(((polygon_coordinates)),srid=4326)
            print("GEOFENCE", geofence)
            newdata = Geofence.objects.create(geoname=geoname,geotype=geotype, description=description,enter_latitude=longitude_data,pos_address=position_add,geofence=geofence)
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['locationCreate'])
            return redirect('geofence')
        return render(request, 'geolocation_form.html',{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})
    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError']) 

#list Geofencing data
def listgeofenceData(request):
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            geofencedata = list(Geofence.objects.values())

        return render(request, 'list_geofence_data.html',{"newuserPermission":newuserPermission, 'listgeofencedata': geofencedata ,"IsAdmin":request.session.get("IsAdmin")})
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

def geofenceFilteringData(request, id):
    newuserPermission=permission(request.session.get("user_type"))
    try:
        geofencedata = list(Geofence.objects.filter(pk=id).values())
        context = {
            "newuserPermission":newuserPermission,
            "IsAdmin":request.session.get("IsAdmin"),
            'geofencedata':geofencedata[0]['enter_latitude']
        }
        return render(request, "filter_geofence_data.html",context)
    except Exception as e:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Delete records of Geofence.
def deleteGeofenceData(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
 
    try:
        pi = Geofence.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['removeLocation']) 
            return redirect('listgeofencedata')
        context = {"newuserPermission":newuserPermission,'geofence' : pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission}
        return render(request, "delete_geofence_data.html", context)
    except Exception as e:
        print(e)
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Add driver For Vechicle Module.
def addDriver(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    getFleetId= list(FleetOperator.objects.filter(created_id=request.session.get("email")).values())

    try:
        if request.method == "POST":
            if Crmuser.objects.filter(email=request.POST.get('contact')).exists():
                messages.add_message(request, messages.WARNING,"Driver is already exists") 
                return redirect('addriver')

            username = request.POST.get('username')
            email = request.POST.get('contact')
            newPassword=generatorPassword()
            password = make_password(newPassword)
            user_type =  request.POST.get('user_type')
            assigned_operator = request.POST.get('assigned_operator')
            adhar_proof = request.FILES['adhar_card'].file.read()
            pancard_proof = request.FILES['pan_card'].file.read()
            license_proof = request.FILES['driving_license'].file.read()
            is_active = True

            newdata = Crmuser.objects.create(
                username=username,email=email,user_type=user_type,
                assigned_operator=assigned_operator,
                adhar_proof=adhar_proof,pancard_proof=pancard_proof,
                license_proof=license_proof,is_active=is_active,
                password = password,user_permission= json.dumps(permission("Driver"))
            )
            newdata.save()
            Crmuser.objects.filter(email=request.POST.get('contact')).update(is_admin=False,created_by=request.session.get("user_type"),created_id=request.session.get("email"))

            messages.add_message(request, messages.SUCCESS,f"Driver create suceessfully your one time password is '{newPassword}' ") 
        return render(request, 'adddriver.html', { "get_Fleet_Operator": getFleetId, "newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

    except Exception as e:
        return messages.add_message(request, messages.ERROR, successAndErrorMessages()['internalError']) 

#This function used for listing driver. 
def listAddedDriver(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    try:
        if request.method == "GET":
            newData=[]
            if(request.session.get("IsAdmin")):
                driverData = images_display(True)
                if(len(driverData) !=0):
                    for i in driverData:
                        vehicle_data = list(Vehicle.objects.filter(chasis_number=i['vehicle_assigned_id']).values())
                        if(len(vehicle_data) != 0 and vehicle_data[0]['vehicle_model_name'] != None):
                            i["vehicle_name"] = vehicle_data[0]['vehicle_model_name']
                        newData.append(i)
            elif(request.session.get("user_type") in successAndErrorMessages()["fleetType"]):
                driverData = images_display(request.session.get("email"))
                if(len(driverData) !=0):
                      for i in driverData:
                        vehicle_data = list(Vehicle.objects.filter(chasis_number=i['vehicle_assigned_id']).values())
                        if(len(vehicle_data) != 0 and vehicle_data[0]['vehicle_model_name'] != None):
                            i["vehicle_name"] = vehicle_data[0]['vehicle_model_name']
                        newData.append(i)
            else:
                driverData = images_display(request.session.get("email"))
                if(len(driverData) !=0):
                    for i in driverData:
                        vehicle_data = list(Vehicle.objects.filter(chasis_number=i['vehicle_assigned_id']).values())
                        if(len(vehicle_data) != 0 and vehicle_data[0]['vehicle_model_name'] != None):
                            i["vehicle_name"] = vehicle_data[0]['vehicle_model_name']
                        newData.append(i)
         
            #REMOVE VEHICLE FROM DRIVER
            get_full_path = request.get_full_path()
            if("action" in get_full_path and "remove" in get_full_path):
                parse.urlsplit(get_full_path)
                parse.parse_qs(parse.urlsplit(get_full_path).query)
                dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(get_full_path).query))
                batteryRemovedFromIot = Crmuser.objects.filter(email= dictinary_obj['email']).values()
                # sendEmail(request, "Remove Vehicle From Driver", f"{batteryRemovedFromIot[0]['battery_serial_num']} Vehicle is Removed From The Driver {dictinary_obj['email']}")
                batteryRemovedFromIot.update(vehicle_assigned_id=None)        
                messages.add_message(request, messages.WARNING, successAndErrorMessages()['vehicleRemovedFromDriver'])
                return redirect('getdrivers')
        context={
                "newuserPermission":newuserPermission,"drivers": newData ,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission,
                }
        return render(request, 'list_drivers.html',context)
    except Exception as e:
        print(e)
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError']) 

# This function will Update Driver
def updateDriver(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    getFleetId=list(FleetOperator.objects.filter(created_id=request.session.get("email")).values())
    
    try:
        newData=[]            
        if request.method == 'GET':    
            pi =list(Crmuser.objects.filter(pk=id).values())
            pi[0]["email"]=pi[0]["email"]
            pi[0]["username"]=pi[0]["username"]
            pi[0]["user_type"]=pi[0]["user_type"]
            pi[0]["is_active"]=pi[0]["is_active"]
            pi[0]["adhar_proof"]=b64encode(pi[0]['adhar_proof']).decode("utf-8")
            pi[0]["pancard_proof"]=b64encode(pi[0]['pancard_proof']).decode("utf-8")
            pi[0]["license_proof"]=b64encode(pi[0]['license_proof']).decode("utf-8")
            pi[0]['assigned_operator']=pi[0]['assigned_operator']

            #LIST OF FLEET OPERATOR DROP-DOWN
            update_vehicle = list(Crmuser.objects.filter(email=id).values())
            for data in getFleetId:
                if(data.get('email') == update_vehicle[0]['assigned_operator']):
                    newData.insert(0,data)
                else:
                    newData.append(data)
        
        
        if request.method == 'POST':      
            username = request.POST.get('username')
            email = request.POST.get('email')
            isactive = request.POST.get('is_active')
            user_type = request.POST.get('user_type')
            assigned_operator = request.POST['assigned_operator']
            
            if isactive == 'on':
                isactive = True
            else:
                isactive = False

            Crmuser.objects.filter(pk=id).update(username=username,email=email,is_active=isactive,user_type=user_type,assigned_operator=assigned_operator,updated_at = timezone.now())     
            pi =list(Crmuser.objects.filter(email=email).values())
            pi[0]["email"]=pi[0]["email"]
            pi[0]["username"]=pi[0]["username"]
            pi[0]["user_type"]=pi[0]["user_type"]
            pi[0]["is_active"]=pi[0]["is_active"]
            pi[0]["adhar_proof"]=b64encode(pi[0]['adhar_proof']).decode("utf-8")
            pi[0]["pancard_proof"]=b64encode(pi[0]['pancard_proof']).decode("utf-8")
            pi[0]["license_proof"]=b64encode(pi[0]['license_proof']).decode("utf-8")
            pi[0]['assigned_operator']=pi[0]['assigned_operator']

            #SELECTED FLEET OPERATOR DROP-DOWN VALUE
            update_vehicle = list(Crmuser.objects.filter(email=id).values())
            for data in getFleetId:
                if(data.get('email') == update_vehicle[0]['assigned_operator']):
                    newData.insert(0,data)
                else:
                    newData.append(data)

            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['updateDriver'])
            return render(request,'update_driver.html',{"get_Fleet_Operator": newData, "newuserPermission":newuserPermission, 'form': pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission })

        return render(request,'update_driver.html',{"get_Fleet_Operator": newData, "newuserPermission":newuserPermission, 'form': pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

    except Exception as error:
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])

#Delete records of driver.
def deleteDriver(request, id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
 
    try:
        pi = Crmuser.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['removeDriver']) 
            return redirect('getdrivers')
        context = {"newuserPermission":newuserPermission,'delete_driver' : pi,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission}
        return render(request, "delete_driver.html", context)
    except Exception as e:
        print(e)
        return messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])


#Generate CSV field vise.
def filedForCSV(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if request.method == "GET":
        list(Vehicle.objects.values())
        request.POST.getlist('checkedvalue')
    return render(request, 'generate_csv.html', {"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

#Exporting CSV.
def exportCSV(request):
    newuserPermission=permission(request.session.get("user_type"))

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

def VCU(request):
    newuserPermission=permission(request.session.get("user_type"))

    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    return render(request, 'VCU.html',{"newuserPermission":newuserPermission, "IsAdmin":request.session.get("IsAdmin"),'UserPermission':userPermission})

#Open swap-station doors.
def swapSatationDoors(request):
    newuserPermission=permission(request.session.get("user_type"))

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

    return render(request, "swap_station_door.html", {"newuserPermission":newuserPermission,'response': response,"IsAdmin":request.session.get("IsAdmin")})


def battery_pack_menu(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    res={"battery_data": [],"filter_data":[], 'batteries':[] , 'session_filter_data':[]}
    newuserPermission=permission(request.session.get("user_type"))
   
    try:
        # charging_status = request.GET.get('charging_status')
        # voltage = request.GET.get('battery_pack_nominal_voltage')
        # charge_capacity = request.GET.get('battery_pack_nominal_charge_capacity')
        # battery_type = request.GET.get('bms_type')
         
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
        if(request.session.get("IsAdmin") == False):
            getVehicleData=list(Vehicle.objects.filter(assigned_to_id=request.session.get("email")).values())
            print(getVehicleData,"==.../.")
            if(len(getVehicleData) != 0):
                filters_data = list(BatteryDetail.objects.filter(vehicle_assign_id=getVehicleData[0]["chasis_number"]).values())
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
                      
        res["IsAdmin"]=request.session.get("IsAdmin")
        res['UserPermission']=userPermission
        context = res
        return render(request, "battery_pack.html",context)
    except Exception as e:
        return render(request, "battery_pack.html",{"newuserPermission":newuserPermission,"IsAdmin":request.session.get("IsAdmin")})

#Not using now. 
def battery_pack_sub_menu(request):
    newuserPermission=permission(request.session.get("user_type"))

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
                    new_res["battery_pack_capacity"]=data["battery_pack_capacity"]
                    print(new_res)
                    new_arr.append(new_res)
                    res['filter_data']=new_arr
                    break
            res['battery_data']=battery_data
            res["IsAdmin"]=request.session.get("IsAdmin")
            res["newuserPermission"]=newuserPermission,

        context = res
        return render(request, "battery_submenu_pack.html", context)
    except Exception as e:
        res["IsAdmin"]=request.session.get("IsAdmin")
        res["newuserPermission"]=newuserPermission,

        return render(request, "battery_submenu_pack.html", res)

def irameData(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    return render(request, "iframe_data.html",{"newuserPermission":newuserPermission,'id':id,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

   ####  fleet owner ####

# create fleet owner
def createFleetManagement(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if request.method == "GET":
        return render(request, "fleet_owner_and_fleet_operator/add_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    if request.method == "POST":
        data=createFleetOwner(request)

        if(data == True):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['fleetownerExists'])
            return render(request, "fleet_owner_and_fleet_operator/add_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

        elif(data == False):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
            return render(request, "fleet_owner_and_fleet_operator/add_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

        else:
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['fleetownerCreate'])
            return render(request, "fleet_owner_and_fleet_operator/add_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

## update fleet owner data
def updateFleetManagement(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    data=updateFleetOwner(request,id)
    if request.method == "GET":
        return render(request, "fleet_owner_and_fleet_operator/update_fleet_owner.html",{"newuserPermission":newuserPermission,'data': data,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    if(data == False and len(data) != 0):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/update_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            data=updateFleetOwner(request,id)
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['fleetownerupdate'])
            return render(request, "fleet_owner_and_fleet_operator/update_fleet_owner.html",{"newuserPermission":newuserPermission,'data' : data ,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})
        else:

            return render(request, "fleet_owner_and_fleet_operator/update_fleet_owner.html",{"newuserPermission":newuserPermission,'data' : data,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})


## list fleet operato data
def listFleetManagement(request):
    data=listFleetOwner(request)
    newuserPermission=permission(request.session.get("user_type"))

    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    if(len(data) == 0) :
        return render(request, "fleet_owner_and_fleet_operator/list_fleet_owner.html",{"newuserPermission":newuserPermission,'data':data, 'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveFleetOperator":FleetOwner.objects.filter(status=True).count(),"InactiveFleetOperator":FleetOwner.objects.filter(status=False).count()})

    elif(data == False):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/list_fleet_owner.html",{"newuserPermission":newuserPermission,'data':data, 'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveFleetOperator":FleetOwner.objects.filter(status=True).count(),"InactiveFleetOperator":FleetOwner.objects.filter(status=False).count()})

    else:
        return render(request, "fleet_owner_and_fleet_operator/list_fleet_owner.html",{"newuserPermission":newuserPermission,'data':data, 'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveFleetOwner":FleetOwner.objects.filter(status=True).count(),"InactiveFleetOwner":FleetOwner.objects.filter(status=False).count()})

## delete fleet Owner data
def deleteFleetManagemant(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    data=True
    if request.method == "GET": 
        data=list(deleteFleetOwner(request,id))[0]
    if(data == False):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/delete_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            data=deleteFleetOwner(request,id)
            return redirect("listfleetowner")
        else:
            return render(request, "fleet_owner_and_fleet_operator/delete_fleet_owner.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"data":data})


## get active and deactive fleet owner
def getActiveandInactiveFleetOwner(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    data=getActiveAndInactiveFleetOwner(request)
    if(data != False and len(data) == 0):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['dataNotFound'])
        return render(request, "fleet_owner_and_fleet_operator/active_and_inactive_fleet_owner.html",{"newuserPermission":newuserPermission, "data": [],'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        return render(request, "fleet_owner_and_fleet_operator/active_and_inactive_fleet_owner.html",{"newuserPermission":newuserPermission, "data": list(data),'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"action": parseQuerySting(request)["action"]})


## create fleet operato data
def createFleetOperatorupnderFleetOwner(request):
    data=createFleetOperator(request)
    newuserPermission=permission(request.session.get("user_type"))
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    if request.method == "GET":
        return render(request, "fleet_owner_and_fleet_operator/add_fleet_operatore.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    if(data == True):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['fleetoperatorExists'])
        return render(request, "fleet_owner_and_fleet_operator/add_fleet_operatore.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    elif(data == False):

        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/add_fleet_operatore.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['fleetoperatorCreate'])

            return render(request, "fleet_owner_and_fleet_operator/add_fleet_operatore.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

## update fleet operato data
def updateFleetOperatorupnderFleetOwner(request,id):
    data=updateFleetOperator(request,id)
    newuserPermission=permission(request.session.get("user_type"))
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    getBattery=list(BatteryDetail.objects.filter(assigned_owner=request.session.get("email")).values())

    if(request.session.get("IsAdmin")):
        getBattery=list(BatteryDetail.objects.all())
    if(data == False and len(data) != 0) :
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/update_fleet_operator.html",{"getBattery":getBattery,"newuserPermission":newuserPermission,'data' : data ,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            data=updateFleetOperator(request,id)
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['fleetoperatorupdate'])
            return render(request, "fleet_owner_and_fleet_operator/update_fleet_operator.html",{"getBattery":getBattery,"newuserPermission":newuserPermission,'data' : data ,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})
        else:
            return render(request, "fleet_owner_and_fleet_operator/update_fleet_operator.html",{"getBattery":getBattery,"newuserPermission":newuserPermission,'data' : data ,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

## delete fleet operato data
def deleteFleetOperatorupnderFleetOwner(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    data=True
    if request.method == "GET": 
        data=list(deleteFleetOperator(request,id))[0]
    if(data == False):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/delete_fleet_operator.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            data=deleteFleetOperator(request,id)
            return redirect("listfleetoperator")
        else:
            return render(request, "fleet_owner_and_fleet_operator/delete_fleet_operator.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"data":data})

## list fleet operato data
def listFleetOperatorupnderFleetOwner(request):
    data=listFleetOperator(request)
    newuserPermission=permission(request.session.get("user_type"))
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    if(len(data) == 0):
        return render(request, "fleet_owner_and_fleet_operator/list_fleet_operator.html",{"newuserPermission":newuserPermission, "data": [],'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    elif(data == False):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "fleet_owner_and_fleet_operator/list_fleet_operator.html",{"newuserPermission":newuserPermission, data: data,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        return render(request, "fleet_owner_and_fleet_operator/list_fleet_operator.html",{"newuserPermission":newuserPermission, "data": data,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"ActiveFleetOperator":FleetOperator.objects.filter(status=True).count(),"InactiveFleetOperator":FleetOperator.objects.filter(status=False).count()})

## get active and deactive fleet operator
def getActiveandInactiveFleetOperatorupnderFleetOwner(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))
    data=getActiveAndInactiveFleetOperatore(request)
    if(data != False and len(data) == 0):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['dataNotFound'])
        return render(request, "fleet_owner_and_fleet_operator/active_and_inactive_fleet_operator.html",{"newuserPermission":newuserPermission, "data": [],'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        return render(request, "fleet_owner_and_fleet_operator/active_and_inactive_fleet_operator.html",{"newuserPermission":newuserPermission, "data": list(data),'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"action": parseQuerySting(request)["action"]})

####  VCU ####
# create VUC
def createVCUManagement(request):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    if request.method == "GET":
        return render(request, "vcu_management_templates/add_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    if request.method == "POST":
        data=createVCU(request)

        if(data == True):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['VCUExists'])
            return render(request, "vcu_management_templates/add_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

        elif(data == False):
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
            return render(request, "vcu_management_templates/add_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

        else:
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['VCUCreate'])
            return render(request, "vcu_management_templates/add_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

## update VCU data
def updateVCUManagement(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    data=updateVCU(request,id)
    if request.method == "GET":
        return render(request, "vcu_management_templates/update_vcu.html",{"newuserPermission":newuserPermission,'data': data,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    if(data == False and len(data) != 0):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "vcu_management_templates/update_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            data=updateVCU(request,id)
            messages.add_message(request, messages.SUCCESS, successAndErrorMessages()['VCUUpdate'])
            return render(request, "vcu_management_templates/update_vcu.html",{"newuserPermission":newuserPermission,'data' : data ,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})
        else:

            return render(request, "vcu_management_templates/update_vcu.html",{"newuserPermission":newuserPermission,'data' : data,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})


## list VCU data
def listVCUManagement(request):
    data=listVCU(request)
    newuserPermission=permission(request.session.get("user_type"))

    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    if(len(data) == 0) :
        return render(request, "vcu_management_templates/list_vcu.html",{"newuserPermission":newuserPermission,'data':data, 'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    elif(data == False):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "vcu_management_templates/list_vcu.html",{"newuserPermission":newuserPermission,'data':data, 'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        return render(request, "vcu_management_templates/list_vcu.html",{"newuserPermission":newuserPermission,'data':data, 'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

## delete VCU data
def deleteVCUManagemant(request,id):
    userPermission=UserPermission(request,request.session.get("IsAdmin"))
    newuserPermission=permission(request.session.get("user_type"))

    data=True
    if request.method == "GET": 
        data=list(deleteVCU(request,id))[0]
    if(data == False):
        messages.add_message(request, messages.WARNING, successAndErrorMessages()['internalError'])
        return render(request, "vcu_management_templates/delete_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission})

    else:
        if request.method == "POST":
            data=deleteVCU(request,id)
            messages.add_message(request, messages.WARNING, successAndErrorMessages()['VCUDelete'])
            return redirect("listvcu")
        else:
            return render(request, "vcu_management_templates/delete_vcu.html",{"newuserPermission":newuserPermission,'IsAdmin' : request.session.get("IsAdmin"),'UserPermission':userPermission,"data":data})
