
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns= [
        path('register/', views.register, name="register"),
        path('', views.loginPage, name="login"),
        # path('otp/', views.userOtp, name='otp'),
        path('logout/', views.logoutUser, name="logout"),

    path('dashboard/', views.batteryDetails, name="home"),
    path('signin', views.signIn, name='signin'),
    path('getdata/', views.getBatteryDetails, name='data'),
    path('update/<int:id>/', views.updateBatteryDetails, name="updatedata"),
    path('delete/<int:id>/', views.deleteRecord, name="deletedata"),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    path('reset<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name="password_reset_complete"),


    
    # path('add_permission/', views.userPermission, name="addpermission")
]