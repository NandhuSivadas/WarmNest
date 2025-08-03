from django.urls import path,include
from ML import views
app_name="webml"

urlpatterns = [

    # path('HomePage/',views.homepage,name='homepage'),
    path('analyze_sentiment/',views.analyze_sentiment,name='analyze_sentiment'),

    path('HomePageReview/',views.homepage,name='homepage'),

]


