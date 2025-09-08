# # api/admin.py

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User, Patient, WoundImage, WoundAnalysis, OTP

# # Custom User Admin to display the 'role' field
# class CustomUserAdmin(UserAdmin):
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('role',)}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('role',)}),
#     )

# admin.site.register(User, CustomUserAdmin)
# admin.site.register(Patient)
# admin.site.register(WoundImage)
# admin.site.register(WoundAnalysis)
# admin.site.register(OTP)


# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import User, Patient, WoundImage, WoundAnalysis

# # Register your custom User model
# # @admin.register(User)
# # class CustomUserAdmin(UserAdmin):
# #     fieldsets = UserAdmin.fieldsets + (
# #         (('Roles', {'fields': ('role',)}),)
# #     )
# #     add_fieldsets = UserAdmin.add_fieldsets + (
# #         (('Roles', {'fields': ('role',)}),)
# #     )

# # admin.site.register(Patient)
# # admin.site.register(WoundImage)
# # admin.site.register(WoundAnalysis)





# core/admin.py
from django.contrib import admin
from .models import User, Patient, Wound, WoundImage, WoundAnalysis, AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Wound)
admin.site.register(WoundImage)
admin.site.register(WoundAnalysis)
admin.site.register(AuditLog)
