from django.urls import path
from . import views

app_name = 'user_management'


urlpatterns= [
        path('adduser/', views.addUser, name="demo"),
        path('getuser/', views.getUser, name="getdata"),
        path('updateuser/<str:id>/', views.updateUser, name="update"),
        path('deletuser/<str:id>/', views.deleteUser, name="delete"),
 
        path('addorg/', views.addOrganisation, name="addorg"),
        path('listorg/', views.listOrganisation, name="listorg"),
        path('updateorg/<int:id>/', views.updateOranisation, name="updateorg"),
        path('deleteorg/<int:id>/', views.deleteOraganisation, name="deleteorg"),
        

        path('orgprofile/', views.addOrganisationProfile, name="orgprofile"),
        path('listorgprofile/', views.listOrganisationProfile, name="listorgprofile"),

        path('addrole/<int:id>', views.createUserRole, name="role"),
        path('getrole/', views.listRole, name="listrole"),
        path('updaterole/<int:id>/', views.updateRole, name="updaterole"),
        path('deleterole/<int:id>/', views.deleteRole, name="deleterole"),
        path('newrole/', views.listedUserRole, name="mrole"),
        path('list/<int:id>', views.orgUserinfo, name="list"),     
        
        
]