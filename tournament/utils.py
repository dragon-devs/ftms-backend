from knockout.models import QualifyTeam


def update_tournament_current_stage(tournament):
    qualified_teams_count = QualifyTeam.objects.filter(tournament=tournament).count()

    if qualified_teams_count == 16:
        tournament.current_stage = 'Round16'
    elif qualified_teams_count == 8:
        tournament.current_stage = 'QuarterFinal'
    elif qualified_teams_count == 4:
        tournament.current_stage = 'SemiFinal'
    else:
        # Handle other cases if needed (e.g., finals)
        pass

    tournament.save()
