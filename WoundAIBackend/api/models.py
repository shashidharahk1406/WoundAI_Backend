# # api/models.py

# import uuid
# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.conf import settings
# from django.utils import timezone

# class User(AbstractUser):
#     """
#     Custom User model to include a 'role' field.
#     """
#     ROLE_CHOICES = (
#         ('doctor', 'Doctor'),
#         ('patient', 'Patient'),
#         ('admin', 'Admin'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

#     def __str__(self):
#         return f"{self.username} ({self.role})"

# class Patient(models.Model):
#     """
#     Model for patient profiles, linked to a User.
#     """
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
#     mrn_uid = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="MRN/UID (Medical Record Number/Unique ID)")
#     gender = models.CharField(max_length=10, blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     mobile_number = models.CharField(max_length=15, blank=True, null=True)
#     # Example co-morbidities (can be extended to a ManyToManyField to a separate Comorbidity model)
#     co_morbidities = models.TextField(blank=True, help_text="Comma-separated list, e.g., DM, PAD, CVI")
#     address = models.TextField(blank=True, null=True)
#     # New fields based on document
#     wound_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., DFU, PVD ulcer, post-op wound, trauma")
#     wound_location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Right Foot, Left Hand")

#     def __str__(self):
#         return f"Patient: {self.user.username} (MRN: {self.mrn_uid or 'N/A'})"

# class WoundImage(models.Model):
#     """
#     Model for storing wound images uploaded by patients or doctors.
#     """
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
#     image = models.ImageField(upload_to='wound_photos/')
#     capture_date = models.DateTimeField(auto_now_add=True)
#     notes = models.TextField(blank=True, null=True)
    
#     def __str__(self):
#         return f"Wound Image for {self.patient.user.username} on {self.capture_date.strftime('%Y-%m-%d')}"

# class WoundAnalysis(models.Model):
#     """
#     Model for storing AI analysis results for a given wound image.
#     """
#     wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name='analysis')
#     is_wound = models.BooleanField(default=False)
#     rejection_reason = models.CharField(max_length=100, blank=True, null=True)
#     wound_area_cm2 = models.FloatField(blank=True, null=True)
#     estimated_depth_mm = models.FloatField(blank=True, null=True)
#     estimated_distance_cm = models.FloatField(blank=True, null=True)
#     # New fields for AI output based on document features
#     healing_stage = models.CharField(max_length=100, blank=True, null=True)
#     tissue_type = models.CharField(max_length=100, blank=True, null=True)
#     exudate = models.CharField(max_length=100, blank=True, null=True)
#     odor = models.CharField(max_length=50, blank=True, null=True)
#     periwound_skin = models.CharField(max_length=100, blank=True, null=True)
#     potential_complications = models.JSONField(blank=True, null=True) # Stored as JSON array
#     recommendations = models.JSONField(blank=True, null=True) # Stored as JSON array
#     analysis_summary = models.TextField(blank=True, null=True)
#     wound_outline_coordinates = models.JSONField(blank=True, null=True) # Stored as JSON array of [x,y] pairs
#     analyzed_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Analysis for {self.wound_image}"

# class OTP(models.Model):
#     """
#     Model for storing One-Time Passwords for password reset.
#     """
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
#     code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)
#     # OTPs expire after a certain time (e.g., 5 minutes)
#     expiration_time = models.DateTimeField()

#     def save(self, *args, **kwargs):
#         if not self.id:  # Only set expiration time when OTP is first created
#             self.expiration_time = timezone.now() + timezone.timedelta(minutes=5) # OTP valid for 5 minutes
#         super().save(*args, **kwargs)

#     def is_valid(self):
#         return not self.is_verified and self.expiration_time > timezone.now()

#     def __str__(self):
#         return f"OTP for {self.user.username}: {self.code}"




# api/models.py 
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# class User(AbstractUser):
#     ROLE_CHOICES = (
#         ('doctor', 'Doctor'),
#         ('patient', 'Patient'),
#         ('admin', 'Admin'),
#     )
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

#     def __str__(self):
#         return f"{self.username} ({self.role})"

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    mrn_uid = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="MRN/UID (Medical Record Number/Unique ID)")
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    co_morbidities = models.TextField(blank=True, help_text="Comma-separated list, e.g., DM, PAD, CVI")
    address = models.TextField(blank=True, null=True)
    wound_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., DFU, PVD ulcer, post-op wound, trauma")
    wound_location = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Right Foot, Left Hand")

    def __str__(self):
        return f"Patient: {self.user.username} (MRN: {self.mrn_uid or 'N/A'})"

