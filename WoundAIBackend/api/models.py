# # # # api/models.py

# # # import uuid
# # # from django.db import models
# # # from django.contrib.auth.models import AbstractUser
# # # from django.conf import settings
# # # from django.utils import timezone

# # # class User(AbstractUser):
# # #     """
# # #     Custom User model to include a 'role' field.
# # #     """
# # #     ROLE_CHOICES = (
# # #         ('doctor', 'Doctor'),
# # #         ('patient', 'Patient'),
# # #         ('admin', 'Admin'),
# # #     )
# # #     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

# # #     def __str__(self):
# # #         return f"{self.username} ({self.role})"

# # # class Patient(models.Model):
# # #     """
# # #     Model for patient profiles, linked to a User.
# # #     """
# # #     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
# # #     mrn_uid = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="MRN/UID (Medical Record Number/Unique ID)")
# # #     gender = models.CharField(max_length=10, blank=True, null=True)
# # #     date_of_birth = models.DateField(blank=True, null=True)
# # #     mobile_number = models.CharField(max_length=15, blank=True, null=True)
# # #     # Example co-morbidities (can be extended to a ManyToManyField to a separate Comorbidity model)
# # #     co_morbidities = models.TextField(blank=True, help_text="Comma-separated list, e.g., DM, PAD, CVI")
# # #     address = models.TextField(blank=True, null=True)
# # #     # New fields based on document
# # #     wound_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., DFU, PVD ulcer, post-op wound, trauma")
# # #     wound_location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Right Foot, Left Hand")

# # #     def __str__(self):
# # #         return f"Patient: {self.user.username} (MRN: {self.mrn_uid or 'N/A'})"

# # # class WoundImage(models.Model):
# # #     """
# # #     Model for storing wound images uploaded by patients or doctors.
# # #     """
# # #     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
# # #     image = models.ImageField(upload_to='wound_photos/')
# # #     capture_date = models.DateTimeField(auto_now_add=True)
# # #     notes = models.TextField(blank=True, null=True)
    
# # #     def __str__(self):
# # #         return f"Wound Image for {self.patient.user.username} on {self.capture_date.strftime('%Y-%m-%d')}"

# # # class WoundAnalysis(models.Model):
# # #     """
# # #     Model for storing AI analysis results for a given wound image.
# # #     """
# # #     wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name='analysis')
# # #     is_wound = models.BooleanField(default=False)
# # #     rejection_reason = models.CharField(max_length=100, blank=True, null=True)
# # #     wound_area_cm2 = models.FloatField(blank=True, null=True)
# # #     estimated_depth_mm = models.FloatField(blank=True, null=True)
# # #     estimated_distance_cm = models.FloatField(blank=True, null=True)
# # #     # New fields for AI output based on document features
# # #     healing_stage = models.CharField(max_length=100, blank=True, null=True)
# # #     tissue_type = models.CharField(max_length=100, blank=True, null=True)
# # #     exudate = models.CharField(max_length=100, blank=True, null=True)
# # #     odor = models.CharField(max_length=50, blank=True, null=True)
# # #     periwound_skin = models.CharField(max_length=100, blank=True, null=True)
# # #     potential_complications = models.JSONField(blank=True, null=True) # Stored as JSON array
# # #     recommendations = models.JSONField(blank=True, null=True) # Stored as JSON array
# # #     analysis_summary = models.TextField(blank=True, null=True)
# # #     wound_outline_coordinates = models.JSONField(blank=True, null=True) # Stored as JSON array of [x,y] pairs
# # #     analyzed_at = models.DateTimeField(auto_now_add=True)

# # #     def __str__(self):
# # #         return f"Analysis for {self.wound_image}"

# # # class OTP(models.Model):
# # #     """
# # #     Model for storing One-Time Passwords for password reset.
# # #     """
# # #     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
# # #     code = models.CharField(max_length=6)
# # #     created_at = models.DateTimeField(auto_now_add=True)
# # #     is_verified = models.BooleanField(default=False)
# # #     # OTPs expire after a certain time (e.g., 5 minutes)
# # #     expiration_time = models.DateTimeField()

