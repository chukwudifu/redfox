from django.db import models
from users.models import User
from helpers.models import BaseModel


class Season(models.Model):
    season = models.CharField(max_length=100)

    def __str__(self):
        return self.season


class GameScore(BaseModel):
    season = models.ForeignKey(
        Season, related_name='scoreboard_game', on_delete=models.CASCADE)
    player = models.ForeignKey(
        User, related_name='user_game', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.player.address} - {self.score}'
