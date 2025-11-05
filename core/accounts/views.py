from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from rest_framework.views import APIView
from .otp_adapter import EmailOTPAdapter
from .utils import generate_otp

class RegisterView(generics.CreateAPIView):
    """
    Register a normal user and send OTP via email.
    Tokens will be issued only after OTP verification.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate and save OTP
        otp_code = generate_otp()
        user.otp = otp_code
        user.save()

        # Send OTP via email adapter
        otp_sender = EmailOTPAdapter()
        otp_sender.send_otp(user, otp_code)

        return Response({
            "message": "Registration successful. OTP sent to your email.",
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_201_CREATED)



class ProfileView(generics.RetrieveUpdateAPIView):
    """
    user can view and updte profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user



class LoginView(APIView):
    """
    User login view that returns JWT tokens upon successful authentication.
    
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data['user']
            tokens = serializer.create_tokens(user)

            return Response({
                'message': 'Login successful',
                'access': tokens['access'],
                'refresh': tokens['refresh'],
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as ve:
            return Response({
                'message': str(ve),
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'message': 'An error occurred during login',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class LogoutView(APIView):
    """
    takes the refresh token and blacklist for logout
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)



class VerifyOTPView(APIView):
    """
    verify OTP and issue Tokens
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"detail": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP verified
        user.otp = None
        user.save()

        # Issue JWT tokens now
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "detail": "OTP verified successfully.",
            "tokens": {
                "refresh": str(refresh),
                "access": str(access)
            }
        }, status=status.HTTP_200_OK)



class ResendOTPView(APIView):
    """
    resend otp to the user email again with newly generated otp
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        otp_code = generate_otp()
        user.otp = otp_code
        user.save()

        otp_sender = EmailOTPAdapter()
        otp_sender.send_otp(user, otp_code)

        return Response({"detail": "OTP resent successfully."}, status=status.HTTP_200_OK)


# change password view