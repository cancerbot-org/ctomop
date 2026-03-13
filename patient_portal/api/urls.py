from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CurrentUserViewSet, PatientInfoViewSet, login_view, logout_view, auth_test

router = DefaultRouter()
router.register(r'user', CurrentUserViewSet, basename='user')
router.register(r'patient-info', PatientInfoViewSet, basename='patient-info')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/test/', auth_test, name='auth_test'),
]