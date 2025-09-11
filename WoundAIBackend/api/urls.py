# # # api/urls.py

# # from django.urls import path, include
# # from rest_framework.routers import DefaultRouter
# # from .views import (
# #     RegisterUserView, CustomAuthToken, ForgotPasswordView, ResetPasswordView,
# #     PatientViewSet, WoundImageViewSet, WoundAnalysisViewSet
# # )

# # router = DefaultRouter()
# # router.register(r'patients', PatientViewSet)
# # router.register(r'wound_images', WoundImageViewSet)
# # router.register(r'wound_analyses', WoundAnalysisViewSet) # Read-only for direct access

# # urlpatterns = [
# #     path('register/', RegisterUserView.as_view(), name='register'),
# #     path('login/', CustomAuthToken.as_view(), name='login'),
# #     path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
# #     path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
# #     path('', include(router.urls)), # Include all router-generated URLs
# # ]




# # core/urls.py
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import (
#     register, login, me, my_patient,
#     PatientViewSet, WoundViewSet, WoundImageViewSet, WoundAnalysisViewSet,ReportViewSet,PrescriptionViewSet
# )

# router = DefaultRouter()
# router.register(r"reports", ReportViewSet, basename="reports")
# router.register(r"prescriptions", PrescriptionViewSet, basename="prescriptions")
# router.register(r"patients", PatientViewSet, basename="patients")
# router.register(r"wounds", WoundViewSet, basename="wounds")
# router.register(r"wound-images", WoundImageViewSet, basename="wound-images")
# router.register(r"wound-analyses", WoundAnalysisViewSet, basename="wound-analyses")

# urlpatterns = [
#     path("auth/register/", register),
#     path("auth/login/", login),
#     path("users/me/", me),
#     path("users/me/patient/", my_patient),
#     path("", include(router.urls)),
# ]




# project/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from api import views as api_views

router = DefaultRouter()

# ---------- Core (user/patient/wound) ----------
router.register(r"patients", api_views.PatientViewSet, basename="patient")
router.register(r"wounds", api_views.WoundViewSet, basename="wound")
router.register(r"wound-images", api_views.WoundImageViewSet, basename="woundimage")
router.register(r"analyses", api_views.WoundAnalysisViewSet, basename="analysis")

# ---------- API (reports/prescriptions) ----------
router.register(r"reports", api_views.ReportViewSet, basename="report")
router.register(r"prescriptions", api_views.PrescriptionViewSet, basename="prescription")

urlpatterns = [
   
    # ---- Auth ----
    path("auth/register/", api_views.register, name="register"),
    path("auth/login/", api_views.login, name="login"),
    path("auth/me/", api_views.me, name="me"),
    path("auth/my-patient/", api_views.my_patient, name="my_patient"),

    # ---- Main API (router viewsets) ----
    path("", include(router.urls)),
]
