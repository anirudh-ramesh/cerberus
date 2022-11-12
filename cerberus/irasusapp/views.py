from wsgiref.handlers import read_environ
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from datetime import datetime
import re
import json
from user_management.models import Organisation
# from .mixins import MessageHandler
from .forms import CreateUserForm
from .models import Crmuser, BatteryDetail, Geofence,Vehicle
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from .auth_helper import getSignInFlow, getTokenFromCode,getToken,getMsalApp,removeUserAndToken, storeUser
from db_connect import listAssignedBatteryVehicle,assignedVehicleToOrganisation,getOrgAssignedVehicle,removeAssignedVehiclefromOrganisation,listAssignedVehicleToUser,removeUserVehicle
from django.contrib.gis.geos import Point,Polygon
from django.contrib.gis.measure import Distance



format='%Y-%m-%d'

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        contact = request.POST['contact']
        password1 = request.POST['password']
        password_conformation = request.POST['password_conformation']

        if password1 == password_conformation:
            if Crmuser.objects.filter(username=username).exists():
                messages.info(request,'Username exists! try another username')
                return redirect('register')
            else:
                if Crmuser.objects.filter(email=email).exists():
                    messages.info(request,'Email is already taken! try another one')
                    return redirect('register')
                else:
                    user = Crmuser.objects.create_user(username=username, email=email, password=password1, contact=contact, password_conformation=password_conformation)
                    print(user)
                    user.save()
                    return redirect('login')   
        else:
            messages.info(request,'Password did not matched!..')
            return redirect('register')
    else:
        return render(request, 'register.html')  

def loginPage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        crmuser = Crmuser.get_user_by_email(email)
        if crmuser:
            flag = check_password(password,crmuser.password)
            if flag:
                return redirect('home')
            else:
                messages.info(request, "Username or Password Inccorect")
                return redirect('login')
        else:
            messages.info(request, "User not Found")

    return render(request,'login.html')  

#Logout
def logoutUser(request):
    logout(request)
    return redirect('login')

def forgotPassword(request):
    pass

#Add_Battery_details
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
        return render(request,'dashboard.html')
    except Exception as e:
        print("Server Error")

    

#Get_Battery_details
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
        messages.warning(request,"Internal server error")

#This Function Will Update_Battery_details/Edit
def updateBatteryDetails(request, id):
    battery_data = BatteryDetail.objects.filter(battery_serial_num=id).values()
    if request.method == "POST":
        model_name = request.POST['model_name']
        battery_serial_num = request.POST['battery_serial_num']
        battery_type = request.POST['battery_type']
        bms_type = request.POST['bms_type']
        iot_type = request.POST['iot_type']
        iot_imei_number = request.POST['iot_imei_number']
        sim_number = request.POST['sim_number']
        warrenty_start_date = datetime.strptime(request.POST['warrenty_start_date'],format)
        warrenty_duration = datetime.strptime(request.POST['warrenty_duration'],format)
        assigned_owner = request.POST['assigned_owner']
        status = request.POST['status']
        battery_cell_chemistry = request.POST['battery_cell_chemistry']
        battery_pack_nominal_voltage = request.POST['battery_pack_nominal_voltage']
        battery_pack_nominal_charge_capacity = request.POST['battery_pack_nominal_charge_capacity']
        charging_status = request.POST['charging_status']

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
        return render(request,'update_battery_details.html', {'form': battery_data })

    battery_data = list(BatteryDetail.objects.filter(battery_serial_num=id).values())
    return render(request,'update_battery_details.html',{'form': battery_data})
    
#Delete_Record
def deleteRecord(request,id):
    try:
        pi = BatteryDetail.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            return redirect('data')
        context = {}
        return render(request, "battery_details.html", context)
    except Exception as e:
        print("Error While deleting Record",e)


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

def signIn(request):
    flow = getSignInFlow()
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    return HttpResponseRedirect(flow['auth_uri'])

