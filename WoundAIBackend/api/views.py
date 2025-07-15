# import json
# import base64
# import requests
# import random
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.db import IntegrityError
# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.views import APIView
# from .models import Patient, WoundImage, WoundAnalysis, User, OTP
# from .serializers import (
#     PatientSerializer, WoundImageSerializer, WoundAnalysisSerializer, 
#     UserSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
# )
# from .utils import send_otp_email # Import the email utility

# class UserRegistrationView(generics.CreateAPIView):
#     """
#     API endpoint for user registration (Sign-up).
#     Creates a new user and automatically a Token for them.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny] # No authentication needed for registration

#     def perform_create(self, serializer):
#         user = serializer.save()
#         # Automatically create a Patient profile for new 'patient' role users
#         if user.role == 'patient':
#             Patient.objects.create(user=user)

# class CustomAuthToken(ObtainAuthToken):
#     """
#     Custom endpoint for user login (Sign-in).
#     Returns user data and authentication token.
#     """
#     serializer_class = LoginSerializer # Use custom LoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username,
#             'email': user.email,
#             'role': user.role,
#         }, status=status.HTTP_200_OK)

# class ForgotPasswordView(APIView):
#     """
#     API endpoint to initiate password reset (send OTP to email).
#     """
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.user # User object retrieved from serializer validation

#         # Generate OTP
#         otp_code = ''.join(random.choices('0123456789', k=6))
#         # Invalidate any existing unverified OTPs for this user
#         OTP.objects.filter(user=user, is_verified=False).update(is_verified=True)
#         otp_instance = OTP.objects.create(user=user, code=otp_code)

#         # Send OTP via email
#         if send_otp_email(user.email, otp_code):
#             return Response({"detail": "OTP sent to your email."}, status=status.HTTP_200_OK)
#         else:
#             return Response({"detail": "Failed to send OTP email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class ResetPasswordView(APIView):
#     """
#     API endpoint to reset password using OTP.
#     """
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = ResetPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user = serializer.validated_data['user']
#         otp_instance = serializer.validated_data['otp_instance']
#         new_password = serializer.validated_data['new_password']

#         user.set_password(new_password)
#         user.save()
        
#         # Mark OTP as verified after successful password reset
#         otp_instance.is_verified = True
#         otp_instance.save()

#         return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)

# class PatientViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for Patient operations.
#     - Authenticated users can view/edit their own patient profile.
#     - Doctors/Admins can view all patient profiles.
#     - Creation: Patients create their own profile upon registration (handled by signal/registration view). Doctors/Admins can create for specific users.
#     """
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.role == 'doctor':
#             return Patient.objects.all()
#         return Patient.objects.filter(user=user)

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         user = self.request.user
#         # Allow owner, doctor, or admin to view
#         if user == instance.user or user.role in ['doctor', 'admin'] or user.is_staff:
#             serializer = self.get_serializer(instance)
#             return Response(serializer.data)
#         return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         user = self.request.user
#         # Only owner or admin can update
#         if user == instance.user or user.is_staff or user.role == 'doctor': # Allowing doctor to update patient profile
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             return Response(serializer.data)
#         return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

#     def create(self, request, *args, **kwargs):
#         # Patients get a profile automatically on registration via UserRegistrationView.
#         # This endpoint is primarily for doctors/admins to create profiles for other users.
#         user = request.user
#         if user.role == 'patient':
#             # If a patient tries to create a profile directly here, check if one already exists
#             if hasattr(user, 'patient_profile') and user.patient_profile:
#                 return Response({"detail": "You already have a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
#             # If not, allow them to create their own profile, linking it to themselves
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save(user=user) # Link to the current authenticated user
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         elif user.role in ['doctor', 'admin'] or user.is_staff:
#             # Doctors/Admins must specify which user to create the patient profile for
#             user_id = request.data.get('user') # Expecting 'user' ID in request data
#             if not user_id:
#                 return Response({"detail": "For doctors/admins, 'user' ID is required to create a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 target_user = User.objects.get(id=user_id)
#                 # Check if target user already has a patient profile
#                 if hasattr(target_user, 'patient_profile') and target_user.patient_profile:
#                     return Response({"detail": f"User {target_user.username} already has a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
                
#                 serializer = self.get_serializer(data=request.data)
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save(user=target_user) # Link to the specified user
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except User.DoesNotExist:
#                 return Response({"detail": "Specified user not found."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)


# import json
# import base64
# import requests
# import random
# import uuid
# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.db import IntegrityError
# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.views import APIView
# from .models import Patient, WoundImage, WoundAnalysis, User, OTP
# from .serializers import (
#     PatientSerializer, WoundImageSerializer, WoundAnalysisSerializer, 
#     UserSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
# )
# from .utils import send_otp_email

# class WoundImageViewSet(viewsets.ModelViewSet):
#     queryset = WoundImage.objects.all()
#     serializer_class = WoundImageSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.role == 'doctor':
#             return WoundImage.objects.all()
#         return WoundImage.objects.filter(patient__user=user)

#     def create(self, request, *args, **kwargs):
#         patient_id = request.data.get('patient')
#         image_data = request.data.get('image')
#         notes = request.data.get('notes', '')

#         if not patient_id or not image_data:
#             return Response({"error": "Patient ID and image data are required."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             patient = Patient.objects.get(id=patient_id)
#             if not (request.user == patient.user or request.user.role in ['doctor', 'admin'] or request.user.is_staff):
#                 return Response({"detail": "You do not have permission to upload images for this patient."}, status=status.HTTP_403_FORBIDDEN)
#         except Patient.DoesNotExist:
#             return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

#         try:
#             if ";" not in image_data or "," not in image_data:
#                 raise ValueError("Image data is not in expected base64 format (e.g., data:image/jpeg;base64,...)")
#             format, imgstr = image_data.split(';base64,')
#             ext = format.split('/')[-1]
#             image_file_name = f'{patient.user.username}_wound_{uuid.uuid4()}.{ext}'
#             image_file = ContentFile(base64.b64decode(imgstr), name=image_file_name)
#         except Exception as e:
#             print(f"Error decoding image data: {e}")
#             return Response({"error": f"Invalid image format or decode error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             wound_image = WoundImage.objects.create(patient=patient, image=image_file, notes=notes)
#         except IntegrityError as e:
#              return Response({"error": f"Database error creating wound image: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#         gemini_api_key = settings.GEMINI_API_KEY
#         gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

#         prompt = """Analyze the provided image for a human wound.
# If a wound is clearly depicted, provide a detailed, structured JSON report.
# Crucially, include the wound's exact outline as an array of normalized coordinates (0.0 to 1.0) in the 'wound_outline_coordinates' field.
# The 'wound_outline_coordinates' array MUST contain at least 10-15 distinct [x, y] pairs, accurately tracing the wound's perimeter. These points should be ordered consecutively to form a polygon.
# If it is NOT a wound, set "is_wound" to false and provide a brief "rejection_reason" (max 10 words) and omit wound-specific details and the wound_outline_coordinates.