# # #     def save(self, *args, **kwargs):
# # #         if not self.id:  # Only set expiration time when OTP is first created
# # #             self.expiration_time = timezone.now() + timezone.timedelta(minutes=5) # OTP valid for 5 minutes
# # #         super().save(*args, **kwargs)

# # #     def is_valid(self):
# # #         return not self.is_verified and self.expiration_time > timezone.now()

# # #     def __str__(self):
# # #         return f"OTP for {self.user.username}: {self.code}"




# # # api/models.py 
# # import uuid
# # from django.db import models
# # from django.contrib.auth.models import AbstractUser
# # from django.conf import settings
# # from django.utils import timezone

# # # class User(AbstractUser):
# # #     ROLE_CHOICES = (
# # #         ('doctor', 'Doctor'),
# # #         ('patient', 'Patient'),
# # #         ('admin', 'Admin'),
# # #     )
# # #     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

# # #     def __str__(self):
# # #         return f"{self.username} ({self.role})"

# # class Patient(models.Model):
# #     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
# #     mrn_uid = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="MRN/UID (Medical Record Number/Unique ID)")
# #     gender = models.CharField(max_length=10, blank=True, null=True)
# #     date_of_birth = models.DateField(blank=True, null=True)
# #     mobile_number = models.CharField(max_length=15, blank=True, null=True)
# #     co_morbidities = models.TextField(blank=True, help_text="Comma-separated list, e.g., DM, PAD, CVI")
# #     address = models.TextField(blank=True, null=True)
# #     wound_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., DFU, PVD ulcer, post-op wound, trauma")
# #     wound_location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Right Foot, Left Hand")

# #     def __str__(self):
# #         return f"Patient: {self.user.username} (MRN: {self.mrn_uid or 'N/A'})"

# # class WoundImage(models.Model):
# #     # patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
# #     # image = models.ImageField(upload_to='wound_photos/')
# #     # plotted_image = models.ImageField(upload_to='wound_plots/', blank=True, null=True)
# #     # capture_date = models.DateTimeField(auto_now_add=True)
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
# #     image = models.ImageField(upload_to='wound_images/')
# #     plotted_image = models.ImageField(upload_to='plotted_wound_images/', null=True, blank=True,
# #                                       help_text="Image with ML analysis plotted (e.g., 3D visualization, segmentation overlay)")
# #     uploaded_at = models.DateTimeField(auto_now_add=True)
# #     notes = models.TextField(blank=True, null=True)

# #     def __str__(self):
# #         return f"Wound Image {self.id} for {self.patient.user.username}"
    
# #     def __str__(self):
# #         return f"Wound Image for {self.patient.user.username} on {self.capture_date.strftime('%Y-%m-%d')}"

# # # class WoundAnalysis(models.Model):
# # #     wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name='analysis')
# # #     is_wound = models.BooleanField(default=False)
# # #     rejection_reason = models.CharField(max_length=100, blank=True, null=True)
# # #     wound_area_cm2 = models.FloatField(blank=True, null=True)
# # #     estimated_depth_mm = models.FloatField(blank=True, null=True)
# # #     estimated_distance_cm = models.FloatField(blank=True, null=True)
# # #     healing_stage = models.CharField(max_length=100, blank=True, null=True)
# # #     tissue_type = models.CharField(max_length=100, blank=True, null=True)
# # #     exudate = models.CharField(max_length=100, blank=True, null=True)
# # #     odor = models.CharField(max_length=50, blank=True, null=True)
# # #     periwound_skin = models.CharField(max_length=100, blank=True, null=True)
# # #     potential_complications = models.JSONField(blank=True, null=True)
# # #     recommendations = models.JSONField(blank=True, null=True)
# # #     analysis_summary = models.TextField(blank=True, null=True)
# # #     wound_outline_coordinates = models.JSONField(blank=True, null=True)
# # #     analyzed_at = models.DateTimeField(auto_now_add=True)

# # #     def __str__(self):
# # #         return f"Analysis for {self.wound_image}"

# # class OTP(models.Model):
# #     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
# #     code = models.CharField(max_length=6)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     is_verified = models.BooleanField(default=False)
# #     expiration_time = models.DateTimeField()

