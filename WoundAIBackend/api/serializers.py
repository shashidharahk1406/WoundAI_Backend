# # # api/serializers.py

# from rest_framework import serializers
# # from rest_framework.authtoken.models import Token
# # from django.contrib.auth import authenticate
# # from .models import Patient, WoundImage, WoundAnalysis, User, OTP
# # import re # For email validation

# # class UserSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for User registration.
# #     """
# #     password = serializers.CharField(write_only=True, required=True, min_length=8)
# #     password2 = serializers.CharField(write_only=True, required=True, min_length=8) # For password confirmation
# #     role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

# #     class Meta:
# #         model = User
# #         fields = ['id', 'username', 'email', 'role', 'password', 'password2']
# #         read_only_fields = ['id']

# #     def validate_email(self, value):
# #         # Basic email format validation
# #         if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
# #             raise serializers.ValidationError("Invalid email format.")
# #         if User.objects.filter(email=value).exists():
# #             raise serializers.ValidationError("This email is already registered.")
# #         return value

# #     def validate_username(self, value):
# #         if User.objects.filter(username=value).exists():
# #             raise serializers.ValidationError("This username is already taken.")
# #         return value

# #     def validate(self, data):
# #         if data['password'] != data['password2']:
# #             raise serializers.ValidationError({"password": "Password fields didn't match."})
# #         return data

# #     def create(self, validated_data):
# #         validated_data.pop('password2') # Remove password2 before creating user
# #         user = User.objects.create_user(
# #             username=validated_data['username'],
# #             email=validated_data['email'],
# #             password=validated_data['password'],
# #             role=validated_data.get('role', 'patient')
# #         )
# #         return user

# # class LoginSerializer(serializers.Serializer):
# #     """
# #     Serializer for user login.
# #     """
# #     username = serializers.CharField(required=True)
# #     password = serializers.CharField(write_only=True, required=True)

# #     def validate(self, data):
# #         username = data.get('username')
# #         password = data.get('password')

# #         if username and password:
# #             user = authenticate(request=self.context.get('request'), username=username, password=password)
# #             if not user:
# #                 raise serializers.ValidationError("Invalid login credentials.", code='authorization')
# #         else:
# #             raise serializers.ValidationError("Must include 'username' and 'password'.", code='authorization')

# #         data['user'] = user
# #         return data

# # class PatientSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for Patient profiles.
# #     Nested User serializer for patient_profile creation if needed.
# #     """
# #     user_info = UserSerializer(source='user', read_only=True) # Display user info linked to patient

# #     class Meta:
# #         model = Patient
# #         fields = [
# #             'id', 'user', 'user_info', 'mrn_uid', 'gender', 'date_of_birth',
# #             'mobile_number', 'co_morbidities', 'wound_type', 'wound_location'
# #         ]
# #         read_only_fields = ['user'] # User field will be set by the view for current user or admin

# #     def create(self, validated_data):
# #         # The user is set in the view based on permissions (authenticated user or admin)
# #         return super().create(validated_data)


# # class WoundAnalysisSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for WoundAnalysis results.
# #     """
# #     class Meta:
# #         model = WoundAnalysis
# #         fields = '__all__'
# #         read_only_fields = ['wound_image', 'analyzed_at']

# # class WoundImageSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for WoundImage, including nested WoundAnalysis.
# #     """
# #     analysis = WoundAnalysisSerializer(read_only=True) # Nested analysis serializer

# #     class Meta:
# #         model = WoundImage
# #         fields = ['id', 'patient', 'image', 'capture_date', 'notes', 'analysis']
# #         read_only_fields = ['capture_date']

# class ForgotPasswordSerializer(serializers.Serializer):
#     """
#     Serializer for requesting a password reset OTP.
#     """
#     email = serializers.EmailField(required=True)

#     def validate_email(self, value):
#         try:
#             user = User.objects.get(email=value)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("No user found with this email address.")
#         self.user = user # Store user object for later use in view
#         return value

# class ResetPasswordSerializer(serializers.Serializer):
#     """
#     Serializer for resetting password using OTP.
#     """
#     email = serializers.EmailField(required=True)
#     otp = serializers.CharField(required=True, max_length=6)
#     new_password = serializers.CharField(write_only=True, required=True, min_length=8)
#     confirm_new_password = serializers.CharField(write_only=True, required=True, min_length=8)

#     def validate(self, data):
#         email = data.get('email')
#         otp_code = data.get('otp')
#         new_password = data.get('new_password')
#         confirm_new_password = data.get('confirm_new_password')

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("No user found with this email address.")

#         # Check if new passwords match
#         if new_password != confirm_new_password:
#             raise serializers.ValidationError({"new_password": "New passwords do not match."})

#         # Check OTP validity
#         try:
#             otp = OTP.objects.get(user=user, code=otp_code, is_verified=False)
#             if not otp.is_valid():
#                 raise serializers.ValidationError("Invalid or expired OTP.")
#         except OTP.DoesNotExist:
#             raise serializers.ValidationError("Invalid or expired OTP.")
        
