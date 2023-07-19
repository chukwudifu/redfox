from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from drf_yasg.utils import swagger_auto_schema

from .models import User

from .services import get_player_profile, save_referral_details, user_login


class LoginAPI(APIView):
    """
    Metamask Login

    Endpoint for handling wallet login
    """
    permission_classes = (permissions.AllowAny,)

    class InputSerializer(serializers.Serializer):
        address = serializers.CharField()
        signature = serializers.CharField()
        message = serializers.CharField()

        class Meta:
            ref_name = 'login input'

    class RefreshTokenSerializer(serializers.Serializer):
        access_token = serializers.CharField()
        refresh_token = serializers.CharField()

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: RefreshTokenSerializer}
        )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            result = user_login(**input_serializer.validated_data)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(result, status=status.HTTP_200_OK)
    

class SaveReferralDetails(APIView):
    """
    Save a user's referrer

    Endpoint for saving a user's referrer
    """    
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        referral_address = serializers.CharField()
        referrer_username = serializers.CharField()

        class Meta:
            ref_name = 'save ref'

    @swagger_auto_schema(
        request_body=InputSerializer)
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        save_referral_details(**input_serializer)

        return Response(status=status.HTTP_200_OK)
    

class ViewProfile(APIView):
    """
    View a user profile

    Endpoint for viewing user profile
    """    
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        address = serializers.CharField()

        class Meta:
            ref_name = 'view profile'

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [
                'address',
                'referral_username',
                'referrer_username',
                'referral_count'
            ]
            ref_name = 'view profile out'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: OutputSerializer}
        )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        player_profile = get_player_profile(**input_serializer)

        output_serializer = self.OutputSerializer(player_profile)

        return Response(output_serializer.data)