# #     def save(self, *args, **kwargs):
# #         if not self.id:
# #             self.expiration_time = timezone.now() + timezone.timedelta(minutes=5)
# #         super().save(*args, **kwargs)

# #     def is_valid(self):
# #         return not self.is_verified and self.expiration_time > timezone.now()

# #     def __str__(self):
# #         return f"OTP for {self.user.username}: {self.code}"
    







# # from django.db import models
# # from django.contrib.auth.models import AbstractUser, Group, Permission
# # import uuid

# # # Custom User Model with roles
# # class User(AbstractUser):
# #     # Add custom roles
# #     ROLE_CHOICES = (
# #         ('patient', 'Patient'),
# #         ('doctor', 'Doctor'),
# #         ('admin', 'Admin'),
# #     )
# #     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

# #     # Add related_name to avoid clashes with auth.User's groups and user_permissions
# #     groups = models.ManyToManyField(
# #         Group,
# #         verbose_name=('groups'),
# #         blank=True,
# #         help_text=(
# #             'The groups this user belongs to. A user will get all permissions '
# #             'granted to each of their groups.'
# #         ),
# #         related_name="wound_care_users", # Custom related_name
# #         related_query_name="wound_care_user",
# #     )
# #     user_permissions = models.ManyToManyField(
# #         Permission,
# #         verbose_name=('user permissions'),
# #         blank=True,
# #         help_text=('Specific permissions for this user.'),
# #         related_name="wound_care_users", # Custom related_name
# #         related_query_name="wound_care_user",
# #     )

# #     def __str__(self):
# #         return self.username

# # # class Patient(models.Model):
# # #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# # #     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
# # #     date_of_birth = models.DateField(null=True, blank=True)
# # #     gender = models.CharField(max_length=10, null=True, blank=True)
# # #     contact_number = models.CharField(max_length=20, null=True, blank=True)
# # #     address = models.TextField(null=True, blank=True)

# # #     def __str__(self):
# # #         return f"Patient: {self.user.username}"

# # # class WoundImage(models.Model):
# # #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# # #     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
# # #     image = models.ImageField(upload_to='wound_images/')
# # #     plotted_image = models.ImageField(upload_to='plotted_wound_images/', null=True, blank=True,
# # #                                       help_text="Image with ML analysis plotted (e.g., 3D visualization, segmentation overlay)")
# # #     uploaded_at = models.DateTimeField(auto_now_add=True)
# # #     notes = models.TextField(blank=True, null=True)

# # #     def __str__(self):
# # #         return f"Wound Image {self.id} for {self.patient.user.username}"

# # class WoundAnalysis(models.Model):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name='analysis')
# #     is_wound = models.BooleanField(default=False)
# #     rejection_reason = models.TextField(blank=True, null=True)
# #     wound_area_cm2 = models.FloatField(null=True, blank=True)
# #     estimated_depth_mm = models.FloatField(null=True, blank=True)
# #     estimated_distance_cm = models.FloatField(null=True, blank=True)
# #     healing_stage = models.CharField(max_length=100, blank=True, null=True)
# #     tissue_type = models.JSONField(max_length=100, blank=True, null=True,help_text="JSON object: {'Slough': 'X%', 'Necrosis': 'Y%', ...}")

# #     # tissue_type = models.JSONField(blank=True, null=True,
# #     #                                help_text="JSON object: {'Slough': 'X%', 'Necrosis': 'Y%', ...}")
# #     exudate = models.CharField(max_length=50, blank=True, null=True)
# #     odor = models.CharField(max_length=50, blank=True, null=True)
# #     periwound_skin = models.CharField(max_length=100, blank=True, null=True)
# #     potential_complications = models.JSONField(blank=True, null=True,
# #                                                 help_text="JSON array: ['Infection Risk', 'Delayed Healing']")
# #     recommendations = models.JSONField(blank=True, null=True,
# #                                        help_text="JSON array: ['Cleanse daily', 'Apply dressing']")
# #     analysis_summary = models.TextField(blank=True, null=True)
# #     wound_outline_coordinates = models.JSONField(blank=True, null=True,
# #                                                  help_text="JSON array of [x, y] coordinates for wound outline")
# #     analyzed_at = models.DateTimeField(auto_now_add=True)