#         data['user'] = user
#         data['otp_instance'] = otp # Store OTP instance for verification
#         return data





# from rest_framework import serializers
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate
# from .models import Patient, WoundImage, WoundAnalysis, User, OTP
# import re

# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, min_length=8)
#     password2 = serializers.CharField(write_only=True, required=True, min_length=8)
#     role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'role', 'password', 'password2']
#         read_only_fields = ['id']

#     def validate_email(self, value):
#         if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
#             raise serializers.ValidationError("Invalid email format.")
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("This email is already registered.")
#         return value

#     def validate_username(self, value):
#         if User.objects.filter(username=value).exists():
#             raise serializers.ValidationError("This username is already taken.")
#         return value

#     def validate(self, data):
#         if data['password'] != data['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return data

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password'],
#             role=validated_data.get('role', 'patient')
#         )
#         return user

# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(write_only=True, required=True)

#     def validate(self, data):
#         username = data.get('username')
#         password = data.get('password')

#         if username and password:
#             user = authenticate(request=self.context.get('request'), username=username, password=password)
#             if not user:
#                 raise serializers.ValidationError("Invalid login credentials.", code='authorization')
#         else:
#             raise serializers.ValidationError("Must include 'username' and 'password'.", code='authorization')

#         data['user'] = user
#         return data

# class PatientSerializer(serializers.ModelSerializer):
#     user_info = UserSerializer(source='user', read_only=True)

#     class Meta:
#         model = Patient
#         fields = [
#             'id', 'user', 'user_info', 'mrn_uid', 'gender', 'date_of_birth',
#             'mobile_number', 'co_morbidities', 'wound_type', 'wound_location'
#         ]
#         read_only_fields = ['user']

#     def create(self, validated_data):
#         return super().create(validated_data)


# class WoundAnalysisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WoundAnalysis
#         fields = '__all__'
#         read_only_fields = ['wound_image', 'analyzed_at']

# class WoundImageSerializer(serializers.ModelSerializer):
#     analysis = WoundAnalysisSerializer(read_only=True)
#     plotted_image_url = serializers.ImageField(source='plotted_image', read_only=True)

#     class Meta:
#         model = WoundImage
#         fields = ['id', 'patient', 'image', 'plotted_image_url', 'capture_date', 'notes', 'analysis']
#         read_only_fields = ['capture_date']

# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)

#     def validate_email(self, value):
#         try:
#             user = User.objects.get(email=value)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("No user found with this email address.")
#         self.user = user
#         return value

# class ResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#     otp = serializers.CharField(required=True, max_length=6)
#     new_password = serializers.CharField(write_only=True, required=True, min_length=8)
#     confirm_new_password = serializers.CharField(write_only=True, required=True, min_length=8)

#     def validate(self, data):
#         email = data.get('email')
#         otp_code = data.get('otp')
#         new_password = data.get('new_password')
#         confirm_new_password = data.get('confirm_new_password')

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("No user found with this email address.")

#         if new_password != confirm_new_password:
#             raise serializers.ValidationError({"new_password": "New passwords do not match."})

#         try:
#             otp = OTP.objects.get(user=user, code=otp_code, is_verified=False)
#             if not otp.is_valid():
#                 raise serializers.ValidationError("Invalid or expired OTP.")
#         except OTP.DoesNotExist:
#             raise serializers.ValidationError("Invalid or expired OTP.")
        
#         data['user'] = user
#         data['otp_instance'] = otp
#         return data
    




#     from rest_framework import serializers
# from .models import User, Patient, WoundImage, WoundAnalysis
# from rest_framework.authtoken.models import Token # For user registration

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'role']

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email', ''),
#             password=validated_data['password'],
#             role=validated_data.get('role', 'patient')
#         )
#         Token.objects.create(user=user) # Automatically create a token for the new user
#         return user

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'role', 'is_staff']
#         read_only_fields = ['role', 'is_staff'] # Roles should be set by admin, not user on signup

# class PatientSerializer(serializers.ModelSerializer):
#     user = UserSerializer(read_only=True) # Nested user serializer for patient profile

#     class Meta:
#         model = Patient
#         fields = '__all__'

# class WoundAnalysisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WoundAnalysis
#         fields = '__all__'
#         read_only_fields = '__all__' # Analysis is generated by ML, not directly editable via API

# class WoundImageSerializer(serializers.ModelSerializer):
#     # Use PrimaryKeyRelatedField for patient to allow patient ID (UUID) in request
#     patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
#     analysis = WoundAnalysisSerializer(read_only=True) # Nested analysis serializer

#     class Meta:
#         model = WoundImage
#         fields = ['id', 'patient', 'image', 'plotted_image', 'uploaded_at', 'notes', 'analysis']
#         read_only_fields = ['plotted_image', 'uploaded_at', 'analysis'] # These are generated/auto-set

