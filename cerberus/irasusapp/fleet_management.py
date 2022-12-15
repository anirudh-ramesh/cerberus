""" Fleet manageemnt """
""" create Fleet owner """

from .models import FleetOperator,FleetOwner
from urllib import parse

def checkActiveAndInActiveStatus(data):
    if(data == "Active"):
        return True
    else:
        return False    

def parseQuerySting(request):
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

    try:
        """ check Fleet owner is exists """
        if(len(FleetOwner.objects.filter(email=request.POST.get('email')).values())):
            return True

        """ create Fleet owner """
        formData = FleetOwner.objects.create(
                        username = request.POST.get('username'),
                        email = request.POST.get('email'),
                        is_admin = True,
                        status=checkActiveAndInActiveStatus(request.POST.get('status'))
                    )
        formData.save()            
        return formData             
    except Exception as e:
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
            list =FleetOwner.objects.values()
            return list

        else:
            list =FleetOwner.objects.filter(email=request.session.get("email")).values()
            return list

    except Exception as e:
        return [] 

## get active and deactive fleet owner               
def getActiveAndInactiveFleetOwner(request):
    """ get active and deactive fleet operator """
    try:
        getQuerySting=parseQuerySting(request)
        status=checkActiveAndInActiveStatus(getQuerySting.get("action"))
        data=FleetOwner.objects.filter(status=status).values()
        return data
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
        if(len(FleetOperator.objects.filter(email=request.POST.get('email')).values())):
            return True

        """ create fleet operator """
        formData = FleetOperator.objects.create(
                    username = request.POST.get('username'),
                    email = request.POST.get('email'),
                    is_admin = True,
                    status=request.POST.get('status') is "Active" and True or False,
                    fleetId=request.session.get("email")
                )
        formData.save()  
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
            list =FleetOperator.objects.filter(email=id).values()
            return list

        """ update Fleet operator """
        FleetOperator.objects.filter(email=id).update(
                        username = request.POST.get('username'),
                        status=checkActiveAndInActiveStatus(request.POST.get('status')),
                        fleetId=request.session.get("email"))
        list =FleetOperator.objects.filter(email=id).values()
        return list

    except Exception as e:
        return False

def deleteFleetOperator(request,id):

    """ Fleet operator delete"""
    """ delete Fleet operator data by email"""

    try:

        """ delete Fleet operator """
        if request.method == "GET":
            list =FleetOperator.objects.filter(pk=id).values()
            return list

        delete = FleetOperator.objects.get(pk=id).delete()
        return delete

    except Exception as e:
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