# #     def __str__(self):
# #         return f"Analysis for Wound Image {self.wound_image.id}"








# # api/models.py
# from django.conf import settings
# from django.db import models
# from django.utils import timezone
# from django.contrib.auth.models import AbstractUser

# ROLE_CHOICES = (("admin", "Admin"), ("doctor", "Doctor"), ("patient", "Patient"))
# GENDER_CHOICES = (("male", "Male"), ("female", "Female"), ("other", "Other"))
# WOUND_TYPES = (
#     ("DFU", "Diabetic Foot Ulcer"),
#     ("PVD", "Peripheral Vascular Disease Ulcer"),
#     ("POST_OP", "Post-Operative Wound"),
#     ("TRAUMA", "Trauma"),
#     ("OTHER", "Other"),
# )

# class User(AbstractUser):
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")
#     mobile_number = models.CharField(max_length=20, blank=True, null=True)
#     hospital_id = models.CharField(max_length=100, blank=True, null=True)

#     def is_admin(self):
#         return self.is_staff or self.role == "admin"

#     def is_doctor(self):
#         return self.role == "doctor"

#     def is_patient(self):
#         return self.role == "patient"


# class Patient(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile")
#     mrn = models.CharField(max_length=64, unique=True)
#     first_name = models.CharField(max_length=80,blank=True, null=True)
#     last_name = models.CharField(max_length=80, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     gender = models.CharField(max_length=12, choices=GENDER_CHOICES, blank=True, null=True)
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     comorbidities = models.JSONField(blank=True, null=True, help_text="e.g. ['DM','PAD']")
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.mrn} - {self.first_name} {self.last_name or ''}".strip()


# class Wound(models.Model):
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="wounds")
#     wound_type = models.CharField(max_length=20, choices=WOUND_TYPES, default="OTHER")
#     body_location = models.CharField(max_length=120, blank=True, null=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_wounds")
#     created_at = models.DateTimeField(auto_now_add=True)
#     latest_status = models.CharField(max_length=120, blank=True, null=True)

#     def __str__(self):
#         return f"Wound#{self.id} ({self.wound_type}) for {self.patient}"


# def upload_wound_image_path(instance, filename):
#     # filename sanitized by Django storage backend; include MRN + timestamp
#     return f"wounds/{instance.wound.patient.mrn}/images/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{filename}"


# class WoundImage(models.Model):
#     wound = models.ForeignKey(Wound, on_delete=models.CASCADE, related_name="images")
#     image = models.ImageField(upload_to=upload_wound_image_path, blank=True, null=True)
#     plotted_image = models.ImageField(upload_to=upload_wound_image_path, blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)
#     uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_wound_images")
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     width_px = models.IntegerField(blank=True, null=True)
#     height_px = models.IntegerField(blank=True, null=True)

#     def __str__(self):
#         return f"WoundImage#{self.id} for Wound#{self.wound_id}"


# class WoundAnalysis(models.Model):
#     wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name="analysis")
#     is_wound = models.BooleanField(default=True)
#     rejection_reason = models.CharField(max_length=255, blank=True, null=True)
#     wound_area_cm2 = models.FloatField(blank=True, null=True)
#     length_cm = models.FloatField(blank=True, null=True)
#     width_cm = models.FloatField(blank=True, null=True)
#     estimated_depth_mm = models.FloatField(blank=True, null=True)
#     perimeter_cm = models.FloatField(blank=True, null=True)
#     volume_cm3 = models.FloatField(blank=True, null=True)
#     tissue_type = models.JSONField(blank=True, null=True)
#     exudate = models.CharField(max_length=120, blank=True, null=True)
#     odor = models.CharField(max_length=120, blank=True, null=True)
#     periwound_skin = models.CharField(max_length=120, blank=True, null=True)
#     healing_stage = models.CharField(max_length=120, blank=True, null=True)
#     classification = models.CharField(max_length=120, blank=True, null=True)
#     healing_index = models.FloatField(blank=True, null=True)
#     recommendations = models.JSONField(blank=True, null=True)
#     potential_complications = models.JSONField(blank=True, null=True)
#     analysis_summary = models.TextField(blank=True, null=True)
#     wound_outline_coordinates = models.JSONField(blank=True, null=True)
#     analyzed_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Analysis for WoundImage#{self.wound_image_id}"


