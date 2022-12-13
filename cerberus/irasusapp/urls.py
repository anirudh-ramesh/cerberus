
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


# app_name = 'irasusapp'

urlpatterns= [
        path('register/', views.register, name="register"),
        path('', views.loginPage, name="login"),
        # path('otp/', views.userOtp, name='otp'),
        path('logout/', views.logoutUser, name="logout"),

    path('dashboard/', views.dashboard, name="home"),
    path('dashboarddata/', views.batteryDetails, name="homed"),
    # path('signin', views.signIn, name='signin'),
    path(r'getdata', views.getBatteryDetails, name="data"),
    path('update/<str:id>', views.updateBatteryDetails, name="updatedata"),
    path('delete/<str:id>', views.deleteRecord, name="deletedata"),

    path('activebattery', views.activeBatteryDetails, name="active"), 
    path('inactivebattery', views.inactiveBatteryDetails, name="inactive"), 
    path('damaged', views.damagedBatteryDetails, name="damagedbattery"), 

    path('activevehicle', views.activeVehicleDetails, name="actvehicle"), 
    path('inactivevehicle', views.inactiveVehicleDetails, name="inactivevehicle"),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    path('reset<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name="password_reset_complete"),

    path('addvehicle/', views.addVehicleDetails, name='addvehicle'),
    path(r'getvehicle', views.getVehicleDetails, name='getvehicle'),
    path('updatevehicle/<int:id>', views.updateVehicleDetails, name='updatevehicle'),
    path('deletevehicle/<int:id>', views.deleteVehicleRecord, name='deletevehicle'),
    
    
    path(r'assigned/<int:id>', views.assignedBatteryList, name="assinged"),
    path(r'orgvehicle/<int:id>', views.assignedOrgVehicleList, name="assingedtoorg"),
    path(r'uservehicle/<str:id>', views.assignedVehicleToUser, name="uservehicle"),

    path('geofence', views.addgeofenceVehicles, name="geofence"),
    path('listdata', views.listgeofenceData, name="add_data"),

    path('driver', views.addDriver, name="addriver"),
    
    path('listdriver', views.listAddedDriver, name="getdrivers"),
    path('updatedriver/<str:id>', views.updateDriver, name="updatedriver"),
    path('deletedriver/<str:id>', views.deleteDriver, name="driverdelete"),

    path('getcsv', views.filedForCSV, name="csv"),
    path(r'export_to_csv', views.exportCSV, name="exportcsv"),

    path('open', views.swapSatationDoors, name="swapdoor"),

    path('adddevice', views.addIotDevice, name="adddevice"),

    path('listdevice', views.listIotDevice, name="listdevice"),
    path(r'updatedevice/<int:id>', views.updateIOTDevice, name="updatedevice"),
    path('deletedevice/<int:id>', views.deleteIOTDeviceRecord, name="devicedelete"),

 
    path('vehicledetails', views.VCU, name="details"),
    path(r'assignediot', views.assignedIotDeviceToBattery, name="iotdevice"),

    path(r'bettrypack', views.battery_pack_menu, name="battery_data"),
    path(r'subpack', views.battery_pack_sub_menu, name="sub_data"),

    path('irame', views.irameData, name="iramedata"),

    path(r'activeiot', views.getActiveAnddeactiveIotBystatus, name="activeiot"),
    path(r'deactiveiot', views.getActiveAnddeactiveIotBystatus, name="deactiveiot"),     



    
    
]