from django.contrib.auth import get_user_model
from django.db import models

from tournament.utils import update_tournament_current_stage


class QualifyTeam(models.Model):
    tournament = models.ForeignKey('tournament.MyTournament', on_delete=models.CASCADE)
    group = models.ForeignKey('tournament.Group', on_delete=models.CASCADE)
    team = models.ForeignKey('tournament.GroupClub', on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    def __str__(self):
        return f"Qualify Team {self.group.group} {self.position}: {self.team} "


def update_qualify_teams(group):
    # Get all the teams in the group
    teams = group.groupclub_set.all()

    # Sort the teams based on points, goal difference, goals for, etc.
    teams = sorted(teams, key=lambda team: (
        -team.points,  # Descending order of points
        -team.gf,  # Descending order of goals for
        team.played  # Ascending order of matches played (lower number of matches is better)
    ))

    # Qualify the top 2 teams
    for i, team in enumerate(teams[:2], 1):
        QualifyTeam.objects.update_or_create(
            tournament=group.tournament,
            group=group,
            team=team,
            defaults={'position': i}
        )

        # Update the tournament's current_stage after all group matches have ended
        Match = get_user_model().Match
        all_matches_ended = Match.objects.filter(group=group, is_match_ended=False).exists()
        if not all_matches_ended:
            update_tournament_current_stage(group.tournament)
