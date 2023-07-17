from django.urls import path

from . import apis

app_name = 'whack_blob'

urlpatterns = [
    path('create-season', apis.CreateSeasonAPI.as_view(), name='create-season'),
    path('add-score', apis.CreateScoreAPI.as_view(), name='add-score'),
    path('scoreboard', apis.ViewScoreboardAPI.as_view(), name='scoreboard'),
    path('player-scoreboard', apis.ViewPlayerScoreboardAPI.as_view(), name='player-scoreboard'),
    path('player-lives', apis.ViewPlayerLives.as_view(), name='player-lives'),
    path('add-points-alone', apis.AddPointsOnlyAPI.as_view(), name='add-points_only'),
]
