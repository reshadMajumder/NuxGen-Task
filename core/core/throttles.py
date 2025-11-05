from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Throttle for authentication endpoints (register, login).
    Rate: 5 requests per hour for anonymous users.
    """
    scope = 'auth'


class OTPRateThrottle(AnonRateThrottle):
    """
    Throttle for OTP endpoints (verify-otp, resend-otp).
    Rate: 3 requests per hour for anonymous users.
    """
    scope = 'otp'

