import random

def generate_otp(length=6):
    """
    Generate a numeric OTP of given length.
    Default length is 6 digits.
    """
    if length < 4:
        length = 4  # minimum OTP length
    if length > 10:
        length = 10  # max OTP length to avoid huge numbers
    return str(random.randint(10**(length-1), 10**length - 1))


def send_otp_debug(user_email, otp):
    """
    Debug helper: Print OTP instead of sending email.
    Useful for local dev without SMTP setup.
    """
    print(f"[DEBUG] OTP for {user_email}: {otp}")