# class AuditLog(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#     action = models.CharField(max_length=128)
#     entity = models.CharField(max_length=128)
#     entity_id = models.CharField(max_length=64, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     meta = models.JSONField(blank=True, null=True)

#     class Meta:
#         ordering = ["-timestamp"]






# # api/models.py
# import uuid
# import os
# from django.conf import settings
# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# def reports_upload_path(instance, filename):
#     ext = filename.split('.')[-1]
#     filename = f"{uuid.uuid4()}.{ext}"
#     return os.path.join("reports", str(instance.hospital_id or "global"), filename)

# # class AuditLog(models.Model):
# #     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
# #     action = models.CharField(max_length=128)
# #     object_type = models.CharField(max_length=128, null=True, blank=True)
# #     object_id = models.CharField(max_length=64, null=True, blank=True)
# #     details = models.JSONField(null=True, blank=True)
# #     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.timestamp.isoformat()} | {self.user} | {self.action}"

# class Report(models.Model):
#     STATUS_CHOICES = (("draft", "Draft"), ("uploaded", "Uploaded"), ("shared", "Shared"))

#     id = models.AutoField(primary_key=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_reports")
#     patient = models.ForeignKey("api.Patient", on_delete=models.CASCADE, related_name="reports")
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     file = models.FileField(upload_to=reports_upload_path, null=True, blank=True)
#     # file_base64 used only if client queues base64 payload; remove after upload
#     file_base64 = models.TextField(null=True, blank=True)
#     shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="shared_reports", blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     hospital_id = models.CharField(max_length=64, db_index=True)
#     status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="draft")

#     def __str__(self):
#         return f"Report {self.id} - {self.title}"

# class Prescription(models.Model):
#     STATUS_CHOICES = (("pending", "Pending"), ("ai_generated", "AI Generated"), ("approved", "Approved"), ("rejected", "Rejected"))

#     id = models.AutoField(primary_key=True)
#     requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requested_prescriptions")
#     patient = models.ForeignKey("api.Patient", on_delete=models.CASCADE, related_name="prescriptions")
#     wound = models.ForeignKey("api.Wound", on_delete=models.SET_NULL, null=True, blank=True)
#     ai_suggestion = models.JSONField(null=True, blank=True)
#     clinician_review = models.JSONField(null=True, blank=True)
#     status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="pending")
#     model_version = models.CharField(max_length=64, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     hospital_id = models.CharField(max_length=64, db_index=True)

#     def __str__(self):
#         return f"Prescription {self.id} for patient {self.patient_id}"








# api/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# ------------------ CHOICES ------------------ #
ROLE_CHOICES = (
    ("admin", "Admin"),
    ("doctor", "Doctor"),
    ("patient", "Patient"),
)

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
)

WOUND_TYPES = (
    ("DFU", "Diabetic Foot Ulcer"),
    ("PVD", "Peripheral Vascular Disease Ulcer"),
    ("POST_OP", "Post-Operative Wound"),
    ("TRAUMA", "Trauma"),
    ("OTHER", "Other"),
)


# ------------------ USER ------------------ #
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    hospital_id = models.CharField(max_length=100, blank=True, null=True)

    def is_admin(self):
        return self.is_staff or self.role == "admin"

    def is_doctor(self):
        return self.role == "doctor"

    def is_patient(self):
        return self.role == "patient"

    def __str__(self):
        return f"{self.username} ({self.role})"


# ------------------ PATIENT ------------------ #
class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    mrn = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=12, choices=GENDER_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    comorbidities = models.JSONField(blank=True, null=True, help_text="e.g. ['DM','PAD']")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Patients must select doctors at signup
    doctors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_patients",
        limit_choices_to={"role": "doctor"},
        blank=True,
    )

    def __str__(self):
        return f"{self.mrn} - {self.first_name or ''} {self.last_name or ''}".strip()


