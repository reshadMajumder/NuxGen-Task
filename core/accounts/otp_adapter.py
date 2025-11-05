from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings

class OTPAdapter(ABC):
    @abstractmethod
    def send_otp(self, user, otp):
        """Send OTP to the user"""
        pass

class EmailOTPAdapter(OTPAdapter):
    def send_otp(self, user, otp):
        subject = "Your OTP Code"
        message = f"Hello {user.first_name or user.email},\n\nYour OTP code is: {otp}"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
