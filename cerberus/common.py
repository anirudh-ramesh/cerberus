from user_management.models import Settings,userSettings
from django.conf import settings
from django.core.mail import send_mail

def successAndErrorMessages():
    response = {
        "AuthError":"You are not authorize to view this",
        "userCreate": "User is create successfully",
        "userUpdate": "User is update successfully",
        "userRemove": "User is remove successfully",
        "singupMessage": "You have successfully signed up",
        "loginMessage": "You have successfully Logged in",
        "emailTaken": "Email is already taken! try another one",
        "passwordNotMatched": "Password did not matched!",
        "loginErrorMessage": "Username or password is inccorect",
        "userNotFound": "User is not found",
        "logout": "You have successfully Logout.",
        "addUser": "User is added successfully",
        "updateUser": "User is update successfully",
        "removeUser":"User is remove successfully",

        "createOrganisation": "Organisation is create successfully",
        "updateOrganisation": "Organisation is update successfully",
        "removeOrganisation": "Organisation is remove successfully",
        "roleAssigned" : "Role is assigned to organisation",

        "createOrganisationProfile": "Organisation-Profile is created successfully",
        "updateOrganisationProfile": "Organisation-Profile is updated successfully",
        "removeOrganisationProfile": "Organisation-Profile is removed successfully",

        "addVehicle": "Vehicle is added successfully",
        "updateVehicle": "Vechicle-details is Updated successfully",
        "removeVehicle": "Vehicle is removed successfully",
        "assignBattery" : "Battery assign to vehicle successfully",
        "batteryRemovefrom" : "Battery is removed from vehicle",
        "alreadyAddedVehicle": "Details already is added for this serial number",
        "alreadyVehicleUser": "Vehicle is already added To this user",

        "addBattery": "Battery is added successfully",
        "addBatteryError": "Battery is already assiged to This vehicle",
        "updateBatteryDetails" : "Battery-details is updated successfully",
        "removeBatteryDetails" : "Battery-details is removed successfully",
        "alreadyAddedBattery": "Details already is added for this serial number",

        "addDriver" : "Driver is added successfully",
        "updateDriver" : "Driver is updated successfully",
        "removeDriver" : "Driver is removed successfully",

        "csvGenerate" : "CSV generate successfully",
        "locationCreate" : "Location is created successfully",
        "locationUpdate": "Location is update successfully",
        "removeLocation": "Remove Location",
        "internalError": "Server Error",

        "removeVehiclefromUser": "Removed vehicle from user",
        "addVehicleToUser" : "Vehicle added to user",

        "createSwapStation": "Swap-Station is Created successfully",
        "updateSwapStation": "Swap-Station is Updated successfully",
        "removeSwapStation": "Swap-Station is removed successfully",

        "deivceAdded" : "Device is added successfully",
        "deviceUpdate": "Device is update successfully",
        "removeDevice": "Device is deleted successfully",
        "devicealreadyAdded": "Device is already added",
        "deviceAddToBattery": "Device is added To battery successfully.",
        "deviceAlreadyAdded": "This IOT-Device is already added.",
        "removeDeviceFromBattery": "Device is remove from battery successfully.",
        "dataNotFound": "Data Not Found",

        "Role":"Role is create successfully",
        "userViewPermission": ["Users","BatteryPacks","Vehicles"],

        #fleet management

        "fleetownerExists": "fleet owner is already exists",
        "fleetownerCreate": "fleet owner is create successfully",
        "fleetownerupdate":"fleet owner is update successfully",

        "fleetoperatorExists": "fleet operatoe is already exists",
        "fleetoperatorCreate": "fleet operatoe is create successfully",
        "fleetoperatorupdate":"fleet operatoe is update successfully",

    }
    return response

def UserPermission(request,check=None):
    try:
        module_data = Settings.objects.values()
        new_data=[]
        res={}
        if(request.session.get("IsAdmin")):
            res['module'] = module_data
            for permission in module_data:
                data=list(userSettings.objects.filter(user_id=request.session.get("email"),module_name=permission["module_name"]).values())
                if(len(data) and data[0]["module_status"] == True):
                    permission["module_status"]= False
                    new_data.append(permission)
                else:
                    permission["module_status"]= True
                    new_data.append(permission)

            res['module'] = new_data
        else:
            new_data=[]
            for permission in module_data:
                if(permission["module_name"] in successAndErrorMessages()["userViewPermission"]):
                    data=list(userSettings.objects.filter(user_id=request.session.get("email"),module_name=permission["module_name"]).values())
                    if(len(data) and data[0]["module_status"] == False):
                        permission["module_status"]= False
                        new_data.append(permission)
                    else:
                        permission["module_status"]= True
                        new_data.append(permission)                             
            res['module'] = new_data
        if(check != None):
            res={
                "Users":True,
                "BatteryPacks":True,
                "Vehicles":True,
                "Geography":False,
                "Organisation":False,
                "IOTDevice":False,
                "Reports":False,
                "SwapingStation":False,
                "VCU":False,
            }
            for i in new_data:
                if(request.session.get("IsAdmin")):
                    res[i["module_name"]]= i["module_status"]
                else:
                    res[i["module_name"]]= i["module_status"]
        return res
    except Exception as e:
        print(e)

def sendEmail(request, subject, message=None):
    try:
        subject = subject
        message = message
        # id = id 
        # assignToid = assignToid
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['dixit.ims.in@gmail.com']
        email = send_mail( subject, message, email_from, recipient_list )
    except Exception as e:
        print(e)




