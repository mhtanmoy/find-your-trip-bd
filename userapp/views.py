from rest_framework import status
from rest_framework import viewsets
from .serializers import UserLoginSerializer, UserRegistrationSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from utils.logging import logger
from utils.response_wrapper import ResponseWrapper


class UserLoginView(viewsets.ViewSet):
    @swagger_auto_schema(
        request_body=UserLoginSerializer,
    )
    def create(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                logger.info("User login successful")
                return ResponseWrapper(
                    data=serializer.validated_data, status=status.HTTP_200_OK
                )
            logger.error("User login failed")
            return ResponseWrapper(
                error_message=f"User login failed: {serializer.errors}",
                status=status.HTTP_400_BAD_REQUEST,
                error_code=400,
            )
        except Exception as e:
            logger.error(f"User login error: {str(e)}")
            return ResponseWrapper(
                error_message=f"User login error: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=500,
            )


class UserRegistrationView(viewsets.ViewSet):
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
    )
    def create(self, request):
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                logger.info("User registration successful")
                return ResponseWrapper(
                    data={
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_201_CREATED,
                )
            logger.error("User registration failed")
            return ResponseWrapper(
                error_message=f"User registration failed: {serializer.errors}",
                status=status.HTTP_400_BAD_REQUEST,
                error_code=400,
            )
        except Exception as e:
            logger.error(f"User registration error: {str(e)}")
            return ResponseWrapper(
                error_message=f"User registration error: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=500,
            )