# JSON Report Structure:
# {
#   "is_wound": boolean,
#   "rejection_reason": string (optional, max 10 words),
#   "wound_area_cm2": number (optional, in cm²),
#   "estimated_depth_mm": number (optional, in mm),
#   "estimated_distance_cm": number (optional, in cm),
#   "healing_stage": string (optional, concise, max 20 words),
#   "tissue_type": string (optional, concise, comma-separated, max 20 words),
#   "exudate": string (optional, type and amount, concise, max 20 words),
#   "odor": string (optional, presence/absence, concise, max 10 words),
#   "periwound_skin": string (optional, concise description, max 20 words),
#   "potential_complications": string[] (optional, array of concise strings, max 20 words each),
#   "recommendations": string[] (optional, array of concise strings, max 20 words each),
#   "analysis_summary": string (optional, concise professional summary, max 3 sentences),
#   "wound_outline_coordinates": [[number, number], ...] // Array of [x, y] pairs, normalized 0.0 to 1.0, at least 10-15 points.
# }

# Provide realistic but varied values. Ensure that if "is_wound" is true, "wound_outline_coordinates" is always populated with a valid, dense array of coordinates. Do NOT include any conversational text or disclaimers outside the JSON."""

#         headers = { 'Content-Type': 'application/json' }
#         payload = {
#             "contents": [
#                 {"role": "user", "parts": [{"text": prompt}]},
#                 {"role": "user", "parts": [{"inlineData": {"mimeType": format.replace('data:', ''), "data": imgstr}}]}
#             ],
#             "generationConfig": {
#                 "responseMimeType": "application/json",
#                 "responseSchema": {
#                     "type": "OBJECT",
#                     "properties": {
#                         "is_wound": {"type": "BOOLEAN"},
#                         "rejection_reason": {"type": "STRING", "nullable": True},
#                         "wound_area_cm2": {"type": "NUMBER", "nullable": True},
#                         "estimated_depth_mm": {"type": "NUMBER", "nullable": True},
#                         "estimated_distance_cm": {"type": "NUMBER", "nullable": True},
#                         "healing_stage": {"type": "STRING", "nullable": True},
#                         "tissue_type": {"type": "STRING", "nullable": True},
#                         "exudate": {"type": "STRING", "nullable": True},
#                         "odor": {"type": "STRING", "nullable": True},
#                         "periwound_skin": {"type": "STRING", "nullable": True},
#                         "potential_complications": {
#                             "type": "ARRAY",
#                             "items": {"type": "STRING"},
#                             "nullable": True
#                         },
#                         "recommendations": {
#                             "type": "ARRAY",
#                             "items": {"type": "STRING"},
#                             "nullable": True
#                         },
#                         "analysis_summary": {"type": "STRING", "nullable": True},
#                         "wound_outline_coordinates": {
#                             "type": "ARRAY",
#                             "items": {
#                                 "type": "ARRAY",
#                                 "items": {"type": "NUMBER"},
#                                 "minItems": 2,
#                                 "maxItems": 2
#                             },
#                             "minItems": 10,
#                             "nullable": True
#                         }
#                     }
#                 }
#             }
#         }
        
#         try:
#             gemini_response = requests.post(f"{gemini_api_url}?key={gemini_api_key}",
#                                              headers=headers,
#                                              data=json.dumps(payload))
#             gemini_response.raise_for_status()
#             gemini_result = gemini_response.json()

#             ai_data = {}
#             if gemini_result and 'candidates' in gemini_result and gemini_result['candidates']:
#                 ai_content_parts = gemini_result['candidates'][0]['content']['parts']
#                 if ai_content_parts and ai_content_parts[0] and 'text' in ai_content_parts[0]:
#                     ai_data_str = ai_content_parts[0]['text']
#                     try:
#                         ai_data = json.loads(ai_data_str)
#                     except json.JSONDecodeError as e:
#                         print(f"Failed to decode AI JSON: {e}")
#                         print(f"Raw AI response text: {ai_data_str}")
#                         ai_data = {"is_wound": False, "rejection_reason": "AI response parsing error."}
#                 else:
#                     ai_data = {"is_wound": False, "rejection_reason": "AI content not found."}
#             else:
#                 ai_data = {"is_wound": False, "rejection_reason": "AI candidates not found."}

#             wound_analysis_data = {
#                 "wound_image": wound_image,
#                 "is_wound": ai_data.get("is_wound", False),
#                 "rejection_reason": ai_data.get("rejection_reason"),
#                 "wound_area_cm2": ai_data.get("wound_area_cm2"),
#                 "estimated_depth_mm": ai_data.get("estimated_depth_mm"),
#                 "estimated_distance_cm": ai_data.get("estimated_distance_cm"),
#                 "healing_stage": ai_data.get("healing_stage"),
#                 "tissue_type": ai_data.get("tissue_type"),
#                 "exudate": ai_data.get("exudate"),
#                 "odor": ai_data.get("odor"),
#                 "periwound_skin": ai_data.get("periwound_skin"),
#                 "potential_complications": ai_data.get("potential_complications", []),
#                 "recommendations": ai_data.get("recommendations", []),
#                 "analysis_summary": ai_data.get("analysis_summary"),
#                 "wound_outline_coordinates": ai_data.get("wound_outline_coordinates", [])
#             }
#             wound_analysis = WoundAnalysis.objects.create(**wound_analysis_data)

#             serializer = WoundImageSerializer(wound_image, context={'request': request})
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except requests.exceptions.RequestException as e:
#             print(f"Gemini API request failed: {e}")
#             wound_analysis = WoundAnalysis.objects.create(
#                 wound_image=wound_image,
#                 is_wound=False,
#                 rejection_reason=f"AI API request error: {e}"
#             )
#             serializer = WoundImageSerializer(wound_image, context={'request': request})
#             return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         except Exception as e:
#             print(f"Error during AI analysis or data saving: {e}")
#             wound_analysis = WoundAnalysis.objects.create(
#                 wound_image=wound_image,
#                 is_wound=False,
#                 rejection_reason=f"Internal server error during analysis: {e}"
#             )
#             serializer = WoundImageSerializer(wound_image, context={'request': request})
#             return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         user = self.request.user
#         if user == instance.patient.user or user.role in ['doctor', 'admin'] or user.is_staff:
#             serializer = self.get_serializer(instance)
#             return Response(serializer.data)
#         return Response({"detail": "You do not have permission to view this wound image."}, status=status.HTTP_403_FORBIDDEN)

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         user = self.request.user
#         if user == instance.patient.user or user.role in ['doctor', 'admin'] or user.is_staff:
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             return Response(serializer.data)
#         return Response({"detail": "You do not have permission to update this wound image."}, status=status.HTTP_403_FORBIDDEN)

#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         user = self.request.user
#         if user == instance.patient.user or user.is_staff or user.role == 'doctor':
#             self.perform_destroy(instance)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response({"detail": "You do not have permission to delete this wound image."}, status=status.HTTP_403_FORBIDDEN)


# class WoundAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = WoundAnalysis.objects.all()
#     serializer_class = WoundAnalysisSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.role == 'doctor':
#             return WoundAnalysis.objects.all()
#         return WoundAnalysis.objects.none()

# import matplotlib
# matplotlib.use('Agg')

# import json
# import base64
# import requests
# import random
# import uuid
# import io

# from django.conf import settings
# from django.core.files.base import ContentFile
# from django.db import IntegrityError
# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.views import APIView

# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# import numpy as np

# from PIL import Image

# from .models import Patient, WoundImage, WoundAnalysis, User, OTP
# from .serializers import (
#     PatientSerializer, WoundImageSerializer, WoundAnalysisSerializer, 
#     UserSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
# )
# from .utils import send_otp_email

# # Function to simulate an external wound segmentation/detection API
# def _simulate_external_segmentation_api(image_base64_data):
#     """
#     Simulates a call to an external ML service (e.g., running YOLO, U-Net, R-CNN).
#     For demonstration, this function generates a consistent, plausible wound outline
#     and estimated depth, and other wound details.
#     """
#     # In a real application, you would send image_base64_data to your ML server
#     # and parse its response.
    
