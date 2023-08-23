from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.datetime_safe import datetime
from django.db.models import F
from football_tournaments_management_system import settings

User = get_user_model()

tournament = 'tournament.MyTournament'


class QualifyTeam(models.Model):
    tournament = models.ForeignKey('tournament.MyTournament', on_delete=models.CASCADE)
    group = models.ForeignKey('tournament.Group', on_delete=models.CASCADE, blank=True, null=True)
    team = models.ForeignKey('tournament.GroupClub', on_delete=models.CASCADE)
    # knockout_team = models.ForeignKey('ftms.Club', on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    group_position = models.CharField(max_length=2, blank=True, null=True)
    r32w = models.BooleanField(default=False)
    r16w = models.BooleanField(default=False)
    qfw = models.BooleanField(default=False)
    tpw = models.BooleanField(default=False)
    sfl = models.BooleanField(default=False)
    sfw = models.BooleanField(default=False)
    champion = models.BooleanField(default=False)

    """
       @property
    def champion(self):
        # Here, you can define the logic to determine if the team is the champion
        # For example, you might have a boolean field in your model to mark the champion team
        return self.is_champion  # Replace 'is_champion' with the actual field name
    """

    def get_group_position(self):
        return f"{self.group.group}{self.position}"

    def save(self, *args, **kwargs):
        self.group_position = self.get_group_position()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Qualify Team : {self.group.group}{self.position} - {self.team}"

    class Meta:
        ordering = ['-champion', '-sfw', '-tpw', '-qfw']


def all_group_matches_ended(tournament):
    # Get all the groups for the tournament
    groups = tournament.groups.all()
    Match = apps.get_model('tournament', 'Match')

    # Check if all group matches have ended
    for group in groups:
        if Match.objects.filter(group=group, is_match_ended=False).exists():
            return False

    return True


def update_tournament_current_stage(tournament):
    qualified_teams_count = QualifyTeam.objects.filter(tournament=tournament)

    if qualified_teams_count.count() == 32:
        tournament.current_stage = 'Round32'
    elif qualified_teams_count.count() == 16:
        tournament.current_stage = 'Round16'
        for team in qualified_teams_count:
            if all_group_matches_ended(tournament):
                team.r32w = True
                team.save()
    elif qualified_teams_count.count() == 8:
        tournament.current_stage = 'QuarterFinal'
        for team in qualified_teams_count:
            if all_group_matches_ended(tournament):
                team.r16w = True
                team.save()
    elif qualified_teams_count.count() == 4:
        tournament.current_stage = 'SemiFinal'
        for team in qualified_teams_count:
            if all_group_matches_ended(tournament):
                team.qfw = True
                team.save()
    else:
        for team in qualified_teams_count:
            if all_group_matches_ended(tournament):
                team.sfw = True
                team.save()
        tournament.current_stage = 'Final'
        # Handle other cases if needed (e.g., finals)


    if all_group_matches_ended(tournament):
        tournament.save()
        create_round_of_32_matches(tournament)
        create_round_of_16_matches(tournament)
        create_quarterfinal_matches(tournament)
        create_semifinals_matches(tournament)
        create_final_match(tournament)


def determine_r16w(match):
    # Check if both team1_score and team2_score are not None before making the comparison
    if match.team1_score is not None and match.team2_score is not None:
        if match.team1_score > match.team2_score:
            return match.team1
        elif match.team1_score < match.team2_score:
            return match.team2
        else:
            # Handle draw scenario if needed
            return None
    else:
        return None  # If the match has not ended, return None to indicate no winner has been determined yet


