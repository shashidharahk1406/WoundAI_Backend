# # api/utils.py

# from django.core.mail import send_mail
# from django.conf import settings

# def send_otp_email(email, otp_code):
#     """
#     Sends an OTP to the specified email address.
#     """
#     subject = 'Password Reset OTP for WoundAI'
#     message = f'Your One-Time Password (OTP) for password reset is: {otp_code}\n\nThis OTP is valid for 5 minutes.'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [email]
    
#     try:
#         send_mail(subject, message, from_email, recipient_list, fail_silently=False)
#         return True
#     except Exception as e:
#         print(f"Error sending OTP email to {email}: {e}")
#         return False





# core/utils.py
import base64
from datetime import timedelta
import uuid
import io
import requests
from django.core.files.base import ContentFile
from PIL import Image
from django.conf import settings

def decode_base64_to_contentfile(data_uri: str):
    """
    Convert a data URI (data:image/jpeg;base64,xxxx) to Django ContentFile.
    Returns (ContentFile, extension)
    """
    if not data_uri or ";base64," not in data_uri:
        raise ValueError("Invalid base64 image format. Expected data:<mime>;base64,<data>")
    header, b64data = data_uri.split(";base64,")
    ext = header.split("/")[-1]
    try:
        binary = base64.b64decode(b64data)
    except Exception as e:
        raise ValueError(f"Base64 decode error: {e}")
    filename = f"{uuid.uuid4()}.{ext}"
    return ContentFile(binary, name=filename), ext

def get_image_size(path):
    with Image.open(path) as im:
        return im.width, im.height

def call_external_ai(image_base64: str, meta: dict = None):
    """
    Calls external AI model defined in settings.AI_MODEL_URL.
    Returns parsed JSON or raises.
    """
    if meta is None:
        meta = {}
    payload = {"image_base64": image_base64, "meta": meta}
    url = getattr(settings, "AI_MODEL_URL", None)
    timeout = getattr(settings, "AI_MODEL_TIMEOUT", 30)
    if not url:
        raise RuntimeError("AI_MODEL_URL not configured in settings")
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()




# api/utils.py
from rest_framework_simplejwt.tokens import AccessToken

def generate_report_share_token(report, user):
    token = AccessToken.for_user(user)
    token["report_id"] = report.id
    token.set_exp(lifetime=timedelta(minutes=15))  # link valid for 15 mins
    return str(token)