#     # Simulate a successful wound detection
#     is_wound = True
    
#     # Generate a realistic but random wound area (e.g., 0.5 to 10.0 cm^2)
#     wound_area_cm2 = round(random.uniform(0.5, 10.0), 2)
    
#     # Generate a realistic but random estimated depth (e.g., 1.0 to 8.0 mm)
#     estimated_depth_mm = round(random.uniform(1.0, 8.0), 1)

#     # Generate a more consistent and varied wound outline for better visualization
#     # This simulates a more accurate segmentation model
#     num_points = random.randint(15, 30) # More points for smoother outline
#     center_x, center_y = random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)
#     radius_x, radius_y = random.uniform(0.05, 0.2), random.uniform(0.05, 0.15)
    
#     wound_outline_coordinates = []
#     for i in range(num_points):
#         angle = 2 * np.pi * i / num_points
#         x = center_x + radius_x * np.cos(angle) * random.uniform(0.8, 1.2) # Add some irregularity
#         y = center_y + radius_y * np.sin(angle) * random.uniform(0.8, 1.2)
#         wound_outline_coordinates.append([round(x, 2), round(y, 2)])

#     # Simulate other detailed analysis fields
#     healing_stages = ["Inflammatory", "Proliferative", "Maturation", "Stalled"]
#     tissue_types = ["Granulation", "Slough", "Necrotic", "Epithelialization"]
#     exudates = ["Minimal, serous", "Moderate, serosanguinous", "Heavy, purulent"]
#     odors = ["None detected", "Foul", "Slightly malodorous"]
#     periwound_skins = ["Intact", "Erythematous", "Macerated", "Dry and flaky"]
#     complications = ["Infection", "Delayed healing", "Edema", "Undermining"]
#     recommendations = ["Cleanse with saline", "Apply hydrocolloid", "Debridement", "Elevate limb"]

#     analysis_summary = (
#         f"A {random.choice(['small', 'medium', 'large'])} wound is observed. "
#         f"It appears to be in the {random.choice(healing_stages).lower()} stage. "
#         f"The primary tissue type is {random.choice(tissue_types).lower()}. "
#         f"Expected healing time is approximately {random.randint(7, 45)} days."
#     )
    
#     # Ensure some complications/recommendations are provided randomly
#     potential_complications = random.sample(complications, k=random.randint(0, min(2, len(complications))))
#     recommendations = random.sample(recommendations, k=random.randint(0, min(2, len(recommendations))))

#     return {
#         "is_wound": is_wound,
#         "rejection_reason": None,
#         "wound_area_cm2": wound_area_cm2,
#         "estimated_depth_mm": estimated_depth_mm,
#         "estimated_distance_cm": round(random.uniform(5.0, 20.0), 1), # Always provide a value
#         "healing_stage": random.choice(healing_stages),
#         "tissue_type": random.choice(tissue_types),
#         "exudate": random.choice(exudates),
#         "odor": random.choice(odors),
#         "periwound_skin": random.choice(periwound_skins),
#         "potential_complications": potential_complications,
#         "recommendations": recommendations,
#         "analysis_summary": analysis_summary,
#         "wound_outline_coordinates": wound_outline_coordinates
#     }

# # Function to encapsulate Matplotlib plotting logic
# def plot_3d_wound_on_image(img, wound_outline_coordinates, estimated_depth_mm):
#     try:
#         # Ensure coordinates are a numpy array and float type for plotting
#         outline_pixels = np.array(wound_outline_coordinates, dtype=float)
#         if outline_pixels.shape[0] < 3: # Need at least 3 points for a polygon
#             print("Warning: Insufficient points for wound outline, skipping 3D plot.")
#             return None

#         # Convert normalized coordinates to image pixel coordinates
#         outline_pixels_scaled = np.array([(x * img.width, y * img.height) for x, y in outline_pixels])
        
#         # Create a figure and a 3D subplot
#         fig = plt.figure(figsize=(img.width / 100, img.height / 100), dpi=100)
#         ax = fig.add_subplot(111, projection='3d')

#         # Display the 2D image in the background of the 3D plot
#         ax.imshow(img, extent=[0, img.width, 0, img.height], origin='upper')

#         depth_scale_factor = img.width / 500 # Adjust this factor for visual prominence
#         depth_scaled = estimated_depth_mm * depth_scale_factor
        
#         if depth_scaled <= 0 or np.isnan(depth_scaled):
#             depth_scaled = 1.0

#         # Create the top surface of the wound (the original outline) at Z=0
#         top_surface_vertices = np.c_[outline_pixels_scaled, np.zeros(len(outline_pixels_scaled))]
#         top_polygon = Poly3DCollection([top_surface_vertices])
#         top_polygon.set_facecolor((0, 1, 0, 0.4)) # Green with 40% opacity
#         top_polygon.set_edgecolor('red')
#         top_polygon.set_linewidth(2)
#         ax.add_collection3d(top_polygon)

#         # Create the bottom surface (extruded depth) at Z = -depth_scaled
#         bottom_surface_vertices = np.c_[outline_pixels_scaled, -depth_scaled * np.ones(len(outline_pixels_scaled))]
#         bottom_polygon = Poly3DCollection([bottom_surface_vertices])
#         bottom_polygon.set_facecolor((0, 1, 0, 0.1)) # Lighter green with 10% opacity
#         bottom_polygon.set_edgecolor('red')
#         bottom_polygon.set_linewidth(0.5)
#         ax.add_collection3d(bottom_polygon)

#         # Create side walls by connecting corresponding points on top and bottom outlines
#         sides = []
#         for i in range(len(outline_pixels_scaled)):
#             p1_top = top_surface_vertices[i]
#             p2_top = top_surface_vertices[(i + 1) % len(outline_pixels_scaled)]
#             p1_bottom = bottom_surface_vertices[i]
#             p2_bottom = bottom_surface_vertices[(i + 1) % len(outline_pixels_scaled)]
#             sides.append([p1_top, p2_top, p2_bottom, p1_bottom])
        
#         side_polygons = Poly3DCollection(sides)
#         side_polygons.set_facecolor((0, 0, 1, 0.2)) # Blue with 20% opacity
#         side_polygons.set_edgecolor('blue')
#         side_polygons.set_linewidth(0.5)
#         ax.add_collection3d(side_polygons)

#         # Set 3D axis limits for better viewing of wound within image context
#         ax.set_xlim(0, img.width)
#         ax.set_ylim(0, img.height)
#         ax.set_zlim(-depth_scaled * 1.2, depth_scaled * 0.2) 
        
#         # Adjust view angle for a good 3D perspective
#         ax.view_init(elev=25, azim=-55) 

#         # Hide axes labels and ticks for a cleaner image
#         ax.set_axis_off()
#         ax.set_xlabel('')
#         ax.set_ylabel('')
#         ax.set_zlabel('')
#         ax.grid(False)

#         # Remove padding around the image in the subplot
#         plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

#         # Save the plot to an in-memory binary stream
#         buffer = io.BytesIO()
#         plt.savefig(buffer, format='jpeg', bbox_inches='tight', pad_inches=0, dpi=150)
#         buffer.seek(0)
        
#         plt.close(fig) # IMPORTANT: Close the figure to free up memory
#         return buffer

#     except Exception as plot_e:
#         print(f"Error in plot_3d_wound_on_image: {plot_e}")
#         return None