def create_round_of_32_matches(tournament):
    if tournament.current_stage == 'Round32':
        qualified_teams = QualifyTeam.objects.filter(tournament=tournament).order_by('group', 'position')
        # Group the qualified teams by group
        groups = {}
        for team in qualified_teams:
            if team.group in groups:
                groups[team.group].append(team)
            else:
                groups[team.group] = [team]

        # Create RoundOf16 matches
        round_of_32_matches = []
        group_keys = list(groups.keys())
        paired_teams = list(tournament.paired_teams.all())
        count = 1
        for i in range(0, len(group_keys), 2):
            group1 = groups[group_keys[i]]
            group2 = groups[group_keys[i + 1]]
            for j in range(len(group1)):
                team1 = group1[j]
                team2 = group2[-(j + 1)]
                if team1 not in paired_teams and team2 not in paired_teams and team2.group != team1.group:
                    round_of_32_match = RoundOf32.objects.create(
                        tournament=tournament,
                        team1=team1,
                        team2=team2,
                        position=count
                    )
                    # Determine the winner and update the QualifyTeam instances
                    count += 1
                    round_of_32_matches.append(round_of_32_match)
                    paired_teams.append(team1)
                    paired_teams.append(team2)

        tournament.paired_teams.set(paired_teams)
        return round_of_32_matches


class RoundOf32(models.Model):
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(QualifyTeam, related_name='round_of_32_team1', on_delete=models.CASCADE, null=True,
                              blank=True)
    team2 = models.ForeignKey(QualifyTeam, related_name='round_of_32_team2', on_delete=models.CASCADE, null=True,
                              blank=True)
    date = models.DateTimeField(default=datetime.now)
    # location = models.CharField(max_length=100)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    position = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # After the match has been saved, check if all RoundOf16 matches have ended

        # Call the create_quarterfinal_matches function to create Quarterfinals matches
        if self.is_match_ended and self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.team1.r32w = True
                self.team1.position = self.position
                self.team1.save()
            elif self.team1_score < self.team2_score:
                self.team2.r32w = True
                self.team2.position = self.position
                self.team2.save()

            all_round_of_32_matches_ended = all(
                match.is_match_ended for match in RoundOf32.objects.filter(tournament=self.tournament))
            if all_round_of_32_matches_ended:
                # Update the tournament's current stage to Quarterfinals
                self.tournament.current_stage = 'Round16'
                self.tournament.save()

            create_round_of_16_matches(self.tournament)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Round Of 32 : {self.team1} vs {self.team2}"

    # You can add additional fields or methods to capture match details and results


