from django.urls import path, include
from Guest import views
app_name = "wguest"

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('homepage/', views.homepage, name='homepage'),
    path('viewproperty/', views.viewproperty, name='viewproperty'),
    path('viewdetails/<int:property_id>/', views.viewdetails, name='viewdetails'),
    path('forget-password/', views.forget_password_view, name='forget_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.create_new_password_view, name='reset_password'),
    path('verify/<str:signed_user_id>/', views.verify_email, name='verify_email'),
]