# class UserRegistrationView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]

#     def perform_create(self, serializer):
#         user = serializer.save()
#         if user.role == 'patient':
#             Patient.objects.create(user=user)

# class CustomAuthToken(ObtainAuthToken):
#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.pk,
#             'username': user.username,
#             'email': user.email,
#             'role': user.role,
#         }, status=status.HTTP_200_OK)

# class ForgotPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.user

#         otp_code = ''.join(random.choices('0123456789', k=6))
#         OTP.objects.filter(user=user, is_verified=False).update(is_verified=True)
#         otp_instance = OTP.objects.create(user=user, code=otp_code)

#         if send_otp_email(user.email, otp_code):
#             return Response({"detail": "OTP sent to your email."}, status=status.HTTP_200_OK)
#         else:
#             return Response({"detail": "Failed to send OTP email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class ResetPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = ResetPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         user = serializer.validated_data['user']
#         otp_instance = serializer.validated_data['otp_instance']
#         new_password = serializer.validated_data['new_password']

#         user.set_password(new_password)
#         user.save()
        
#         otp_instance.is_verified = True
#         otp_instance.save()

#         return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)

# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.role == 'doctor':
#             return Patient.objects.all()
#         # Ensure patients can only see their own profiles
#         return Patient.objects.filter(user=user) 

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         user = self.request.user
#         # Allow doctors/admins to view any patient, patients to view their own
#         if user == instance.user or user.role in ['doctor', 'admin'] or user.is_staff:
#             serializer = self.get_serializer(instance)
#             return Response(serializer.data)
#         return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         instance = self.get_object()
#         user = self.request.user
#         # Allow doctors/admins to update any patient, patients to update their own
#         if user == instance.user or user.is_staff or user.role == 'doctor':
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             self.perform_update(serializer)
#             return Response(serializer.data)
#         return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

#     def create(self, request, *args, **kwargs):
#         user = request.user
#         # Logic for creating a patient profile based on user role
#         if user.role == 'patient':
#             if hasattr(user, 'patient_profile') and user.patient_profile:
#                 return Response({"detail": "You already have a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save(user=user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
        
#         elif user.role in ['doctor', 'admin'] or user.is_staff:
#             user_id = request.data.get('user')
#             if not user_id:
#                 return Response({"detail": "For doctors/admins, 'user' ID is required to create a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
#             try:
#                 target_user = User.objects.get(id=user_id)
#                 if hasattr(target_user, 'patient_profile') and target_user.patient_profile:
#                     return Response({"detail": f"User {target_user.username} already has a patient profile."}, status=status.HTTP_400_BAD_REQUEST)
                
