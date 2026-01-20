from django.urls import path
from . import views

app_name = 'patient_portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.patient_login, name='login'),
    path('logout/', views.patient_logout, name='logout'),
    path('health-records/', views.health_records, name='health_records'),
    path('health-records/update/', views.update_health_records, name='update_health_records'),
    path('messages/', views.messages_list, name='messages'),
    path('consents/', views.consent_management, name='consents'),
]