# ------------------ WOUND ------------------ #
class Wound(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="wounds")
    wound_type = models.CharField(max_length=20, choices=WOUND_TYPES, default="OTHER")
    body_location = models.CharField(max_length=120, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_wounds",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    latest_status = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"Wound#{self.id} ({self.wound_type}) for {self.patient}"


def upload_wound_image_path(instance, filename):
    return f"wounds/{instance.wound.patient.mrn}/images/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{filename}"


# ------------------ WOUND IMAGE ------------------ #
class WoundImage(models.Model):
    wound = models.ForeignKey(Wound, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_wound_image_path, blank=True, null=True)
    plotted_image = models.ImageField(upload_to=upload_wound_image_path, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_wound_images",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width_px = models.IntegerField(blank=True, null=True)
    height_px = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"WoundImage#{self.id} for Wound#{self.wound_id}"


# ------------------ WOUND ANALYSIS ------------------ #
class WoundAnalysis(models.Model):
    wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name="analysis")
    is_wound = models.BooleanField(default=True)
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    wound_area_cm2 = models.FloatField(blank=True, null=True)
    length_cm = models.FloatField(blank=True, null=True)
    width_cm = models.FloatField(blank=True, null=True)
    estimated_depth_mm = models.FloatField(blank=True, null=True)
    perimeter_cm = models.FloatField(blank=True, null=True)
    volume_cm3 = models.FloatField(blank=True, null=True)
    tissue_type = models.JSONField(blank=True, null=True)
    exudate = models.CharField(max_length=120, blank=True, null=True)
    odor = models.CharField(max_length=120, blank=True, null=True)
    periwound_skin = models.CharField(max_length=120, blank=True, null=True)
    healing_stage = models.CharField(max_length=120, blank=True, null=True)
    classification = models.CharField(max_length=120, blank=True, null=True)
    healing_index = models.FloatField(blank=True, null=True)
    recommendations = models.JSONField(blank=True, null=True)
    potential_complications = models.JSONField(blank=True, null=True)
    analysis_summary = models.TextField(blank=True, null=True)
    wound_outline_coordinates = models.JSONField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for WoundImage#{self.wound_image_id}"


# ------------------ AUDIT LOG ------------------ #
class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=128)
    entity = models.CharField(max_length=128)
    entity_id = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp.isoformat()} | {self.user} | {self.action}"







# api/models.py
import uuid
import os
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def reports_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("reports", str(instance.hospital_id or "global"), filename)


# ------------------ REPORT ------------------ #
class Report(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("uploaded", "Uploaded"),
        ("shared", "Shared"),
    )

    id = models.AutoField(primary_key=True)

    # Who created the report (usually the patient, could be a doctor too)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_reports",
    )

    # Report belongs to a patient
    patient = models.ForeignKey(
        "api.Patient",
        on_delete=models.CASCADE,
        related_name="reports",
    )

    # NEW ✅: link the doctor(s) the patient shared this report with
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="shared_reports",
        blank=True,
        limit_choices_to={"role": "doctor"},
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=reports_upload_path, null=True, blank=True)
    file_base64 = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    hospital_id = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="draft")

    def __str__(self):
        return f"Report {self.id} - {self.title}"


# ------------------ PRESCRIPTION ------------------ #
class Prescription(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("ai_generated", "AI Generated"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    id = models.AutoField(primary_key=True)

    # Requested by patient (through app)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requested_prescriptions",
    )

    # The patient for whom this prescription is generated
    patient = models.ForeignKey(
        "api.Patient",
        on_delete=models.CASCADE,
        related_name="prescriptions",
    )

    # The doctor assigned to handle this prescription
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_prescriptions",
        limit_choices_to={"role": "doctor"},
        null=True,
        blank=True,
    )

    # Optional: wound context
    wound = models.ForeignKey(
        "api.Wound",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # AI and clinician input
    ai_suggestion = models.JSONField(null=True, blank=True)
    clinician_review = models.JSONField(null=True, blank=True)

    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="pending")
    model_version = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hospital_id = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return f"Prescription {self.id} for patient {self.patient_id}"