class WoundImage(models.Model):
    # patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
    # image = models.ImageField(upload_to='wound_photos/')
    # plotted_image = models.ImageField(upload_to='wound_plots/', blank=True, null=True)
    # capture_date = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
    image = models.ImageField(upload_to='wound_images/')
    plotted_image = models.ImageField(upload_to='plotted_wound_images/', null=True, blank=True,
                                      help_text="Image with ML analysis plotted (e.g., 3D visualization, segmentation overlay)")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Wound Image {self.id} for {self.patient.user.username}"
    
    def __str__(self):
        return f"Wound Image for {self.patient.user.username} on {self.capture_date.strftime('%Y-%m-%d')}"

# class WoundAnalysis(models.Model):
#     wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name='analysis')
#     is_wound = models.BooleanField(default=False)
#     rejection_reason = models.CharField(max_length=100, blank=True, null=True)
#     wound_area_cm2 = models.FloatField(blank=True, null=True)
#     estimated_depth_mm = models.FloatField(blank=True, null=True)
#     estimated_distance_cm = models.FloatField(blank=True, null=True)
#     healing_stage = models.CharField(max_length=100, blank=True, null=True)
#     tissue_type = models.CharField(max_length=100, blank=True, null=True)
#     exudate = models.CharField(max_length=100, blank=True, null=True)
#     odor = models.CharField(max_length=50, blank=True, null=True)
#     periwound_skin = models.CharField(max_length=100, blank=True, null=True)
#     potential_complications = models.JSONField(blank=True, null=True)
#     recommendations = models.JSONField(blank=True, null=True)
#     analysis_summary = models.TextField(blank=True, null=True)
#     wound_outline_coordinates = models.JSONField(blank=True, null=True)
#     analyzed_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Analysis for {self.wound_image}"

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.expiration_time = timezone.now() + timezone.timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_verified and self.expiration_time > timezone.now()

    def __str__(self):
        return f"OTP for {self.user.username}: {self.code}"
    







from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid

# Custom User Model with roles
class User(AbstractUser):
    # Add custom roles
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    # Add related_name to avoid clashes with auth.User's groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="wound_care_users", # Custom related_name
        related_query_name="wound_care_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="wound_care_users", # Custom related_name
        related_query_name="wound_care_user",
    )

    def __str__(self):
        return self.username

# class Patient(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
#     date_of_birth = models.DateField(null=True, blank=True)
#     gender = models.CharField(max_length=10, null=True, blank=True)
#     contact_number = models.CharField(max_length=20, null=True, blank=True)
#     address = models.TextField(null=True, blank=True)

#     def __str__(self):
#         return f"Patient: {self.user.username}"

# class WoundImage(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='wound_images')
#     image = models.ImageField(upload_to='wound_images/')
#     plotted_image = models.ImageField(upload_to='plotted_wound_images/', null=True, blank=True,
#                                       help_text="Image with ML analysis plotted (e.g., 3D visualization, segmentation overlay)")
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"Wound Image {self.id} for {self.patient.user.username}"

class WoundAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wound_image = models.OneToOneField(WoundImage, on_delete=models.CASCADE, related_name='analysis')
    is_wound = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    wound_area_cm2 = models.FloatField(null=True, blank=True)
    estimated_depth_mm = models.FloatField(null=True, blank=True)
    estimated_distance_cm = models.FloatField(null=True, blank=True)
    healing_stage = models.CharField(max_length=100, blank=True, null=True)
    tissue_type = models.JSONField(max_length=100, blank=True, null=True,help_text="JSON object: {'Slough': 'X%', 'Necrosis': 'Y%', ...}")

    # tissue_type = models.JSONField(blank=True, null=True,
    #                                help_text="JSON object: {'Slough': 'X%', 'Necrosis': 'Y%', ...}")
    exudate = models.CharField(max_length=50, blank=True, null=True)
    odor = models.CharField(max_length=50, blank=True, null=True)
    periwound_skin = models.CharField(max_length=100, blank=True, null=True)
    potential_complications = models.JSONField(blank=True, null=True,
                                                help_text="JSON array: ['Infection Risk', 'Delayed Healing']")
    recommendations = models.JSONField(blank=True, null=True,
                                       help_text="JSON array: ['Cleanse daily', 'Apply dressing']")
    analysis_summary = models.TextField(blank=True, null=True)
    wound_outline_coordinates = models.JSONField(blank=True, null=True,
                                                 help_text="JSON array of [x, y] coordinates for wound outline")
    analyzed_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Analysis for Wound Image {self.wound_image.id}"
