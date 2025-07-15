# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, CustomAuthToken, ForgotPasswordView, ResetPasswordView,
    PatientViewSet, WoundImageViewSet, WoundAnalysisViewSet
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'wound_images', WoundImageViewSet)
router.register(r'wound_analyses', WoundAnalysisViewSet) # Read-only for direct access

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('', include(router.urls)), # Include all router-generated URLs
]