def signOut(request):
    removeUserAndToken(request)
    return redirect('login')

def callBack(request):
    result = getTokenFromCode(request)
    user = get_user(result['access_token'])
    storeUser(request,user)
    return redirect('home')

def userSignin(request):
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        CreateUserForm()
    context = { 'form': form }
    return render(request, 'login.html', context)

#Add Organisation Profile
def addVehicleDetails(request): 
    if request.method == "POST":
        formData = Vehicle.objects.create(
            vehicle_model_name = request.POST['vehicle_model_name'],
            chasis_number = request.POST['chasis_number'],
            configuration = request.POST['configuration'],
            vehicle_choice = request.POST['vehicle_choice'],
            vehicle_iot_imei_number = request.POST['vehicle_iot_imei_number'],
            vehicle_sim_number = request.POST['vehicle_sim_number'],
            vehicle_warrenty_start_date = datetime.strptime(request.POST['vehicle_warrenty_start_date'], format),
            vehicle_warrenty_end_date = datetime.strptime(request.POST['vehicle_warrenty_end_date'], format),
            assigned_owner = request.POST['assigned_owner'],
            insurance_start_date = datetime.strptime(request.POST['insurance_start_date'], format),
            insurance_end_date = datetime.strptime(request.POST['insurance_start_date'], format)   
        )
        formData.save()
    return render(request,'add_vehicle_details.html')

def getVehicleDetails(request):
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
            return redirect('getvehicle')

    return render(request, 'list_vehicle_details.html', {'vehicle_data':vehicle_data , 'email_id': email_id , 'serial_number': serial_number})

def updateVehicleDetails(request,id):
    update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())

    if request.method == "POST":
        vehicle_model_name = request.POST['vehicle_model_name']
        chasis_number = request.POST['chasis_number']
        configuration = request.POST.get('configuration')
        vehicle_choice = request.POST['vehicle_choice']
        vehicle_iot_imei_number = request.POST['vehicle_iot_imei_number']
        vehicle_sim_number = request.POST['vehicle_sim_number']
        vehicle_warrenty_start_date = datetime.strptime(request.POST['vehicle_warrenty_start_date'], format)
        vehicle_warrenty_end_date = datetime.strptime(request.POST['vehicle_warrenty_end_date'], format)
        assigned_owner = request.POST['assigned_owner']
        insurance_start_date = datetime.strptime(request.POST['insurance_start_date'], format)
        insurance_end_date = datetime.strptime(request.POST['insurance_start_date'], format)

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

        return render(request,'update_vehicle.html',{'update_vehicle_data': update_vehicle })

    update_vehicle = list(Vehicle.objects.filter(chasis_number=id).values())
    return render(request,'update_vehicle.html',{'update_vehicle_data': update_vehicle })

#Delete_Record
def deleteVehicleRecord(request,id):
    try:
        pi = Vehicle.objects.get(pk=id)
        if request.method == 'POST':
            pi.delete()
            return redirect('getvehicle')
        context = {}
        return render(request, "list_vehicle_details.html", context)
    except Exception as e:
        print("Error While deleting Record",e)
  
def assignedBatteryList(request,id):
    # Vehicle.objects.filter(chasis_number=id).values()
    if request.method == "GET":
        data = listAssignedBatteryVehicle(id)

    if request.method == "POST": 
        data = listAssignedBatteryVehicle(id)
        assigned_vehicle_battery = Vehicle.objects.filter(chasis_number=id)
        for x in data:
            data = BatteryDetail.objects.filter(pk=x['battery_serial_num']).update(vehicle_assign_id=None, is_assigned=False)

    context = {
        'assigned_battery_list' : data
    }
    return render(request, 'list_assigned_battery.html',context)