def create_round_of_16_matches(tournament):
    if tournament.current_stage == 'Round16':
        qualified_teams_checking = QualifyTeam.objects.filter(tournament=tournament)
        if qualified_teams_checking.count() == 16 and all_group_matches_ended(tournament):
            print('directmatches16')
            qualified_teams = QualifyTeam.objects.filter(tournament=tournament).order_by('group', 'position')

            # Group the qualified teams by group
            groups = {}
            for team in qualified_teams:
                if team.group in groups:
                    groups[team.group].append(team)
                else:
                    groups[team.group] = [team]

            # Create RoundOf16 matches
            round_of_16_matches = []
            group_keys = list(groups.keys())
            paired_teams = list(tournament.paired_teams.all())
            count = 1
            for i in range(0, len(group_keys), 2):
                group1 = groups[group_keys[i]]
                group2 = groups[group_keys[i + 1]]
                for j in range(len(group1)):
                    team1 = group1[j]
                    team2 = group2[-(j + 1)]
                    if team1 not in paired_teams and team2 not in paired_teams and team2.group != team1.group:
                        round_of_16_match = RoundOf16.objects.create(
                            tournament=tournament,
                            team1=team1,
                            team2=team2,
                            position=count
                        )

                        # Determine the winner and update the QualifyTeam instances

                        count += 1
                        round_of_16_matches.append(round_of_16_match)
                        paired_teams.append(team1)
                        paired_teams.append(team2)

            tournament.paired_teams.set(paired_teams)
            return round_of_16_matches
        else:
            print('Received from Round of 32 Round of 16 matches')

            # Retrieve the qualified teams and order them by position
            qualified_teams = QualifyTeam.objects.filter(tournament=tournament, r32w=True).order_by(
                'position')

            paired_teams_odd = []
            paired_teams_even = []

            def match_exists(team1, team2):
                return RoundOf16.objects.filter(
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                ).exists()

            round_of_16_matches = []

            if qualified_teams.count() >= 3:
                paired_teams_odd = []
                paired_teams_even = []

                for team in qualified_teams:
                    if team.position in [1, 3, 5, 7, 9, 11, 13, 15]:
                        paired_teams_odd.append(team)
                    else:
                        paired_teams_even.append(team)

                # Pair the teams with odd positions (1, 3, 5, 7)
                for idx in range(0, len(paired_teams_odd), 2):
                    if idx + 1 < len(paired_teams_odd):
                        team1_winner = paired_teams_odd[idx]
                        team2_winner = paired_teams_odd[idx + 1]

                        if not match_exists(team1_winner, team2_winner):
                            round_of_16_match = RoundOf16.objects.create(
                                tournament=tournament,
                                team1=team1_winner,
                                team2=team2_winner,
                                position=(idx // 2) + 1  # Assign the correct quarterfinal position
                            )
                            round_of_16_matches.append(round_of_16_match)

                # Pair the teams with even positions (2, 4, 6)
                for idx in range(0, len(paired_teams_even), 2):
                    if idx + 1 < len(paired_teams_even):
                        team1_winner = paired_teams_even[idx]
                        team2_winner = paired_teams_even[idx + 1]

                        if not match_exists(team1_winner, team2_winner):
                            round_of_16_match = RoundOf16.objects.create(
                                tournament=tournament,
                                team1=team1_winner,
                                team2=team2_winner,
                                position=((idx // 2) + 1) + len(paired_teams_odd) // 2
                                # Assign the correct quarterfinal position
                            )
                            round_of_16_matches.append(round_of_16_match)

                return round_of_16_matches


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
    # Update the tournament's current_stage after all group matches have ended

    Match = apps.get_model('tournament', 'Match')
    all_matches_ended = Match.objects.filter(group=group, is_match_ended=False).exists()
    if not all_matches_ended:
        update_tournament_current_stage(group.tournament)


class RoundOf16(models.Model):
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(QualifyTeam, related_name='round_of_16_team1', on_delete=models.CASCADE, null=True,
                              blank=True)
    team2 = models.ForeignKey(QualifyTeam, related_name='round_of_16_team2', on_delete=models.CASCADE, null=True,
                              blank=True)
    date = models.DateTimeField(default=datetime.now)
    # location = models.CharField(max_length=100)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    position = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # After the match has been saved, check if all RoundOf16 matches have ended

        # Call the create_quarterfinal_matches function to create Quarterfinals matches
        if self.is_match_ended and self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.team1.r16w = True
                self.team1.position = self.position
                self.team1.save()
            elif self.team1_score < self.team2_score:
                self.team2.r16w = True
                self.team2.position = self.position
                self.team2.save()

            all_round_of_16_matches_ended = all(
                match.is_match_ended for match in RoundOf16.objects.filter(tournament=self.tournament))
            if all_round_of_16_matches_ended:
                # Update the tournament's current stage to Quarterfinals
                self.tournament.current_stage = 'QuarterFinal'
                self.tournament.save()

            create_quarterfinal_matches(self.tournament)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Round Of 16 : {self.team1} vs {self.team2}"

    # You can add additional fields or methods to capture match details and results


def create_quarterfinal_matches(tournament):
    if tournament.current_stage == 'QuarterFinal':
        qualified_teams_checking = QualifyTeam.objects.filter(tournament=tournament)
        if qualified_teams_checking.count() == 8 and all_group_matches_ended(tournament):
            print('16 teams tournament quarterfinals.')

            qualified_teams = QualifyTeam.objects.filter(tournament=tournament, r16w=True).order_by('group', 'position')

            # Group the qualified teams by group
            groups = {}
            for team in qualified_teams:
                if team.group in groups:
                    groups[team.group].append(team)
                else:
                    groups[team.group] = [team]

            # Create RoundOf16 matches
            round_of_16_matches = []
            group_keys = list(groups.keys())
            paired_teams = list(tournament.paired_teams.all())
            count = 1
            for i in range(0, len(group_keys), 2):
                group1 = groups[group_keys[i]]
                group2 = groups[group_keys[i + 1]]
                for j in range(len(group1)):
                    team1 = group1[j]
                    team2 = group2[-(j + 1)]
                    if team1 not in paired_teams and team2 not in paired_teams and team2.group != team1.group:
                        round_of_16_match = QuarterFinal.objects.create(
                            tournament=tournament,
                            team1=team1,
                            team2=team2,
                            position=count
                        )

                        # Determine the winner and update the QualifyTeam instances

                        count += 1
                        round_of_16_matches.append(round_of_16_match)
                        paired_teams.append(team1)
                        paired_teams.append(team2)

            tournament.paired_teams.set(paired_teams)
            return round_of_16_matches

        else:
            print('Received from Round of 16 quarterfinals.')

            # Retrieve the qualified teams and order them by position
            qualified_teams = QualifyTeam.objects.filter(tournament=tournament, r16w=True).order_by(
                'position')

            paired_teams_odd = []
            paired_teams_even = []

            def match_exists(team1, team2):
                return QuarterFinal.objects.filter(
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                ).exists()

            quarterfinal_matches = []

            if qualified_teams.count() >= 3:
                paired_teams_odd = []
                paired_teams_even = []

                for team in qualified_teams:
                    if team.position in [1, 3, 5, 7]:
                        paired_teams_odd.append(team)
                    else:
                        paired_teams_even.append(team)

                # Pair the teams with odd positions (1, 3, 5, 7)
                for idx in range(0, len(paired_teams_odd), 2):
                    if idx + 1 < len(paired_teams_odd):
                        team1_winner = paired_teams_odd[idx]
                        team2_winner = paired_teams_odd[idx + 1]

                        if not match_exists(team1_winner, team2_winner):
                            quarterfinal_match = QuarterFinal.objects.create(
                                tournament=tournament,
                                team1=team1_winner,
                                team2=team2_winner,
                                position=(idx // 2) + 1  # Assign the correct quarterfinal position
                            )
                            quarterfinal_matches.append(quarterfinal_match)

                # Pair the teams with even positions (2, 4, 6)
                for idx in range(0, len(paired_teams_even), 2):
                    if idx + 1 < len(paired_teams_even):
                        team1_winner = paired_teams_even[idx]
                        team2_winner = paired_teams_even[idx + 1]

                        if not match_exists(team1_winner, team2_winner):
                            quarterfinal_match = QuarterFinal.objects.create(
                                tournament=tournament,
                                team1=team1_winner,
                                team2=team2_winner,
                                position=((idx // 2) + 1) + len(paired_teams_odd) // 2
                                # Assign the correct quarterfinal position
                            )
                            quarterfinal_matches.append(quarterfinal_match)

                return quarterfinal_matches

        



class QuarterFinal(models.Model):
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(QualifyTeam, related_name='quarter_final_team1', on_delete=models.CASCADE, null=True,
                              blank=True)
    team2 = models.ForeignKey(QualifyTeam, related_name='quarter_final_team2', on_delete=models.CASCADE, null=True,
                              blank=True)
    date = models.DateTimeField(default=datetime.now)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    position = models.PositiveIntegerField(null=True, blank=True)

    # Add any other fields you need for the match
    def save(self, *args, **kwargs):
        # Call the create_quarterfinal_matches function to create SemiFinals matches
        if self.is_match_ended and self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.team1.qfw = True
                self.team1.position = self.position
                self.team1.save()
            elif self.team1_score < self.team2_score:
                self.team2.qfw = True
                self.team2.position = self.position
                self.team2.save()

            all_quarterfinal_matches_ended = all(
                match.is_match_ended for match in QuarterFinal.objects.filter(tournament=self.tournament))
            if all_quarterfinal_matches_ended:
                # Update the tournament's current stage to SemiFinals
                self.tournament.current_stage = 'SemiFinal'
                self.tournament.save()

            create_semifinals_matches(self.tournament)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quarter Final :{self.team1} vs {self.team2}"


def create_semifinals_matches(tournament):
    if tournament.current_stage == 'SemiFinal':
        qualified_teams_checking = QualifyTeam.objects.filter(tournament=tournament)
        if qualified_teams_checking.count() == 4 and all_group_matches_ended(tournament):
            print('8 Teams tournament semifinals.')

            qualified_teams = QualifyTeam.objects.filter(tournament=tournament, qfw=True).order_by('group', 'position')

            # Group the qualified teams by group
            groups = {}
            for team in qualified_teams:
                if team.group in groups:
                    groups[team.group].append(team)
                else:
                    groups[team.group] = [team]

            # Create RoundOf16 matches
            round_of_16_matches = []
            group_keys = list(groups.keys())
            paired_teams = list(tournament.paired_teams.all())
            count = 1
            for i in range(0, len(group_keys), 2):
                group1 = groups[group_keys[i]]
                group2 = groups[group_keys[i + 1]]
                for j in range(len(group1)):
                    team1 = group1[j]
                    team2 = group2[-(j + 1)]
                    if team1 not in paired_teams and team2 not in paired_teams and team2.group != team1.group:
                        round_of_16_match = SemiFinal.objects.create(
                            tournament=tournament,
                            team1=team1,
                            team2=team2,
                            position=count
                        )

                        # Determine the winner and update the QualifyTeam instances
                        count+1
                        round_of_16_matches.append(round_of_16_match)
                        paired_teams.append(team1)
                        paired_teams.append(team2)

            tournament.paired_teams.set(paired_teams)
            return round_of_16_matches
        else:
            print('Received from quarterfinals. semifinals.')

            # Retrieve the qualified teams and order them by position
            qualified_teams = QualifyTeam.objects.filter(tournament=tournament, qfw=True).order_by(
                'position')

            paired_teams_odd = []
            paired_teams_even = []

            def match_exists(team1, team2):
                return SemiFinal.objects.filter(
                    tournament=tournament,
                    team1=team1,
                    team2=team2,
                ).exists()

            semifinals_matches = []

            if qualified_teams.count() >= 2:
                paired_teams_odd = []
                paired_teams_even = []

                for team in qualified_teams:
                    if team.position in [1, 3, 5, 7]:
                        paired_teams_odd.append(team)
                    else:
                        paired_teams_even.append(team)

                # Pair the teams with odd positions (1, 3, 5, 7)
                for idx in range(0, len(paired_teams_odd), 1):
                    if idx + 1 < len(paired_teams_odd):
                        team1_winner = paired_teams_odd[idx]
                        team2_winner = paired_teams_odd[idx + 1]

                        if not match_exists(team1_winner, team2_winner):
                            semifinal_match = SemiFinal.objects.create(
                                tournament=tournament,
                                team1=team1_winner,
                                team2=team2_winner,
                                position=(idx // 2) + 1  # Assign the correct quarterfinal position
                            )
                            semifinals_matches.append(semifinal_match)

                # Pair the teams with even positions (2, 4, 6)
                for idx in range(0, len(paired_teams_even), 2):
                    if idx + 1 < len(paired_teams_even):
                        team1_winner = paired_teams_even[idx]
                        team2_winner = paired_teams_even[idx + 1]

                        if not match_exists(team1_winner, team2_winner):
                            semifinal_match = SemiFinal.objects.create(
                                tournament=tournament,
                                team1=team1_winner,
                                team2=team2_winner,
                                position=((idx // 2) + 1) + len(paired_teams_odd) // 2
                                # Assign the correct quarterfinal position
                            )
                            semifinals_matches.append(semifinal_match)

                return semifinals_matches


class SemiFinal(models.Model):
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(QualifyTeam, related_name='semi_final_team1', on_delete=models.CASCADE, null=True,
                              blank=True)
    team2 = models.ForeignKey(QualifyTeam, related_name='semi_final_team2', on_delete=models.CASCADE, null=True,
                              blank=True)
    date = models.DateTimeField(default=datetime.now)
    # location = models.CharField(max_length=100)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    position = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Call the create_quarterfinal_matches function to create SemiFinals matches
        if self.is_match_ended and self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.team1.sfw = True
                self.team2.sfl = True
                self.team1.save()
                self.team2.save()
            elif self.team1_score < self.team2_score:
                self.team2.sfw = True
                self.team1.sfl = True
                self.team2.save()
                self.team1.save()
            create_third_place_match(self.tournament)

        super().save(*args, **kwargs)

        all_semifinal_matches_ended = all(
            match.is_match_ended for match in SemiFinal.objects.filter(tournament=self.tournament))
        if all_semifinal_matches_ended:
            # Update the tournament's current stage to Final
            self.tournament.current_stage = 'Final'
            self.tournament.save()

    def __str__(self):
        return f"Semi Final : {self.team1} vs {self.team2}"


def create_third_place_match(tournament):
    # Check if a ThirdPlace match already exists for the given tournament
    if ThirdPlace.objects.filter(tournament=tournament).exists():
        return None

    # Retrieve the qualified teams and order them by position
    qualified_teams = QualifyTeam.objects.filter(tournament=tournament, sfl=True)

    # Check if there are exactly 2 qualified teams left (the two teams that lost in the SemiFinals)

    if qualified_teams.count() == 2:
        team1_loser = qualified_teams[0]
        team2_loser = qualified_teams[1]

        third_place_match = ThirdPlace.objects.create(
            tournament=tournament,
            team1=team1_loser,
            team2=team2_loser,
            position=1
        )

        # Create the final match as well
        create_final_match(tournament)

        return third_place_match
    else:
        return None


class ThirdPlace(models.Model):
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(QualifyTeam, related_name='third_place_team1', on_delete=models.CASCADE, null=True,
                              blank=True)
    team2 = models.ForeignKey(QualifyTeam, related_name='third_place_team2', on_delete=models.CASCADE, null=True,
                              blank=True)
    date = models.DateTimeField(default=datetime.now)

    # location = models.CharField(max_length=100)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    position = models.PositiveIntegerField(null=True, blank=True)


    def save(self, *args, **kwargs):
        # Call the create_quarterfinal_matches function to create SemiFinals matches
        if self.is_match_ended and self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.team1.tpw = True
                self.team1.save()
            elif self.team1_score < self.team2_score:
                self.team2.tpw = True
                self.team2.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Third Place Match : {self.team1} vs {self.team2}"


def create_final_match(tournament):

    # Retrieve the qualified teams and order them by position
    qualified_teams = QualifyTeam.objects.filter(tournament=tournament, sfw=True)

    # Check if there are at least 2 qualified teams
    if qualified_teams.count() == 2:
        def match_exists(team1, team2):
            return Final.objects.filter(
                tournament=tournament,
                team1=team1,
                team2=team2,
            ).exists()

        team1_winner = qualified_teams[0]
        team2_winner = qualified_teams[1]

        if not match_exists(team1_winner, team2_winner):
            final_match = Final.objects.create(
                tournament=tournament,
                team1=team1_winner,
                team2=team2_winner,
                position=1,
            )
            return final_match
        return None


class Final(models.Model):
    tournament = models.ForeignKey(tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(QualifyTeam, related_name='final_team1', on_delete=models.CASCADE, null=True,
                              blank=True)
    team2 = models.ForeignKey(QualifyTeam, related_name='final_team2', on_delete=models.CASCADE, null=True,
                              blank=True)
    date = models.DateTimeField(default=datetime.now)
    # location = models.CharField(max_length=100)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    position = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Call the create_quarterfinal_matches function to create SemiFinals matches
        if self.is_match_ended and self.team1_score is not None and self.team2_score is not None:
            if self.team1_score > self.team2_score:
                self.team1.champion = True
                self.team1.save()
                self.tournament.champion = self.team1.team.club_name

            elif self.team1_score < self.team2_score:
                self.team2.champion = True
                self.team2.save()
                self.tournament.champion = self.team2.team.club_name

            self.tournament.current_stage = "End"
            self.tournament.save()
        super().save(*args, **kwargs)

    # Add more fields as needed, such as match date, time, venue, etc.

    def __str__(self):
        return f"Final Match : {self.team1} vs {self.team2}"
