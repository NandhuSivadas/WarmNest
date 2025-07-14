from django.urls import path,include
from Admin import views
app_name="wadmin"


urlpatterns = [
    path('homepage/',views.HomePage,name='homepage'),
    path('viewproperty/', views.view_property, name='viewproperty'),
    path('addproperty/',views.Add_Property,name='addproperty'),
    path('viewmore/<int:property_id>/', views.view_more, name='viewmore'),
    path('userlist/',views.User_List,name='userlist'),
    path('pendingmessages/', views.pending_user_messages, name='pendingmessages'),
    path('messagereply/<int:user_id>/<int:property_id>/', views.message_reply, name='messagereply'),
    path('repliedmessages/',views.replied_messages,name='repliedmessages'),
    path('verifyuser/<int:id>/', views.verifyuser, name='verifyuser'),
    path('rejectuser/<int:id>/', views.rejectuser, name='rejectuser'),
    path('verified_users/',views.verified_users,name='verified_users'),
    path('blocked_users/',views.blocked_users,name='blocked_users'),
    path('admin_logout/',views.admin_logout,name='admin_logout')
    
    

 

]