def assignedOrgVehicleList(request,id):
    org_vehicle_list = getOrgAssignedVehicle(id)
        
    #REMOVE VEHICLE FROM ORGANISATION
    if request.method == "POST":
        assigned_vehicle = str(request.get_full_path()).split("?").pop()
        vehicle_id = assigned_vehicle.split("&")[0].split("=")[1]
        remove_org_vehicle = removeAssignedVehiclefromOrganisation(id,vehicle_id)
        return redirect('user_management:listorg')
            
    return render(request, 'list_organisation_vehicle.html',{'org_vehicle_list': org_vehicle_list})

def assignedVehicleToUser(request,id):
    user_vehicle =""
    if request.method == "GET":
        user_vehicle = listAssignedVehicleToUser(id)

    #REMOVE VEHICLE FROM USER
    if request.method == "POST":
        assigned_vehicle = str(request.get_full_path()).split("?").pop()
        vehicle_id = assigned_vehicle.split("&")[0].split("=")[1]
        print(vehicle_id)
        user_vehicle = removeUserVehicle(False,vehicle_id)
        return redirect("user_management:getdata")

    return render(request,'list_assigned_vehicle_to_user.html',{'user_vehicle':user_vehicle})


def addgeofenceVehicles(request):
    polygon_coordinates = []
    longitude_data = []
    latitude_data = []
    print(request.method, "=========REQUEST========")
    if request.method == "POST":
        print("IN THE POST===========")
        geoname = request.POST['geoname']
        geotype = request.POST['geotype']
        description = request.POST['description']
        position_add = request.POST['pos_address']
        enter_lat =request.POST['enter_latitude']
        newdata=json.loads(enter_lat)
        print(newdata, "============>>>>>>>>>>>>>>>>NEWDATA")
        coordinate_data = newdata["features"][0]['geometry']['coordinates']
        radidus = newdata["features"][0]['properties']['radius']
        print(coordinate_data, "======COORDINATES=============")

        if newdata["features"][0]['geometry']['type'] == 'Point':
            print("POINT")
            longitude = coordinate_data[0]
            latitude = coordinate_data[1]
            circle_radius = Distance(float(radidus))
            print(circle_radius, "=====CIRCLE")
            location = Point(float(longitude),float(latitude),srid=4326)
            
            print(location, "=============LOCATION")
            
            # newdata = Geofence.objects.create(geoname=geoname,geotype=geotype,description=description,enter_latitude=latitude,enter_longitude=longitude,pos_address=position_add,location=location)
            return render(request, 'geolocation_form.html')


        if newdata["features"][0]['geometry']['type'] == 'Polygon':
            print("POLYGONE CONDITION")
            coordinate_polygon = newdata["features"][0]['geometry']['coordinates']
            newdata = *((*row,) for row in coordinate_polygon[0]),
            converted_tuple_data = list(newdata)
            for polygon_data in converted_tuple_data:
                print(polygon_data, "=========POLYGON-DATA======")
                longitude = ((polygon_data[0]),(polygon_data[1]))
                long = polygon_data[0]
                longitude_data.append(long)
                latitude = polygon_data[1]
                latitude_data.append(latitude)
                polygon_coordinates.append(longitude)
        geofence = Polygon(((polygon_coordinates)),srid=4326)
        newdata = Geofence.objects.create(geoname=geoname,geotype=geotype, description=description,enter_latitude=latitude_data,enter_longitude=longitude_data,pos_address=position_add,geofence=geofence)
        print(newdata, "==========NEWDATA=========")
        

        
        
        # print(newdata["features"][0]['geometry']['type'], "==========LATITUEDE=========")
        # print(newdata["features"][0]['geometry']['coordinates'], "==========LATITUEDE=========")

    return render(request, 'geolocation_form.html')


def listgeofenceData(request):
    if request.method == "GET":
        geofencedata = list(Geofence.objects.values())
        print(geofencedata, "======GEOFENCE-DATA===========")
    
    return render(request, 'list_geofence_data.html',{ 'geofencedata': geofencedata })




        
