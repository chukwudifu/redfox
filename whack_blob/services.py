from datetime import date
from users.models import User
from .models import GameScore, Season
from rest_framework.exceptions import ValidationError


def verify_health(user: User, validated_data: dict) -> int:
    game_season_pk = validated_data.get('season')
    today = date.today()
    players_today_games = GameScore.objects.filter(
        season__pk=game_season_pk,
        player__pk=user.id,
        created_at__year=today.year,
        created_at__month=today.month,
        created_at__day=today.day
    )

    return players_today_games.count()


def attempts_validator(user_attempts: int):
    if user_attempts == 3:
        raise ValidationError(
            "You don't have any lives left"
        )


def calc_lives(attempts: int) -> dict:
    lives_left = 3 - attempts

    player_health = {'current_attempts': attempts, 'lives_left': lives_left}

    return player_health


def update_user_score(user: User, validated_data: dict) -> GameScore:
    user_pk = user.id
    game_season_pk = validated_data.get('season')
    try:
        additional_score = int(validated_data.get('score'))
    except TypeError:
        raise ValidationError('Invalid value provided for score')

    try:
        game_season = Season.objects.get(pk=game_season_pk)
    except Season.DoesNotExist:
        raise ValidationError('Season not found')

    latest_game_score = 0

    try:
        latest_game = GameScore.objects.filter(
            player__pk=user_pk, season__pk=game_season.pk).latest('created_at')
        latest_game_score = latest_game.score
    except GameScore.DoesNotExist:
        pass

    updated_score = additional_score + latest_game_score
    new_game = GameScore.objects.create(
        player=user, season=game_season, score=updated_score)

    return new_game


def view_scoreboard(data: dict) -> list:
    game_season_pk = data.get('season')
    season_players = GameScore.objects.filter(
        season__pk=1).order_by().values_list('player', flat=True).distinct()
    scoreboard = get_scoreboard_list(season_players, game_season_pk)
    sorted_scoreboard = sort_scoreboard_list(scoreboard)
    season_name = get_season_name(game_season_pk)
    scoreboard_with_positions = assign_positions(
        sorted_scoreboard, season_name)

    return scoreboard_with_positions


def get_scoreboard_list(season_players: list, season_pk: int) -> list:
    scoreboard = []

    for player in season_players:
        latest_game = GameScore.objects.filter(
            season__pk=season_pk, player__pk=player).latest('created_at')
        scoreboard.append(latest_game)

    return scoreboard


def sort_scoreboard_list(scoreboard: list) -> list:
    sorted_scoreboard = sorted(
        scoreboard, key=lambda game: game.score, reverse=True)

    return sorted_scoreboard


def view_player_scoreboard(scoreboard_with_positions: list, user: User) -> dict:
    user_address = user.address
    user_address_lower = user_address.lower()
    found = False
    for game_score in scoreboard_with_positions:
        scoreboard_address = game_score.get('player')
        scoreboard_address_lower = scoreboard_address.lower()
        if scoreboard_address_lower == user_address_lower:
            found = True
            return game_score
    if not found:
        raise ValidationError('user not found')


def assign_positions(scoreboard: list, season_name: str) -> list:
    counter = 0
    player_scoreboard_list = []
    for game_score in scoreboard:
        player_scoreboard = {}
        player_scoreboard['player'] = game_score.player.address
        player_scoreboard['score'] = game_score.score
        player_scoreboard['season'] = season_name
        player_scoreboard['position'] = counter + 1
        counter += 1
        player_scoreboard_list.append(player_scoreboard)

    return player_scoreboard_list


def get_season_name(season_id: int) -> str:
    season = Season.objects.get(pk=season_id)
    season_name = season.season

    return season_name
