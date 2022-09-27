from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
# from .mixins import MessageHandler
from .forms import BatteryDetailsFrom, CreateUserForm
from .models import Crmuser, BatteryDetail, CrmUserManager
from django.contrib import messages
from django.contrib.auth import logout
import psycopg2 as db
from django.contrib.auth.hashers import make_password, check_password
from .auth_helper import getSignInFlow, getTokenFromCode,getToken,getMsalApp,removeUserAndToken, storeUser
from .graph_helper import *



em=''
uname = ''
con = ''
pwd = ''
pwd_con = ''
last_login = ''
is_admin = ''
def register(request):
    global em,uname,con,pwd,pwd_con,last_login
    if request.method=="POST":
        conn=db.connect(host="localhost",user="postgres",password="1234",database='battery_management')
        cursor=conn.cursor()
        d=request.POST
        
        for key,value in d.items():
            if key=="email":
                em=value
            if key=="username":
                uname=value
            if key=="contact":
                con=value
            if key=="password":
                pwd=make_password(value)
            if key=="password_conformation":
                pwd_con=make_password(value)
        
        last_login = datetime.now()
        is_admin = False
        c="INSERT INTO irasusapp_crmuser Values('{}','{}','{}','{}','{}','{}','{}')".format(em,uname,con,pwd,pwd_con,last_login,is_admin)   
        cursor.execute(c)
        conn.commit()
        return redirect('login')

    return render(request,'register.html')

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
                # pass
        else:
            messages.info(request, "Username or Password Inccorect")

    return render(request,'login.html')  

#Logout
def logoutUser(request):
    logout(request)
    return redirect('login')

def forgotPassword(request):
    pass

#Add_Battery_details
def batteryDetails(request):
    if request.method == "POST":
        fm = BatteryDetailsFrom(request.POST)
        if fm.is_valid():
            fm.save()
            fm = BatteryDetailsFrom()
    else:
        fm = BatteryDetailsFrom()
    context = {'submit_data': fm }
    return render(request,'dashboard.html', context)

#Get_Battery_details
def getBatteryDetails(request):
    if request.method == "GET":
        data = list(BatteryDetail.objects.values())
    context = {'battery_data': data }
    return render(request, 'battery_details.html',context)

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


def userLogin(request):
    pass
 
#USERPERMISSIONS ========

# def userPermission(request):
#     try:
#         if request.method == "POST":
#             form = UserPermissionFrom(request.method)
#             form.is_valid()
#             form.save()
#     except Exception as e:
#         print(e)