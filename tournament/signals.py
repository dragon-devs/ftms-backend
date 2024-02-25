from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from knockout.models import RoundOf16
from tournament.models import GroupClub #ClubHistory


# @receiver(post_save, sender=GroupClub)
# def update_club_history(sender, instance, **kwargs):
#     club = instance.club_name
#     tournament = instance.group.tournament
#     group = instance.group.group
#     played = instance.played
#     wins = instance.wins
#     draw = instance.draw
#     losses = instance.lose
#     result = instance.get_result()
#
#     # Check if the ClubHistory entry already exists for this club and tournament
#     club_history, created = ClubHistory.objects.get_or_create(club=club, tournament=tournament)
#
#     # Update the ClubHistory fields
#     club_history.group = group
#     club_history.played += played
#     club_history.wins += wins
#     club_history.draws += draw
#     club_history.losses += losses
#     club_history.result = result
#
#     # Save the changes
#     club_history.save()
#

@receiver(post_delete, sender=RoundOf16)
def update_tournament_paired_teams(sender, instance, **kwargs):
    # Get the tournament associated with the RoundOf16 instance
    tournament = instance.tournament

    # Remove the team from the paired_teams field
    tournament.paired_teams.remove(instance.team1)
    tournament.paired_teams.remove(instance.team2)
