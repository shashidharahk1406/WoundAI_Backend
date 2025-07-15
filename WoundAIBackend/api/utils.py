# api/utils.py

from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp_code):
    """
    Sends an OTP to the specified email address.
    """
    subject = 'Password Reset OTP for WoundAI'
    message = f'Your One-Time Password (OTP) for password reset is: {otp_code}\n\nThis OTP is valid for 5 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending OTP email to {email}: {e}")
        return False