from django.urls import path,include
from User import views
app_name="wuser"

urlpatterns= [
    path('userhomepage/',views.userhomepage,name='userhomepage'),
    path('myprofile/',views.my_profile,name='myprofile'),
    path('editprofile/',views.edit_profile,name='editprofile'),
    path('changepassword/',views.change_password,name='changepassword'),
    path('viewproperty/',views.viewproperty,name='viewproperty'),
    path('viewdetails/<int:property_id>/',views.viewdetails,name='viewdetails'),
    path('mymessages/',views.mymessages,name='mymessages'),
    path('add-add_favourite/<int:property_id>/', views.add_to_favourites, name='add_favourite'),
    path('favourites/', views.favourite_list, name='favourite_list'),
    path('user_logout/',views.user_logout,name='user_logout'),
    path('messageuser/<int:property_id>/', views.messageuser, name='messageuser'),
    path('logoutconfirmation/',views.logout_confirm,name='logout_confirm'),
    path('review/<int:property_id>/',views.user_review,name='user_review'),
]