def permission(role):
    if(role == "Admin"):
        superAdmin={
            "vehicle":{
                "create": True,
                "update": True,
                "delete": True,
                "batteryAssigned": True,
                "DriverCreate": True,
                "batteryView": True,
                "userAssigned": True,
                "assignedOrganisation": True
            },
            "battery":{
                "create": True,
                "update": True,
                "delete": True,
                "batteryAssigned": True,
                "assigned": True,
            },
            "swapstation":{
                "create": True,
                "update": True,
                "delete": True,
                "assigned": True,
                "view": True
            },
            "geofence":{
                "create":True,
                "update":True,
                "delete":True
            },
            "org":{
                "addUsertoorg":True,
                "delete":True,
                "createRole":True,
                "createProfile": True,
                "assignedvehical":True,
                "view":True,
                "listVihical": True
            },
            "iot":{
                "create":True,
                "update":True,
                "delete":True,
                "assignBattery":True
            },
            "csv":{
                "download": True,
            },
            "fleetOwner":{
                "create":True,
                "update":True,
                "delete":True,
            },
            "fleetOperater":{
                "create":True,
                "update":True,
                "delete":True,
            },
            "payment":{
                "log": True
            }
        }
        return superAdmin
    if(role == "User" or role =="Driver"):
        User={
            "vehicle":{
                "create": False,
                "update": False,
                "delete": False,
                "view": True,
                "batteryAssigned": False,
                "DriverCreate": False,
                "batteryView": True,
                "userAssigned": False,
                "assignedOrganisation": False
            },
            "battery":{
                "create": False,
                "update": False,
                "delete": False,
                "batteryAssigned": False,
                "assigned": False,
                "view": True
            },
            "swapstation":{
                "create": False,
                "update": False,
                "delete": False,
                "assigned": False,
                "view": False

            },
            "geofence":{
                "create":False,
                "update":False,
                "delete":False
            },
            "org":{
                "addUsertoorg":False,
                "delete":False,
                "createRole":False,
                "createProfile": False,
                "assignedvehical":False,
                "view":True,
                "listVehicle": True
            },
            "iot":{
                "create":False,
                "update":False,
                "delete":False,
                "assignBattery":False
            },
            "csv":{
                "download": False,

            },
            "fleetOwner":{
                "create":False,
                "update":False,
                "delete":False,
            },
            "fleetOperater":{
                "create":False,
                "update":False,
                "delete":False,
            },
            "payment":{
                "log": False
            },
            "driver":{
                "create":True,
                "delete":True,
                "update":True,
            },
        }
        return User 
    if(role == "FleetOprater"):
        fleetOperator={
            "vehicle":{
                "create": False,
                "update": False,
                "delete": False,
                "view": True,
                "batteryAssigned": False,
                "DriverCreate": False,
                "batteryView": True,
                "userAssigned": False,
                "assignedOrganisation": False
            },
            "battery":{
                "create": False,
                "update": False,
                "delete": False,
                "batteryAssigned": False,
                "assigned": False,
                "view": True
            },
            "swapstation":{
                "create": False,
                "update": False,
                "delete": False,
                "assigned": False,
                "view": True
            },
            "geofence":{
                "create":False,
                "update":False,
                "delete":False
            },
            "org":{
                "addUsertoorg":False,
                "delete":False,
                "createRole":False,
                "createProfile": False,
                "assignedvehical":False,
                "view":True,
                "listVihical": True
            },
            "iot":{
                "create":False,
                "update":False,
                "delete":False,
                "assignBattery":False
            },
            "csv":{
                "download": False,

            },
            "fleetOwner":{
                "create":False,
                "update":False,
                "delete":False,
            },
            "fleetOperater":{
                "create":False,
                "update":False,
                "delete":False,
            },
            "payment":{
                "log": True
            },
            "driver":{
                "create":False,
                "delete":False,
                "update":False,
                "view": False
            },
        }
        return fleetOperator
    if(role == "FleetOwner"):
        fleetOwner={
            "vehicle":{
                "create": True,
                "update": True,
                "delete": True,
                "view": True,
                "batteryAssigned": False,
                "DriverCreate": False,
                "batteryView": True,
                "userAssigned": False,
                "assignedOrganisation": False
            },
            "battery":{
                "create": False,
                "update": False,
                "delete": False,
                "batteryAssigned": False,
                "assigned": False,
                "view": True
            },
            "swapstation":{
                "create": False,
                "update": False,
                "delete": False,
                "assigned": False,
                "view": True
            },
            "geofence":{
                "create":False,
                "update":False,
                "delete":False
            },
            "org":{
                "addUsertoorg":False,
                "delete":False,
                "createRole":False,
                "createProfile": False,
                "assignedvehical":False,
                "view":True,
                "listVihical": True
            },
            "iot":{
                "create":False,
                "update":False,
                "delete":False,
                "assignBattery":False
            },
            "csv":{
                "download": False,

            },
            "driver":{
                "create":True,
                "delete":True,
                "update":True,
                "view": True

            },
            "fleetOwner":{
                "create":True,
                "update":True,
                "delete":True,
            },
            "fleetOperater":{
                "create":True,
                "update":True,
                "delete":True,
            },
            "payment":{
                "log": True
            }
        }
        return fleetOwner