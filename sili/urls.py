from django.urls import path
from . import views
# from sili.views import home, get_response
app_name = 'sili'


urlpatterns = [
    path('', views.home, name='home'),
    path('get-response/', views.Talk,name='get-response'),

    path('index/', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('error/', views.error, name='error'),
    path('faq/', views.faq, name='faq'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('signup/', views.SignupView, name='SIGNUP'),
    path('login/', views.login, name='LOGIN'),
    path('logout/', views.userLogOut, name='userLogOut'),
    
]