#                 serializer = self.get_serializer(data=request.data)
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save(user=target_user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except User.DoesNotExist:
#                 return Response({"detail": "Specified user not found."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

# class WoundImageViewSet(viewsets.ModelViewSet):
#     queryset = WoundImage.objects.all()
#     serializer_class = WoundImageSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.role == 'doctor':
#             return WoundImage.objects.all()
#         # Patients can only see their own wound images
#         return WoundImage.objects.filter(patient__user=user)

#     def create(self, request, *args, **kwargs):
#         # All logic for creating and processing wound images is now wrapped in this try-except block
#         try:
#             patient_id = request.data.get('patient')
#             image_data = request.data.get('image')
#             notes = request.data.get('notes', '')

#             if not patient_id or not image_data:
#                 return Response({"error": "Patient ID and image data are required."}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 patient = Patient.objects.get(id=patient_id)
#                 if not (request.user == patient.user or request.user.role in ['doctor', 'admin'] or request.user.is_staff):
#                     return Response({"detail": "You do not have permission to upload images for this patient."}, status=status.HTTP_403_FORBIDDEN)
#             except Patient.DoesNotExist:
#                 return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

#             try:
#                 if ";" not in image_data or "," not in image_data:
#                     raise ValueError("Image data is not in expected base64 format (e.g., data:image/jpeg;base64,...)")
#                 format, imgstr = image_data.split(';base64,')
#                 ext = format.split('/')[-1]
#                 image_file_name = f'{patient.user.username}_wound_{uuid.uuid4()}.{ext}'
#                 image_file = ContentFile(base64.b64decode(imgstr), name=image_file_name)
#             except Exception as e:
#                 print(f"Error decoding image data: {e}")
#                 return Response({"error": f"Invalid image format or decode error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            
#             try:
#                 wound_image = WoundImage.objects.create(patient=patient, image=image_file, notes=notes)
#             except IntegrityError as e:
#                 return Response({"error": f"Database error creating wound image: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#             # --- Simulated External ML Service Call ---
#             # This function provides all the structured data, including accurate outline and depth.
#             simulated_ml_response = _simulate_external_segmentation_api(image_data)
            
#             ai_data = simulated_ml_response 

#             # Print the ai_data dictionary after fallbacks for debugging
#             print("AI Data (from simulated ML) used for analysis:", ai_data)

#             wound_analysis_data = {
#                 "wound_image": wound_image,
#                 "is_wound": ai_data.get("is_wound", False),
#                 "rejection_reason": ai_data.get("rejection_reason"),
#                 "wound_area_cm2": ai_data.get("wound_area_cm2"),
#                 "estimated_depth_mm": ai_data.get("estimated_depth_mm"),
#                 "estimated_distance_cm": ai_data.get("estimated_distance_cm"),
#                 "healing_stage": ai_data.get("healing_stage"),
#                 "tissue_type": ai_data.get("tissue_type"),
#                 "exudate": ai_data.get("exudate"),
#                 "odor": ai_data.get("odor"),
#                 "periwound_skin": ai_data.get("periwound_skin"),
#                 "potential_complications": ai_data.get("potential_complications", []),
#                 "recommendations": ai_data.get("recommendations", []),
#                 "analysis_summary": ai_data.get("analysis_summary"),
#                 "wound_outline_coordinates": ai_data.get("wound_outline_coordinates", [])
#             }
#             wound_analysis = WoundAnalysis.objects.create(**wound_analysis_data)

#             # --- Matplotlib Plotting for 3D Visual ---
#             if wound_analysis.is_wound and wound_analysis.wound_outline_coordinates and wound_analysis.estimated_depth_mm is not None:
#                 try:
#                     original_image_path = wound_image.image.path
#                     img = Image.open(original_image_path)
                    
#                     buffer = plot_3d_wound_on_image(img, wound_analysis.wound_outline_coordinates, wound_analysis.estimated_depth_mm)
                    
#                     if buffer:
#                         plotted_image_file_name = f'plotted_3d_{uuid.uuid4()}.jpeg'
#                         wound_image.plotted_image.save(plotted_image_file_name, ContentFile(buffer.read()), save=True)
#                     else:
#                         wound_image.plotted_image = None
#                         wound_image.save()

#                 except Exception as plot_e:
#                     print(f"Error during Matplotlib 3D plotting: {plot_e}")
#                     wound_image.plotted_image = None
#                     wound_image.save()
#             else:
#                 wound_image.plotted_image = None
#                 wound_image.save()
            
#             serializer = WoundImageSerializer(wound_image, context={'request': request})
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             # This catch-all exception handles any unhandled errors in the entire process.
#             print(f"General error during wound image processing in create method: {e}")
#             # Ensure a minimal analysis object is still created on error
#             # If wound_image was not created, this needs to be handled to prevent a crash
#             if 'wound_image' in locals():
#                 wound_analysis = WoundAnalysis.objects.create(
#                     wound_image=wound_image,
#                     is_wound=False,
#                     rejection_reason=f"Processing error: {e}"
#                 )
#                 serializer = WoundImageSerializer(wound_image, context={'request': request})
#                 return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             else:
#                 # If wound_image itself failed to be created, return a simple error
#                 return Response({"error": f"Failed to initiate wound image processing due to: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class WoundAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = WoundAnalysis.objects.all()
#     serializer_class = WoundAnalysisSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff or user.role == 'doctor':
#             return WoundAnalysis.objects.all()
#         # Restrict analysis view to only superusers/doctors/admins
#         return WoundAnalysis.objects.none()








import base64
import uuid
import io
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cv2 # For contour finding

from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.db.models import Q # For complex queries

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings

from .models import WoundImage, WoundAnalysis, Patient, User
from .serializers import WoundImageSerializer, WoundAnalysisSerializer, UserRegistrationSerializer, UserSerializer, PatientSerializer
from .permissions import IsOwnerOrAdminOrDoctor, IsAdminOrDoctor, IsAdmin

# --- ML Model Imports and Initialization ---
import torch
from transformers import BeitImageProcessor, BeitForImageClassification, ViTImageProcessor, ViTForImageClassification, ResNetForImageClassification
from monai.networks.nets import UNet
from monai.transforms import Compose, ScaleIntensityRanged, ToTensord, Resized # Corrected import
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb
import shap
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

# Global variables for models and processors
_classifier_model = None
_classifier_processor = None
_segmenter_model = None
_healing_predictor_model = None
_wound_type_encoder = None
_device = None
_ml_models_initialized = False # Flag to ensure one-time initialization

# Configuration and Constants (re-defined for clarity in this context)
IMAGE_SIZE = (224, 224)
WOUND_TYPES = ["Abrasions", "Bruises", "Bums", "Cut", "Ingrown_nails", "Laceration", "Stab_wound"]
TISSUE_TYPES = {
    0: "Background",
    1: "Slough",
    2: "Necrosis",
    3: "Granulation",
    4: "Epithelial Edge"
}
NUM_TISSUE_CLASSES = len(TISSUE_TYPES)

# Dummy function for synthetic data generation for the healing predictor's internal scaler/encoder
def generate_synthetic_structured_data(num_samples, wound_types):
    data = {
        'WoundArea': np.random.uniform(5, 100, num_samples), # cm²
        'WoundDepth': np.random.choice(['Superficial', 'Partial Thickness', 'Full Thickness'], num_samples),
        'SloughPercentage': np.random.uniform(0, 100, num_samples),
        'GranulationPercentage': np.random.uniform(0, 100, num_samples),
        'Comorbidities': np.random.randint(0, 2, num_samples), # 0 or 1
        'InfectionStatus': np.random.randint(0, 2, num_samples), # 0 or 1
        'ABIDoppler': np.random.uniform(0.5, 1.2, num_samples),
        'DressingFrequency': np.random.randint(1, 7, num_samples),
        'PriorHealingResponse': np.random.randint(0, 2, num_samples), # 0=Poor, 1=Good
        'WoundType': np.random.choice(wound_types, num_samples), # Synthetic wound types for demo
        'WeeksToHeal': np.random.randint(4, 13, num_samples) # Target variable: 4-12 weeks
    }
    df = pd.DataFrame(data)

    df['SloughPercentage'] = df.apply(lambda row: min(row['SloughPercentage'], 100), axis=1)
    df['GranulationPercentage'] = df.apply(lambda row: min(row['GranulationPercentage'], 100 - row['SloughPercentage']), axis=1)
    return df

# Re-define the XGBoostHealingPredictor class here for self-containment
class XGBoostHealingPredictor:
    def __init__(self):
        self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def preprocess_features(self, df, fit_scaler=True):
        processed_df = df.copy()
        categorical_cols = ['WoundDepth', 'WoundType']
        for col in categorical_cols:
            if col in processed_df.columns:
                if fit_scaler:
                    le = LabelEncoder()
                    processed_df[col] = le.fit_transform(processed_df[col])
                    self.label_encoders[col] = le
                else:
                    if col in self.label_encoders:
                        mapping = {cls: idx for idx, cls in enumerate(self.label_encoders[col].classes_)}
                        # Handle unseen categories by mapping to -1 or a default, then one-hot encoding
                        processed_df[col] = processed_df[col].map(mapping).fillna(-1).astype(int)
                    else:
                        # If encoder not fitted, treat as new categorical data for one-hot encoding
                        processed_df = pd.get_dummies(processed_df, columns=[col], prefix=col)


        numerical_cols = ['WoundArea', 'SloughPercentage', 'GranulationPercentage', 'ABIDoppler', 'DressingFrequency', 'Comorbidities', 'InfectionStatus', 'PriorHealingResponse']
        numerical_cols = [col for col in numerical_cols if col in processed_df.columns]

        if numerical_cols:
            if fit_scaler:
                processed_df[numerical_cols] = self.scaler.fit_transform(processed_df[numerical_cols])
            else:
                processed_df[numerical_cols] = self.scaler.transform(processed_df[numerical_cols])
        return processed_df

    def train(self, X_df, y_series):
        X_processed = self.preprocess_features(X_df, fit_scaler=True)
        self.model.fit(X_processed, y_series)

    def predict(self, X_df):
        X_processed = self.preprocess_features(X_df, fit_scaler=False)
        # Align columns with training data, adding missing columns with 0
        train_cols = self.model.feature_names_in_
        missing_cols = set(train_cols) - set(X_processed.columns)
        for c in missing_cols:
            X_processed[c] = 0
        # Ensure the order of columns is the same as during training
        X_processed = X_processed[train_cols]
        return self.model.predict(X_processed)

# MONAI Transforms for Segmentation (for inference)
_monai_inference_transforms = Compose(
    [
        ScaleIntensityRanged(keys=["image"], a_min=0, a_max=255, b_min=0.0, b_max=1.0, clip=True),
        Resized(keys=["image", "mask"], spatial_size=IMAGE_SIZE, mode=["bilinear", "nearest"]),
        ToTensord(keys=["image", "mask"]),
    ]
)

# --- Classifier Model Definitions (Updated target_layers) ---
class BeitClassifier(nn.Module):
    def __init__(self, num_classes, model_name="microsoft/beit-base-patch16-224"):
        super().__init__()
        print(f"Initializing BEiT classifier: {model_name}...")
        self.model = BeitForImageClassification.from_pretrained(
            model_name,
            num_labels=num_classes,
            ignore_mismatched_sizes=True
        )
        # Target the last encoder layer for Grad-CAM
        self.target_layers = [self.model.beit.encoder.layer[-1]]

    def forward(self, pixel_values):
        outputs = self.model(pixel_values=pixel_values)
        return outputs.logits

class VitClassifier(nn.Module):
    def __init__(self, num_classes, model_name="google/vit-base-patch16-224"):
        super().__init__()
        print(f"Initializing ViT classifier: {model_name}...")
        self.model = ViTForImageClassification.from_pretrained(
            model_name,
            num_labels=num_classes,
            ignore_mismatched_sizes=True
        )
        # Target the last encoder layer for Grad-CAM
        self.target_layers = [self.model.vit.encoder.layer[-1]]

    def forward(self, pixel_values):
        outputs = self.model(pixel_values=pixel_values)
        return outputs.logits

class ResNetClassifier(nn.Module):
    def __init__(self, num_classes, model_name="microsoft/resnet-50"):
        super().__init__()
        print(f"Initializing ResNet-50 classifier: {model_name}...")
        self.model = ResNetForImageClassification.from_pretrained(
            model_name,
            num_labels=num_classes,
            ignore_mismatched_sizes=True
        )
        # Target the last convolutional block for Grad-CAM
        self.target_layers = [self.model.resnet.encoder.stages[-1].layers[-1].conv3]

    def forward(self, pixel_values):
        outputs = self.model(pixel_values=pixel_values)
        return outputs.logits

# --- Reshape transform for Vision Transformers (BEiT, ViT) ---
def reshape_transform_beit_vit(tensor):
    """
    Transforms the output of a Vision Transformer encoder layer
    from (batch_size, num_tokens, hidden_dim) to (batch_size, height, width, hidden_dim).
    This is necessary for Grad-CAM as it expects a spatial grid.
    It also removes the CLS token.
    """
    # The BeitEncoderLayer/ViTEncoderLayer returns a tuple (hidden_states,)
    # We need to extract the hidden_states tensor which is the first element.
    if isinstance(tensor, tuple):
        tensor = tensor[0]

    # For Vision Transformers, the output is typically (batch_size, num_tokens, hidden_dim)
    # where num_tokens = 1 (CLS token) + num_patches.
    # We need to remove the CLS token and reshape the patches into a 2D grid.
    # For 224x224 input with a 16x16 patch size, the number of patches is (224/16)^2 = 14^2 = 196.
    # So, the tensor shape after removing CLS token will be (batch_size, 196, hidden_dim).
    # We want to reshape it to (batch_size, spatial_dim, spatial_dim, hidden_dim) where spatial_dim=14.

    # Remove the CLS token (first token)
    tensor = tensor[:, 1:, :]

    # Calculate height and width of the patch grid
    # This assumes a square grid of patches.
    num_patches = tensor.shape[1]
    spatial_dim = int(np.sqrt(num_patches)) # Should be 14 for 224x224 input, 16x16 patches

    # Reshape to (batch_size, spatial_dim, spatial_dim, hidden_dim)
    result = tensor.reshape(tensor.size(0), spatial_dim, spatial_dim, tensor.size(2))
    return result


def _initialize_ml_models():
    """Initializes and loads all ML models and processors globally."""
    global _classifier_model, _classifier_processor, _segmenter_model, _healing_predictor_model, _wound_type_encoder, _device, _ml_models_initialized

    if _ml_models_initialized:
        print("ML models already initialized.")
        return

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Initializing ML models on device: {_device}")

    # Initialize Classifier (using BEiT as default)
    _classifier_processor = BeitImageProcessor.from_pretrained("microsoft/beit-base-patch16-224")
    _classifier_model = BeitClassifier(num_classes=len(WOUND_TYPES)).to(_device)
    # Placeholder for actual trained weights loading if available
    # _classifier_model.load_state_dict(torch.load('path/to/classifier_weights.pth', map_location=_device))
    _classifier_model.eval()
    print("BEiT classifier initialized.")

    # Initialize Segmenter
    _segmenter_model = UNet(
        spatial_dims=2,
        in_channels=3, # Assuming RGB input
        out_channels=NUM_TISSUE_CLASSES,
        channels=(16, 32, 64, 128, 256),
        strides=(2, 2, 2, 2),
        num_res_units=2,
    ).to(_device)
    # Placeholder for actual trained weights loading if available
    # _segmenter_model.load_state_dict(torch.load('path/to/segmenter_weights.pth', map_location=_device))
    _segmenter_model.eval()
    print("MONAI U-Net segmenter initialized.")

    # Initialize Healing Predictor
    _healing_predictor_instance = XGBoostHealingPredictor() # Use the class to get preprocessors
    # For demonstration, we'll train a dummy model here if not loaded.
    dummy_structured_data = generate_synthetic_structured_data(200, WOUND_TYPES)
    dummy_X = dummy_structured_data.drop(columns=['WeeksToHeal', 'image_id'])
    dummy_y = dummy_structured_data['WeeksToHeal']
    _healing_predictor_instance.train(dummy_X, dummy_y) # This will fit its internal scaler and encoders
    _healing_predictor_model = _healing_predictor_instance # Assign the instance itself
    print("XGBoost healing predictor initialized.")

    _wound_type_encoder = LabelEncoder()
    _wound_type_encoder.fit(WOUND_TYPES) # Fit on all possible wound types

    _ml_models_initialized = True


def _run_ml_pipeline(image_np, structured_features_df):
    """
    Runs the end-to-end WoundAI prediction pipeline for a single sample.
    Returns analysis results and image buffers for visualizations.
    """
    # Ensure models are initialized
    _initialize_ml_models()

    # 1. Image-based Wound Type Classification
    inputs_cls = _classifier_processor(images=Image.fromarray(image_np), return_tensors="pt")
    image_tensor_cls = inputs_cls['pixel_values'].to(_device)

    _classifier_model.eval()
    with torch.no_grad():
        classifier_output = _classifier_model(image_tensor_cls)
        _, predicted_wound_type_idx = torch.max(classifier_output, 1)
    predicted_wound_type = _wound_type_encoder.inverse_transform(predicted_wound_type_idx.cpu().numpy())[0]

    # Grad-CAM for Classifier
    grad_cam_buffer = io.BytesIO()
    try:
        # Determine reshape_transform based on classifier type
        reshape_transform = None
        if isinstance(_classifier_model, (BeitClassifier, VitClassifier)):
            reshape_transform = reshape_transform_beit_vit

        cam_explainer = GradCAM(
            model=_classifier_model,
            target_layers=_classifier_model.target_layers,
            use_cuda=torch.cuda.is_available(),
            reshape_transform=reshape_transform # Pass the reshape transform
        )
        grayscale_cam = cam_explainer(input_tensor=image_tensor_cls, targets=[ClassifierOutputTarget(predicted_wound_type_idx.item())])
        grayscale_cam = grayscale_cam[0, :] # Get heatmap for the first image in batch

        original_image_float = image_np.astype(np.float32) / 255.0
        cam_image = show_cam_on_image(original_image_float, grayscale_cam, use_rgb=True, image_weight=0.4)

        plt.figure(figsize=(6, 6))
        plt.imshow(cam_image)
        plt.title(f"Grad-CAM: {predicted_wound_type}")
        plt.axis('off')
        plt.savefig(grad_cam_buffer, format='jpeg', bbox_inches='tight', pad_inches=0)
        plt.close()
        grad_cam_buffer.seek(0)
    except Exception as e:
        print(f"Error generating Grad-CAM: {e}. Grad-CAM might not be compatible with the chosen model/layer combination or require a different target layer.")
        grad_cam_buffer = None # Indicate failure

    # 2. Tissue Segmentation
    temp_data_dict = {"image": image_np, "mask": np.zeros(IMAGE_SIZE, dtype=np.int64)} # Mask is dummy here for transform
    transformed_input_seg_batch = _monai_inference_transforms(temp_data_dict)['image']
    image_tensor_seg = transformed_input_seg_batch.unsqueeze(0).to(_device)

    _segmenter_model.eval()
    with torch.no_grad():
        segmenter_output = _segmenter_model(image_tensor_seg)
        predicted_mask = torch.argmax(segmenter_output, dim=1).squeeze(0).cpu().numpy()

    # Calculate tissue percentages
    total_pixels = predicted_mask.size
    tissue_counts = {class_id: np.sum(predicted_mask == class_id) for class_id in TISSUE_TYPES.keys()}
    slough_percentage = (tissue_counts.get(1, 0) / total_pixels) * 100
    necrosis_percentage = (tissue_counts.get(2, 0) / total_pixels) * 100
    granulation_percentage = (tissue_counts.get(3, 0) / total_pixels) * 100
    epithelial_edge_percentage = (tissue_counts.get(4, 0) / total_pixels) * 100

    # Derive wound area (simple pixel count for now)
    wound_pixels = np.sum(predicted_mask > 0) # All non-background pixels
    pixels_per_cm2 = (IMAGE_SIZE[0] * IMAGE_SIZE[1]) / (10 * 10) # Example: 224*224 / 100 = 501.76
    wound_area_cm2 = wound_pixels / pixels_per_cm2 if pixels_per_cm2 > 0 else 0

    # Get wound outline coordinates (simple contour from mask)
    wound_outline_coordinates = []
    mask_uint8 = (predicted_mask > 0).astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        wound_outline_coordinates = largest_contour.squeeze().tolist()
        if len(wound_outline_coordinates) > 0 and not isinstance(wound_outline_coordinates[0], list):
            wound_outline_coordinates = [wound_outline_coordinates]

    # 3. Healing Trajectory Prediction
    current_features = structured_features_df.copy()
    current_features['SloughPercentage'] = slough_percentage
    current_features['GranulationPercentage'] = granulation_percentage
    current_features['WoundType'] = predicted_wound_type

    predicted_weeks_to_heal = _healing_predictor_model.predict(current_features)

    # SHAP for Healing Predictor
    shap_plot_buffer = io.BytesIO()
    try:
        processed_features_for_shap = _healing_predictor_model.preprocess_features(current_features, fit_scaler=False)
        processed_features_for_shap = processed_features_for_shap[_healing_predictor_model.model.feature_names_in_]

        explainer = shap.TreeExplainer(_healing_predictor_model.model)
        shap_values = explainer.shap_values(processed_features_for_shap)

        plt.figure(figsize=(8, 6))
        shap.summary_plot(shap_values, processed_features_for_shap, plot_type="bar", show=False)
        plt.title("SHAP Explanation for Healing Prediction")
        plt.tight_layout()
        plt.savefig(shap_plot_buffer, format='jpeg', bbox_inches='tight', pad_inches=0)
        plt.close()
        shap_plot_buffer.seek(0)
    except Exception as e:
        print(f"Error generating SHAP plot: {e}")
        shap_plot_buffer = None

    # For estimated_depth_mm, since the current ML pipeline doesn't predict it,
    # we'll use a placeholder or derive it from wound area for synthetic consistency.
    estimated_depth_mm = 0.5 + (wound_area_cm2 / 100.0) * 2.0 # Simple synthetic derivation

    return {
        "is_wound": True, # Assuming any image with a non-zero mask is a wound
        "rejection_reason": None,
        "wound_area_cm2": wound_area_cm2,
        "estimated_depth_mm": estimated_depth_mm,
        "estimated_distance_cm": 10.0, # Placeholder
        "healing_stage": "Early Granulation", # Placeholder
        "tissue_type": {
            "Slough": f"{slough_percentage:.2f}%",
            "Necrosis": f"{necrosis_percentage:.2f}%",
            "Granulation": f"{granulation_percentage:.2f}%",
            "Epithelial Edge": f"{epithelial_edge_percentage:.2f}%"
        },
        "exudate": "Moderate", # Placeholder
        "odor": "None", # Placeholder
        "periwound_skin": "Intact", # Placeholder
        "potential_complications": ["Infection Risk"], # Placeholder
        "recommendations": ["Cleanse wound daily", "Apply appropriate dressing"], # Placeholder
        "analysis_summary": f"Wound type: {predicted_wound_type}. Estimated healing: {predicted_weeks_to_heal[0]:.2f} weeks.",
        "wound_outline_coordinates": wound_outline_coordinates,
        "grad_cam_image_buffer": grad_cam_buffer,
        "shap_plot_image_buffer": shap_plot_buffer,
        "segmentation_visual_buffer": None # Not directly used for saving in this API
    }

def plot_3d_wound_on_image(original_image, wound_outline_coords, depth_mm):
    """
    Placeholder for 3D plotting. This would typically involve more complex 3D rendering
    using libraries like Mayavi, PyVista, or custom OpenGL/WebGL.
    For demonstration, we'll just overlay a basic shape with a "depth" effect.
    """
    try:
        img_np = np.array(original_image.convert("RGB"))
        height, width, _ = img_np.shape

        # Create a blank canvas for the overlay
        overlay = np.zeros_like(img_np, dtype=np.uint8)

        # Convert outline coordinates to a format suitable for OpenCV
        if not wound_outline_coords:
            return None # No outline to plot

        # Ensure coordinates are integers and in the correct shape (N, 1, 2)
        # Handle cases where wound_outline_coords might be a list of lists or flattened
        if isinstance(wound_outline_coords[0], (int, float)):
            # Assume it's a flattened list of [x1, y1, x2, y2, ...]
            points = np.array(wound_outline_coords).reshape(-1, 2).astype(np.int32)
        else:
            # Assume it's a list of [x, y] pairs or [x, y, z] if 3D, take only x, y
            points = np.array([[p[0], p[1]] for p in wound_outline_coords]).astype(np.int32)

        if points.ndim == 1: # Handle case where it's a single point [x, y]
            points = points.reshape(1, 2)

        # Reshape for cv2.polylines or cv2.fillPoly
        points = points.reshape((-1, 1, 2))

        # Create a mask from the outline
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, [points], 255)

        # Simple "depth" effect: draw concentric outlines
        num_layers = int(depth_mm * 2) # More layers for deeper wounds
        for i in range(num_layers):
            thickness = max(1, int(depth_mm / num_layers * 2))
            color_intensity = int(255 * (1 - i / num_layers))
            # Offset the contour slightly for a 3D feel
            offset_x = int(i * thickness * 0.2)
            offset_y = int(i * thickness * 0.2)

            # Create a slightly offset contour
            offset_points = points.copy()
            offset_points[:, 0, 0] += offset_x
            offset_points[:, 0, 1] += offset_y

            # Draw the offset contour
            cv2.polylines(overlay, [offset_points], isClosed=True, color=(color_intensity, color_intensity, color_intensity), thickness=thickness)

        # Blend the overlay with the original image
        alpha = 0.5 # Transparency of the overlay
        result_image = cv2.addWeighted(img_np, 1 - alpha, overlay, alpha, 0)

        # Save to buffer
        buffer = io.BytesIO()
        Image.fromarray(result_image).save(buffer, format='JPEG')
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"Error in plot_3d_wound_on_image: {e}")
        return None

