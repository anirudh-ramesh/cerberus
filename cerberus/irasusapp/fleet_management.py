""" Fleet manageemnt """
""" create Fleet owner """
from django.contrib.auth.hashers import make_password, check_password
from .models import FleetOperator,FleetOwner,Crmuser
from urllib import parse
import json
from common import permission
import random
import string
PASSWORD_LENGHT=9

def generatorPassword():
    """" auto password generator """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num
    temp = random.sample(all,PASSWORD_LENGHT)
    password = "".join(temp)
    print(password)
    return password


def createCrmUser(request,user_type):
    try: 
        """ create crm user """
        email = request.POST.get('email')
        user_password = generatorPassword()
        password_conformation = user_password
        if user_password == password_conformation:
            password = make_password(user_password)
            print(password)
            password_conformation = password
            if Crmuser.objects.filter(email=email).exists():
                return True
            else:
                user = Crmuser.objects.create_user(email=email, password=password, password_conformation=password_conformation)
                user.save()
                Crmuser.objects.filter(email=email).update(user_type=user_type,username = request.POST.get('username'))

                return user
    except Exception as e:
        print("Error",e)

def checkActiveAndInActiveStatus(data):
    """ check active and deactive status return True and False """
    if(data == "Active"):
        return True
    else:
        return False    


def parseQuerySting(request):
    """ parse QuerySting data """
    data = request.get_full_path()
    parse.urlsplit(data)
    parse.parse_qs(parse.urlsplit(data).query)
    dictinary_obj = dict(parse.parse_qsl(parse.urlsplit(data).query))
    return dictinary_obj


def createFleetOwner(request):

    """ Fleet owner required filed name """
    """ username """
    """ email  unique"""
    """ is_admin  default """
    """ status True or False"""
    """ create crm user with auto password and password send in email """


    try:
        """ check Fleet owner is exists """
        if(len(FleetOwner.objects.filter(email=request.POST.get('email')).values()) !=0 or len(Crmuser.objects.filter(email=request.POST.get('email'))) != 0):
            print(len(FleetOwner.objects.filter(email=request.POST.get('email')).values()) , len(Crmuser.objects.filter(email=request.POST.get('email'))) )
            return True

        """ create Fleet owner """
        formData = FleetOwner.objects.create(
                        username = request.POST.get('username'),
                        email = request.POST.get('email'),
                        is_admin = True,
                        status=checkActiveAndInActiveStatus(request.POST.get('status'))
                    )
        formData.save()

        FleetOwner.objects.filter(email=request.POST.get('email')).update(permission=json.dumps(permission("FleetOwner")))
        
        createCrmUser(request,"FeetOwner")            
        return formData             
    except Exception as e:
        print(e)
        return False

def updateFleetOwner(request,id):

    """ Fleet owner update filed name """
    """ update Fleet owner data by id """
    """ username """
    """ status True or False """

    try:
        if request.method == "GET":
            return FleetOwner.objects.filter(email=id).values()

        """ update Fleet owner """
        if request.method == "POST": 
            FleetOwner.objects.filter(email=id).update(
                            username = request.POST.get('username'),
                            status=checkActiveAndInActiveStatus(request.POST.get('status')))

            return FleetOwner.objects.filter(email=id).values()

    except Exception as e:
        return False

def listFleetOwner(request):

    """ Fleet owner list"""
    """ list Fleet owner data by email"""

    try:

        """ list Fleet owner """
        if(request.session.get("IsAdmin")):
            listData =FleetOwner.objects.values()
            return listData

        else:
            listData =FleetOwner.objects.filter(email=request.session.get("email")).values()
            return listData

    except Exception as e:
        return [] 

def getActiveAndInactiveFleetOwner(request):
    """ get active and deactive fleet operator """
    try:
        getQuerySting=parseQuerySting(request)
        status=checkActiveAndInActiveStatus(getQuerySting.get("action"))
        data=FleetOwner.objects.filter(status=status).values()
        return data
    except Exception as e:
        return False

def deleteFleetOwner(request,id):

    """ Fleet Owner delete"""
    """ delete Fleet Owner data by email"""

    try:

        """ delete Fleet Owner """
        if request.method == "GET":
            listData =FleetOwner.objects.filter(pk=id).values()
            return listData
        getData=list(FleetOwner.objects.filter(pk=id).values())
        deleteCrmUser=list(Crmuser.objects.filter(email=getData[0]["email"]).values())
        Crmuser.objects.get(pk=deleteCrmUser[0]["email"]).delete()
        FleetOwner.objects.get(pk=id).delete()
        return getData

    except Exception as e:
        return False 


# fleet operato

def createFleetOperator(request):

    """ create fleet operator under fleet owner """
    """ fleet operator required filed name """
    """ username """
    """ email  unique"""
    """ Role  default """
    """ status True or False"""


    try:
        """ check fleet operator is exists """
        if(len(FleetOperator.objects.filter(email=request.POST.get('email')).values()) !=0 or len(Crmuser.objects.filter(email=request.POST.get('email'))) != 0):
            return True
        request.session['UserType']="fleetOperator"
        """ create fleet operator """
        formData = FleetOperator.objects.create(
                    username = request.POST.get('username'),
                    email = request.POST.get('email'),
                    is_admin = True,
                    status=checkActiveAndInActiveStatus(request.POST.get('status')),
                    fleetId=request.session.get("email"),
                    permission=json.dumps(permission("FleetOprater"))
                )
        formData.save() 
        createCrmUser(request,"FleetOprater")            
 
        return formData

    except Exception as e:
        return False

def updateFleetOperator(request,id):

    """ Fleet operator update filed name """
    """ update Fleet operator data by id """
    """ username """
    """ status True or False """

    try:
        if request.method == "GET":
            listData =FleetOperator.objects.filter(email=id).values()
            return listData

        """ update Fleet operator """
        FleetOperator.objects.filter(email=id).update(
                        username = request.POST.get('username'),
                        status=checkActiveAndInActiveStatus(request.POST.get('status')),
                        fleetId=request.session.get("email"))
        listData =FleetOperator.objects.filter(email=id).values()
        return listData

    except Exception as e:
        return False

def deleteFleetOperator(request,id):

    """ Fleet operator delete"""
    """ delete Fleet operator data by email"""
    """ delete Crm user """


    try:

        """ delete Fleet operator """
        if request.method == "GET":
            listData =FleetOperator.objects.filter(pk=id).values()
            return listData

        getData=list(FleetOperator.objects.filter(pk=id).values())
        deleteCrmUser=list(Crmuser.objects.filter(email=getData[0]["email"]).values())
        Crmuser.objects.get(pk=deleteCrmUser[0]["email"]).delete()
        FleetOperator.objects.get(pk=id).delete()

        return getData

    except Exception as e:
        print(e)
        return False        


def listFleetOperator(request):

    """ Fleet operator list"""
    """ list Fleet operator data by email"""

    try:

        """ list Fleet operator """
        if(request.session.get("IsAdmin")):
            listData =FleetOperator.objects.values()
            return listData

        else:
            listData =FleetOperator.objects.filter(email=request.session.get("email")).values()
            return listData

    except Exception as e:
        return []        


def getActiveAndInactiveFleetOperatore(request):
    """ get active and deactive fleet operator """
    try:
        getQuerySting=parseQuerySting(request)
        status=checkActiveAndInActiveStatus(getQuerySting.get("action"))
        data=FleetOperator.objects.filter(status=status).values()
        return data
    except Exception as e:
        return False