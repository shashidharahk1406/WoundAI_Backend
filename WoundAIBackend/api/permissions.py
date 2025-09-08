# from rest_framework import permissions

# # from WoundAIBackend.api.models import Patient, User

# class IsAdminOrDoctor(permissions.BasePermission):
#     """
#     Custom permission to only allow 'admin' or 'doctor' users.
#     """
#     def has_permission(self, request, view):
#         return request.user and (request.user.role in ['admin', 'doctor'] or request.user.is_staff)

# class IsAdmin(permissions.BasePermission):
#     """
#     Custom permission to only allow 'admin' users.
#     """
#     def has_permission(self, request, view):
#         return request.user and (request.user.role == 'admin' or request.user.is_staff)

# class IsOwnerOrAdminOrDoctor(permissions.BasePermission):
#     """
#     Custom permission to allow:
#     - Admin/Doctor: full access to all objects.
#     - Patient: access only to their own objects (e.g., Patient profile, WoundImages, WoundAnalysis).
#     """
#     def has_object_permission(self, request, view, obj):
#         # Admins and staff have full access
#         if request.user and (request.user.role in ['admin', 'doctor'] or request.user.is_staff):
#             return True

#         # Patients can only access their own related objects
#         if request.user and request.user.role == 'patient':
#             if isinstance(obj, User): # If the object is a User instance
#                 return obj == request.user
#             elif isinstance(obj, Patient): # If the object is a Patient profile
#                 return obj.user == request.user
#             elif hasattr(obj, 'patient') and obj.patient: # If object has a 'patient' field (WoundImage, WoundAnalysis)
#                 return obj.patient.user == request.user
#         return False





from rest_framework.permissions import BasePermission

class IsAdminOrDoctor(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (u.is_staff or getattr(u, "role", None) in ["admin", "doctor"]))

class IsOwnerOrAdminOrDoctor(BasePermission):
    def has_object_permission(self, request, view, obj):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if u.is_staff or getattr(u, "role", None) in ["admin", "doctor"]:
            return True

        # obj can be Patient, Wound, WoundImage, WoundAnalysis
        patient_user = None
        if hasattr(obj, "user"):  # Patient object
            patient_user = obj.user
        elif hasattr(obj, "patient"):  # Wound object
            patient_user = getattr(obj.patient, "user", None)
        elif hasattr(obj, "wound"):  # WoundImage
            patient_user = getattr(getattr(obj, "wound", None), "patient", None)
            if patient_user:
                patient_user = getattr(patient_user, "user", None)
        elif hasattr(obj, "wound_image"):  # WoundAnalysis
            wound = getattr(obj.wound_image, "wound", None)
            patient_user = getattr(getattr(wound, "patient", None), "user", None) if wound else None

        return patient_user == u

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