# --- API Views ---

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] # Allow anyone to register

    def perform_create(self, serializer):
        user = serializer.save()
        # If a patient registers, automatically create a Patient profile for them
        if user.role == 'patient':
            Patient.objects.create(user=user)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'role': user.role,
        })

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    Admin can view all users. Doctors can view all users. Patients can view only their own profile.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrDoctor]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in ['admin', 'doctor']:
            return User.objects.all()
        return User.objects.filter(pk=user.pk) # Patients can only see their own profile


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed or edited.
    Admin/Doctor: Full CRUD on all patients.
    Patient: Read-only on their own profile.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrDoctor]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in ['admin', 'doctor']:
            return Patient.objects.all()
        return Patient.objects.filter(user=user) # Patients can only see their own patient profile

    def perform_create(self, serializer):
        # When a doctor/admin creates a patient, they might create a new user too
        # Or link to an existing user. For simplicity, let's assume linking to existing user.
        # If creating a new user, you'd need more logic here or a separate endpoint.
        patient = serializer.save()
        # If the user creating this patient is a patient themselves, link it to their user profile
        if self.request.user.role == 'patient' and not patient.user:
            patient.user = self.request.user
            patient.save()

    def create(self, request, *args, **kwargs):
        # Doctors/Admins can create patients and link them to existing users or create new users.
        # For simplicity, this example assumes linking to an existing user or creating a patient profile
        # for the currently logged-in user if they are a patient.
        # A more robust solution would have a separate user creation endpoint for doctors/admins.
        user_id = request.data.get('user')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Ensure only admins/doctors can link to other users
                if not (request.user.role in ['admin', 'doctor'] or request.user.is_staff) and user != request.user:
                    return Response({"detail": "You do not have permission to create a patient profile for another user."}, status=status.HTTP_403_FORBIDDEN)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If no user_id provided, and current user is a patient, assume it's for them
            if request.user.role == 'patient':
                user = request.user
            else:
                return Response({"error": "User ID is required to create a patient profile."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a patient profile already exists for this user
        if hasattr(user, 'patient_profile') and user.patient_profile:
            return Response({"error": f"Patient profile already exists for user {user.username}."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save(user=user) # Link patient to the user
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class WoundImageViewSet(viewsets.ModelViewSet):
    queryset = WoundImage.objects.all().select_related('patient', 'analysis').order_by('-uploaded_at')
    serializer_class = WoundImageSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrDoctor] # Apply custom permission

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in ['admin', 'doctor']:
            return WoundImage.objects.all().select_related('patient', 'analysis')
        # Patients can only see their own wound images
        return WoundImage.objects.filter(patient__user=user).select_related('patient', 'analysis')

    def create(self, request, *args, **kwargs):
        try:
            patient_id = request.data.get('patient')
            image_data = request.data.get('image') # Base64 encoded image
            notes = request.data.get('notes', '')

            if not patient_id or not image_data:
                return Response({"error": "Patient ID and image data are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                patient = Patient.objects.get(id=patient_id)
                # Permission check: Only the patient themselves, doctors, or admins can upload for this patient
                if not (request.user == patient.user or request.user.role in ['doctor', 'admin'] or request.user.is_staff):
                    return Response({"detail": "You do not have permission to upload images for this patient."}, status=status.HTTP_403_FORBIDDEN)
            except Patient.DoesNotExist:
                return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

            # Decode base64 image
            try:
                if ";" not in image_data or "," not in image_data:
                    raise ValueError("Image data is not in expected base64 format (e.g., data:image/jpeg;base64,...)")
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                image_file_name = f'{patient.user.username}_wound_{uuid.uuid4()}.{ext}'
                image_file = ContentFile(base64.b64decode(imgstr), name=image_file_name)
            except Exception as e:
                print(f"Error decoding image data: {e}")
                return Response({"error": f"Invalid image format or decode error: {e}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create WoundImage object first to get an ID for analysis
            wound_image = None
            try:
                wound_image = WoundImage.objects.create(patient=patient, image=image_file, notes=notes)
            except IntegrityError as e:
                return Response({"error": f"Database error creating wound image: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Convert image_file to numpy array for ML pipeline
            image_pil = Image.open(wound_image.image.path).convert("RGB")
            image_np = np.array(image_pil)

            # Prepare structured features for ML pipeline from request data or defaults
            structured_features = {
                "WoundArea": request.data.get("wound_area_input", 50.0), # Example default
                "WoundDepth": request.data.get("wound_depth_input", "Partial Thickness"),
                "SloughPercentage": request.data.get("slough_percentage_input", 0.0),
                "GranulationPercentage": request.data.get("granulation_percentage_input", 0.0),
                "Comorbidities": request.data.get("comorbidities_input", 0),
                "InfectionStatus": request.data.get("infection_status_input", 0),
                "ABIDoppler": request.data.get("abi_doppler_input", 1.0),
                "DressingFrequency": request.data.get("dressing_frequency_input", 3),
                "PriorHealingResponse": request.data.get("prior_healing_response_input", 1),
                "WoundType": "Abrasions" # This will be overwritten by ML prediction
            }
            structured_features_df = pd.DataFrame([structured_features])

            # --- Run ML Pipeline ---
            ml_analysis_results = _run_ml_pipeline(image_np, structured_features_df)
            
            ai_data = ml_analysis_results

            print("AI Data (from ML pipeline) used for analysis:", ai_data)

            wound_analysis_data = {
                "wound_image": wound_image,
                "is_wound": ai_data.get("is_wound", False),
                "rejection_reason": ai_data.get("rejection_reason"),
                "wound_area_cm2": ai_data.get("wound_area_cm2"),
                "estimated_depth_mm": ai_data.get("estimated_depth_mm"),
                "estimated_distance_cm": ai_data.get("estimated_distance_cm"),
                "healing_stage": ai_data.get("healing_stage"),
                "tissue_type": ai_data.get("tissue_type"),
                "exudate": ai_data.get("exudate"),
                "odor": ai_data.get("odor"),
                "periwound_skin": ai_data.get("periwound_skin"),
                "potential_complications": ai_data.get("potential_complications", []),
                "recommendations": ai_data.get("recommendations", []),
                "analysis_summary": ai_data.get("analysis_summary"),
                "wound_outline_coordinates": ai_data.get("wound_outline_coordinates", [])
            }
            wound_analysis = WoundAnalysis.objects.create(**wound_analysis_data)

            # --- Matplotlib Plotting for 3D Visual ---
            if wound_analysis.is_wound and wound_analysis.wound_outline_coordinates and wound_analysis.estimated_depth_mm is not None:
                try:
                    buffer = plot_3d_wound_on_image(image_pil, wound_analysis.wound_outline_coordinates, wound_analysis.estimated_depth_mm)
                    
                    if buffer:
                        plotted_image_file_name = f'plotted_3d_{uuid.uuid4()}.jpeg'
                        wound_image.plotted_image.save(plotted_image_file_name, ContentFile(buffer.read()), save=True)
                    else:
                        wound_image.plotted_image = None
                        wound_image.save()

                except Exception as plot_e:
                    print(f"Error during Matplotlib 3D plotting: {plot_e}")
                    wound_image.plotted_image = None
                    wound_image.save()
            else:
                wound_image.plotted_image = None
                wound_image.save()
            
            serializer = WoundImageSerializer(wound_image, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"General error during wound image processing in create method: {e}")
            if 'wound_image' in locals() and wound_image is not None:
                WoundAnalysis.objects.create(
                    wound_image=wound_image,
                    is_wound=False,
                    rejection_reason=f"Processing error: {e}"
                )
                serializer = WoundImageSerializer(wound_image, context={'request': request})
                return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": f"Failed to initiate wound image processing due to: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WoundAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows wound analyses to be viewed.
    Admin/Doctor: View all analyses.
    Patient: View only their own analyses.
    """
    queryset = WoundAnalysis.objects.all().select_related('wound_image__patient').order_by('-analyzed_at')
    serializer_class = WoundAnalysisSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrDoctor]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in ['admin', 'doctor']:
            return WoundAnalysis.objects.all().select_related('wound_image__patient')
        return WoundAnalysis.objects.filter(wound_image__patient__user=user).select_related('wound_image__patient')

# Initialize ML models when Django app is ready (first request)
# This ensures models are loaded once.
# For more robust production, consider a separate ML service or Celery tasks.
_initialize_ml_models()
