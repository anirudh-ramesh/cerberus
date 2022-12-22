""" VCU manageemnt """
""" create IMEI_NUMBER """

from .models import VCU


def createVCU(request):

    """ VCU required field name """
    """ imei_number """
 
    try:
        """ check imei_number is exists """
        if(len(VCU.objects.filter(imei_number=request.POST.get('imei_number')).values()) !=0 ):
            return True

        """ create VCU """
        formData = VCU.objects.create(
                        imei_number = request.POST.get('imei_number')
                    )
                    
        formData.save()           
        return formData             
    except Exception as e:
        print(e)
        return False

def updateVCU(request,id):

    """ VCU update filed name """

    try:
        if request.method == "GET":
            return VCU.objects.filter(imei_number=id).values()

        """ update VCU """
        if request.method == "POST": 
            VCU.objects.filter(imei_number=id).update(
                            imei_number = request.POST.get('imei_number')
            ) 
            return VCU.objects.filter(imei_number=request.POST.get('imei_number')).values()

    except Exception as e:
        return False

def listVCU(request):

    """list VCU"""
    try:

        """ VCU """
        if(request.session.get("IsAdmin")):
            listData =VCU.objects.values()
            return listData

    except Exception as e:
        return [] 

def deleteVCU(request,id):

    """ delete VCU"""

    try:

        """ delete VCU """
        if request.method == "GET":
            listData =VCU.objects.filter(imei_number=id).values()
            return listData
        VCU.objects.get(imei_number=id).delete()
        return True
    except Exception as e:
        return False 
