from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GameScore, Season
from .services import (attempts_validator, calc_lives, update_user_score,
                       verify_health, view_player_scoreboard, view_scoreboard)


class ScoreBoardOutputSerializer(serializers.Serializer):
    player = serializers.CharField()
    score = serializers.IntegerField()
    season = serializers.CharField()
    position = serializers.IntegerField()


class CreateSeasonAPI(APIView):
    """
    Create Season API

    Endpoint for creating game seasons
    """
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Season
            fields = '__all__'
            ref_name = 'create season input'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: InputSerializer}
    )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        input_serializer.save()
        return Response(input_serializer.data)


class CreateScoreAPI(APIView):
    """
    Add Player Score

    Endpoint for adding or updating a player's score
    """
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        season = serializers.IntegerField()
        score = serializers.IntegerField()

        class Meta:
            ref_name = 'create game score input'

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = GameScore
            fields = '__all__'
            ref_name = 'create game score output'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: OutputSerializer}
    )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        user_attempts = verify_health(
            request.user, input_serializer.validated_data)

        attempts_validator(user_attempts)

        game_score = update_user_score(
            request.user, input_serializer.validated_data)

        output_data = self.OutputSerializer(game_score)

        return Response(output_data.data)


class ViewScoreboardAPI(APIView):
    """
    View Scoreboard

    Endpoint for viewing overall scoreboard
    """
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        season = serializers.IntegerField()

        class Meta:
            ref_name = 'view scoreboard input'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: ScoreBoardOutputSerializer(many=True)}
    )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        scoreboard = view_scoreboard(input_serializer.validated_data)

        output_serializer = ScoreBoardOutputSerializer(scoreboard, many=True)

        return Response(output_serializer.data)


class ViewPlayerScoreboardAPI(APIView):
    """
    View Player Scoreboard

    Endpoint for viewing a player's scoreboard details
    """
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        season = serializers.IntegerField()

        class Meta:
            ref_name = 'view player scoreboard input'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: ScoreBoardOutputSerializer(many=True)}
    )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        scoreboard = view_scoreboard(input_serializer.validated_data)

        player_scoreboard = view_player_scoreboard(scoreboard, request.user)

        output_serializer = ScoreBoardOutputSerializer(player_scoreboard)

        return Response(output_serializer.data)


class ViewPlayerLives(APIView):
    """
    View player lives

    Endpoint for checking a player's number of attempts
    """
    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        season = serializers.IntegerField()

        class Meta:
            ref_name = 'Lives input'

    class OutputSerializer(serializers.Serializer):
        current_attempts = serializers.IntegerField()
        lives_left = serializers.IntegerField()

        class Meta:
            ref_name = 'Lives output'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: OutputSerializer}
    )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        attempts = verify_health(
            request.user, input_serializer.validated_data)

        player_health = calc_lives(attempts)

        output_data = self.OutputSerializer(player_health)

        return Response(output_data.data)


class AddPointsOnlyAPI(APIView):
    """
    Add points to player

    Endpoint for adding points to player without reducing lives
    """

    permission_classes = (permissions.IsAuthenticated,)

    class InputSerializer(serializers.Serializer):
        season = serializers.IntegerField()
        score = serializers.IntegerField()

        class Meta:
            ref_name = 'add points input'

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = GameScore
            fields = '__all__'
            ref_name = 'add points output'

    @swagger_auto_schema(
        request_body=InputSerializer,
        responses={200: OutputSerializer}
    )
    def post(self, request):
        input_serializer = self.InputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        game_score = update_user_score(
            request.user, input_serializer.validated_data, ref_score=True)
        
        output_data = self.OutputSerializer(game_score)

        return Response(output_data.data)
