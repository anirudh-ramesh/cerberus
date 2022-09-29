from django.urls import path
from . import views

app_name = 'user_management'


urlpatterns= [
        path('adduser/', views.addUser, name="demo"),
        path('getuser/', views.getUser, name="getdata"),
        path('updateuser/<str:id>/', views.updateUser, name="update"),
        path('deletuser/<str:id>/', views.deleteUser, name="delete"),
        
]