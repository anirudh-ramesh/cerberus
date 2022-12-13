from django.urls import path
from . import views

app_name = 'user_management'


urlpatterns= [
        path('adduser/', views.addUser, name="demo"),
        path(r'getuser', views.getUser, name="getdata"),
        path('updateuser/<str:id>', views.updateUser, name="update"),
        path('deletuser/<str:id>', views.deleteUser, name="delete"),
 
        path('addorg/', views.addOrganisation, name="addorg"),
        path(r'listorg', views.listOrganisation, name="listorg"),
        path('updateorg/<int:id>', views.updateOranisation, name="updateorg"),
        path('deleteorg/<int:id>', views.deleteOraganisation, name="deleteorg"),
        

        path('addorgprofile/<int:id>', views.addOrganisationProfile, name="addprofile"),
        path('listorgprofile/<int:id>', views.listOrganisationProfile, name="listorgprofile"),
        path('deleteorgprofile/<int:id>', views.deleteOraganisationProfile, name="deleteorgprofile"),

        path('addrole/<int:id>', views.createUserRole, name="role"),
        path('getrole/', views.listRole, name="listrole"),
        path('updaterole/<str:name>', views.updateRole, name="updaterole"),
        path('deleterole/<int:id>', views.deleteRole, name="deleterole"),
        path('newrole/', views.listedUserRole, name="mrole"),
        path(r'list/<int:id>', views.orgUserinfo, name="list"), 

        path('addswap/', views.addSwapStation, name="addswap"),
        path(r'listswapstation', views.listSwapstation, name="listswap"),
        path('updateswapstation/<int:id>', views.updateSwapstationDetails, name="swapstation"),
        path('deletewapstation/<int:id>', views.deleteSwapStation, name="deleteswapstation"),
        
        path('settings', views.moduleSettings, name="setting"),   
        path(r'activeswapstation', views.getActiveAndDeactive, name="activeswapstation"),
        path(r'deactiveswapstation', views.getActiveAndDeactive, name="deactiveswapstation"),     
    
  
]