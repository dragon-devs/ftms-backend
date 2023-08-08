from django.db.models.signals import post_save
from django.dispatch import receiver

from knockout.models import RoundOf32, RoundOf16, QuarterFinal, SemiFinal, create_third_place_match, create_final_match, \
    create_round_of_16_matches, create_quarterfinal_matches, create_semifinals_matches


@receiver(post_save, sender=RoundOf32)
def create_round_of_16_matches_signal(sender, instance, **kwargs):
    """
    Signal handler to create RoundOf16 matches when all RoundOf32 matches have ended.
    """
    if instance.is_match_ended and instance.team1_score is not None and instance.team2_score is not None:
        tournament = instance.tournament
        all_round_of_32_matches_ended = all(
            match.is_match_ended for match in RoundOf32.objects.filter(tournament=tournament))
        if all_round_of_32_matches_ended:
            create_round_of_16_matches(tournament)


@receiver(post_save, sender=RoundOf16)
def create_quarterfinal_matches_signal(sender, instance, **kwargs):
    """
    Signal handler to create Quarterfinals matches when all RoundOf16 matches have ended.
    """
    if instance.is_match_ended and instance.team1_score is not None and instance.team2_score is not None:
        tournament = instance.tournament
        all_round_of_16_matches_ended = all(
            match.is_match_ended for match in RoundOf16.objects.filter(tournament=tournament))
        if all_round_of_16_matches_ended:
            create_quarterfinal_matches(tournament)


@receiver(post_save, sender=QuarterFinal)
def create_semifinals_matches_signal(sender, instance, **kwargs):
    """
    Signal handler to create SemiFinals matches when all Quarterfinal matches have ended.
    """
    if instance.is_match_ended and instance.team1_score is not None and instance.team2_score is not None:
        tournament = instance.tournament
        all_quarterfinal_matches_ended = all(
            match.is_match_ended for match in QuarterFinal.objects.filter(tournament=tournament))
        if all_quarterfinal_matches_ended:
            create_semifinals_matches(tournament)


@receiver(post_save, sender=SemiFinal)
def create_third_place_match_and_final_match(sender, instance, **kwargs):
    """
    Signal handler to create Third Place and Final matches when all SemiFinal matches have ended.
    """
    if instance.is_match_ended and instance.team1_score is not None and instance.team2_score is not None:
        tournament = instance.tournament
        all_semifinal_matches_ended = all(
            match.is_match_ended for match in SemiFinal.objects.filter(tournament=tournament))
        if all_semifinal_matches_ended:
            create_third_place_match(tournament)
