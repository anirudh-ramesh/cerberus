from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
# from .mixins import MessageHandler
from .forms import BatteryDetailsFrom, CreateUserForm
from .models import Crmuser, BatteryDetail
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth import logout
import psycopg2 as db
from django.contrib.auth.hashers import make_password, check_password
from .auth_helper import getSignInFlow, getTokenFromCode,getToken,getMsalApp,removeUserAndToken, storeUser


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
    try:
        if request.method == "GET":
            data = list(BatteryDetail.objects.values())
        context = {'battery_data': data }
        return render(request, 'battery_details.html',context)
    except Exception as e:
        messages.warning("Internal server error")

#This Function Will Update_Battery_details/Edit
def updateBatteryDetails(request, id):
    if request.method == 'POST':
        pi = BatteryDetail.objects.get(pk=id)
        fm = BatteryDetailsFrom(request.POST, instance=pi)
        if fm.is_valid():
            fm.save()
    else:
        pi = BatteryDetail.objects.get(pk=id)
        fm = BatteryDetailsFrom(instance=pi)
    return render(request,'update_battery_details.html',{'form': fm})
    

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
