# # api/serializers.py

from rest_framework import serializers
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import authenticate
# from .models import Patient, WoundImage, WoundAnalysis, User, OTP
# import re # For email validation

# class UserSerializer(serializers.ModelSerializer):
#     """
#     Serializer for User registration.
#     """
#     password = serializers.CharField(write_only=True, required=True, min_length=8)
#     password2 = serializers.CharField(write_only=True, required=True, min_length=8) # For password confirmation
#     role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'role', 'password', 'password2']
#         read_only_fields = ['id']

#     def validate_email(self, value):
#         # Basic email format validation
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
#         validated_data.pop('password2') # Remove password2 before creating user
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password'],
#             role=validated_data.get('role', 'patient')
#         )
#         return user

# class LoginSerializer(serializers.Serializer):
#     """
#     Serializer for user login.
#     """
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
#     """
#     Serializer for Patient profiles.
#     Nested User serializer for patient_profile creation if needed.
#     """
#     user_info = UserSerializer(source='user', read_only=True) # Display user info linked to patient

#     class Meta:
#         model = Patient
#         fields = [
#             'id', 'user', 'user_info', 'mrn_uid', 'gender', 'date_of_birth',
#             'mobile_number', 'co_morbidities', 'wound_type', 'wound_location'
#         ]
#         read_only_fields = ['user'] # User field will be set by the view for current user or admin

#     def create(self, validated_data):
#         # The user is set in the view based on permissions (authenticated user or admin)
#         return super().create(validated_data)


# class WoundAnalysisSerializer(serializers.ModelSerializer):
#     """
#     Serializer for WoundAnalysis results.
#     """
#     class Meta:
#         model = WoundAnalysis
#         fields = '__all__'
#         read_only_fields = ['wound_image', 'analyzed_at']

# class WoundImageSerializer(serializers.ModelSerializer):
#     """
#     Serializer for WoundImage, including nested WoundAnalysis.
#     """
#     analysis = WoundAnalysisSerializer(read_only=True) # Nested analysis serializer

#     class Meta:
#         model = WoundImage
#         fields = ['id', 'patient', 'image', 'capture_date', 'notes', 'analysis']
#         read_only_fields = ['capture_date']

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset OTP.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        self.user = user # Store user object for later use in view
        return value

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password using OTP.
    """
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

        # Check if new passwords match
        if new_password != confirm_new_password:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})

        # Check OTP validity
        try:
            otp = OTP.objects.get(user=user, code=otp_code, is_verified=False)
            if not otp.is_valid():
                raise serializers.ValidationError("Invalid or expired OTP.")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP.")
        
        data['user'] = user
        data['otp_instance'] = otp # Store OTP instance for verification
        return data





from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Patient, WoundImage, WoundAnalysis, User, OTP
import re

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'password2']
        read_only_fields = ['id']

    def validate_email(self, value):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'patient')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid login credentials.", code='authorization')
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.", code='authorization')

        data['user'] = user
        return data

class PatientSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'user_info', 'mrn_uid', 'gender', 'date_of_birth',
            'mobile_number', 'co_morbidities', 'wound_type', 'wound_location'
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        return super().create(validated_data)


class WoundAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoundAnalysis
        fields = '__all__'
        read_only_fields = ['wound_image', 'analyzed_at']

class WoundImageSerializer(serializers.ModelSerializer):
    analysis = WoundAnalysisSerializer(read_only=True)
    plotted_image_url = serializers.ImageField(source='plotted_image', read_only=True)

    class Meta:
        model = WoundImage
        fields = ['id', 'patient', 'image', 'plotted_image_url', 'capture_date', 'notes', 'analysis']
        read_only_fields = ['capture_date']

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")
        self.user = user
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})

        try:
            otp = OTP.objects.get(user=user, code=otp_code, is_verified=False)
            if not otp.is_valid():
                raise serializers.ValidationError("Invalid or expired OTP.")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP.")
        
        data['user'] = user
        data['otp_instance'] = otp
        return data
    




    from rest_framework import serializers
from .models import User, Patient, WoundImage, WoundAnalysis
from rest_framework.authtoken.models import Token # For user registration

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='patient')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'patient')
        )
        Token.objects.create(user=user) # Automatically create a token for the new user
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_staff']
        read_only_fields = ['role', 'is_staff'] # Roles should be set by admin, not user on signup

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Nested user serializer for patient profile

    class Meta:
        model = Patient
        fields = '__all__'

class WoundAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = WoundAnalysis
        fields = '__all__'
        read_only_fields = '__all__' # Analysis is generated by ML, not directly editable via API

class WoundImageSerializer(serializers.ModelSerializer):
    # Use PrimaryKeyRelatedField for patient to allow patient ID (UUID) in request
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    analysis = WoundAnalysisSerializer(read_only=True) # Nested analysis serializer

    class Meta:
        model = WoundImage
        fields = ['id', 'patient', 'image', 'plotted_image', 'uploaded_at', 'notes', 'analysis']
        read_only_fields = ['plotted_image', 'uploaded_at', 'analysis'] # These are generated/auto-set

    def to_representation(self, instance):
        # Override to_representation to return full URL for image fields
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request is not None:
            if instance.image:
                representation['image'] = request.build_absolute_uri(instance.image.url)
            if instance.plotted_image:
                representation['plotted_image'] = request.build_absolute_uri(instance.plotted_image.url)
        return representation