#     def to_representation(self, instance):
#         # Override to_representation to return full URL for image fields
#         representation = super().to_representation(instance)
#         request = self.context.get('request')
#         if request is not None:
#             if instance.image:
#                 representation['image'] = request.build_absolute_uri(instance.image.url)
#             if instance.plotted_image:
#                 representation['plotted_image'] = request.build_absolute_uri(instance.plotted_image.url)
#         return representation





# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Patient, Wound, WoundImage, WoundAnalysis

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "mobile_number", "hospital_id", "is_staff"]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "mobile_number", "hospital_id"]


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(source="user", queryset=User.objects.all(), write_only=True, required=False)

    class Meta:
        model = Patient
        fields = ["id", "mrn", "first_name", "last_name", "dob", "gender", "phone", "address", "comorbidities", "notes", "user", "user_id"]

    def validate_mrn(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("MRN is required")
        return value.strip()


class WoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wound
        fields = ["id", "patient", "wound_type", "body_location", "latest_status", "created_at"]


class WoundImageCreateSerializer(serializers.ModelSerializer):
    image_base64 = serializers.CharField(write_only=True, required=True, help_text="data:image/jpeg;base64,<...>")
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = WoundImage
        fields = ["id", "wound", "image_base64", "notes"]

    def validate(self, data):
        # ensure wound exists and required fields are present
        if "wound" not in data:
            raise serializers.ValidationError({"wound": "Wound id is required."})
        return data

    def create(self, validated_data):
        from .utils import decode_base64_to_contentfile, get_image_size
        image_b64 = validated_data.pop("image_base64")
        content_file, ext = decode_base64_to_contentfile(image_b64)
        wound_image = WoundImage.objects.create(**validated_data, image=content_file)
        try:
            w, h = get_image_size(wound_image.image.path)
            wound_image.width_px = w
            wound_image.height_px = h
            wound_image.save(update_fields=["width_px", "height_px"])
        except Exception:
            # ignore size extraction failures
            pass
        return wound_image


class WoundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoundImage
        fields = ["id", "wound", "image", "plotted_image", "notes", "uploaded_by", "uploaded_at", "width_px", "height_px"]


class WoundAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoundAnalysis
        fields = "__all__"








# api/serializers.py
import base64
import imghdr
import io
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.conf import settings
from .models import Report, Prescription, AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"

class ReportSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.id")
    file = serializers.FileField(required=False, allow_null=True)
    file_base64 = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Report
        fields = ["id", "created_by", "patient", "title", "description", "file", "file_base64", "shared_with", "created_at", "hospital_id", "status"]
        read_only_fields = ["id", "created_at", "status"]

    def validate(self, data):
        # Ensure hospital_id consistency
        request = self.context.get("request")
        if request and not data.get("hospital_id"):
            data["hospital_id"] = getattr(request.user, "hospital_id", None)
        return data

    def create(self, validated_data):
        file_b64 = validated_data.pop("file_base64", None)
        request = self.context.get("request")
        user = request.user if request else None

        report = Report.objects.create(created_by=user, **validated_data)

        # If base64 file provided (queued offline), decode & save
        if file_b64:
            # expected format: data:application/pdf;base64,JV...
            if "," in file_b64:
                header, b64data = file_b64.split(",", 1)
            else:
                b64data = file_b64
            try:
                decoded = base64.b64decode(b64data)
                # create a file name: uuid + extension guessed from header or default pdf
                ext = "pdf"
                if header and "image" in header:
                    # try to guess image ext
                    guessed = imghdr.what(None, decoded)
                    if guessed:
                        ext = guessed
                filename = f"report_{uuid.uuid4()}.{ext}"
                report.file.save(filename, ContentFile(decoded), save=True)
                report.file_base64 = None
                report.status = "uploaded"
                report.save()
            except Exception as e:
                # Keep file_base64 for retry later (client-side will queue again)
                report.file_base64 = validated_data.get("file_base64")
                report.status = "draft"
                report.save()
        return report

class ReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "title", "patient", "created_at", "status", "file"]

class PrescriptionSerializer(serializers.ModelSerializer):
    requested_by = serializers.ReadOnlyField(source="requested_by.id")
    ai_suggestion = serializers.JSONField(read_only=True)
    clinician_review = serializers.JSONField(required=False)

    class Meta:
        model = Prescription
        fields = ["id", "requested_by", "patient", "wound", "ai_suggestion", "clinician_review", "status", "model_version", "created_at", "hospital_id"]
        read_only_fields = ["id", "ai_suggestion", "status", "model_version", "created_at"]

class PrescriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["patient", "wound"]

    def create(self, validated_data):
        request = self.context.get("request")
        p = Prescription.objects.create(
            requested_by=request.user,
            hospital_id=getattr(request.user, "hospital_id", None),
            **validated_data
        )
        return p
