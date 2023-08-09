from datetime import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models

# Create your models here.
from django.db.models import Q, F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ftms.models import Club
from knockout.models import RoundOf16, SemiFinal, Final, ThirdPlace, QuarterFinal, update_qualify_teams, QualifyTeam


class MyTournament(models.Model):
    TEAM_SIZE = (
        ('4', '4 Teams'),
        ('8', '8 Teams'),
        ('16', '16 Teams'),
        ('32', '32 Teams'),
        ('64', '64 Teams'),
    )
    TOURNAMENT_TYPE = (
        ('Groups', 'Groups & Knockout'),
        ('K/O', 'Knockout'),
    )

    STAGE_CHOICES = (
        ('Group', 'Group Stage'),
        ('Round32', 'Round of 32'),
        ('Round16', 'Round of 16'),
        ('QuarterFinal', 'Quarter Finals'),
        ('SemiFinal', 'Semi Finals'),
        ('Final', 'Final'),
        ('End', 'Tournament End'),
    )

    tournament_name = models.CharField(max_length=255)
    champion = models.ForeignKey(Club, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField()
    teams_selection = models.CharField(max_length=2, choices=TEAM_SIZE)
    tournament_type = models.CharField(max_length=8, choices=TOURNAMENT_TYPE)
    current_stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='Group')
    paired_teams = models.ManyToManyField(QualifyTeam, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    """
     def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Create RoundOf16, QuarterFinal, SemiFinal, and Final objects based on teams_selection and tournament_type
        if self.teams_selection == '32' and self.tournament_type == 'Groups':
            # Create RoundOf16, QuarterFinal, SemiFinal, and Final objects for 32 teams with Groups and Knockout format
            round_of_16 = RoundOf16.objects.create(tournament=self)
            quarter_finals = QuarterFinal.objects.create(tournament=self)
            semi_finals = SemiFinal.objects.create(tournament=self)
            final = Final.objects.create(tournament=self)
            third_place = ThirdPlace.objects.create(tournament=self)

            # Add necessary fields specific to each model
            # ... (e.g., set team1 and team2 for RoundOf16, teams for QuarterFinal, etc.)

        elif self.teams_selection == '16' and self.tournament_type == 'Groups':
            # Create QuarterFinal, SemiFinal, and Final objects for 16 teams with Groups format
            quarter_finals = QuarterFinal.objects.create(tournament=self)
            semi_finals = SemiFinal.objects.create(tournament=self)
            third_place = ThirdPlace.objects.create(tournament=self)
            final = Final.objects.create(tournament=self)

            # Add necessary fields specific to each model
            # ... (e.g., set teams for QuarterFinal, etc.)

        elif self.teams_selection == '8' and self.tournament_type == 'Groups':
            # Create SemiFinal and Final objects for 8 teams with Groups format
            semi_finals = SemiFinal.objects.create(tournament=self)
            third_place = ThirdPlace.objects.create(tournament=self)
            final = Final.objects.create(tournament=self)

            # Add necessary fields specific to each model
            # ... (e.g., set teams for SemiFinal, etc.)

        # Continue adding other conditions for different team selections and tournament types
    """
    """
 
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.tournament_type == 'Groups':
            self.create_groups_and_groupclubs()

    def create_groups_and_groupclubs(self):
        team_count = int(self.teams_selection)
        group_count = team_count // 4

        # Create groups
        for i in range(group_count):
            group = Groups.objects.create(group=chr(65 + i), tournament_id=self.id)

            # Create GroupClubs for each group
            for j in range(4):
                GroupClub.objects.create(group=group)
    
    
    !!!
    
    
        def save(self, *args, **kwargs):
        created = not self.pk  # Check if the object is being created or updated

        super().save(*args, **kwargs)

        if created:
            # Check if teams_selection is a specific choice and create GroupClubs
            if self.teams_selection == '8':
                self.create_group_clubs(8)
                if self.tournament_type == 'Groups':
                    self.create_groups(2)

    def create_group_clubs(self, num_clubs):
        for _ in range(num_clubs):
            GroupClub.objects.create(tournament=self)

    def create_groups(self, num_groups):
        group_clubs = self.groupclub_set.all()
        group_clubs_count = group_clubs.count()

        if group_clubs_count % num_groups != 0:
            raise ValueError("The number of GroupClubs is not divisible by the number of groups.")

        group_size = group_clubs_count // num_groups

        for i in range(num_groups):
            group = Groups.objects.create(tournament=self, group=f'Group {chr(ord("A") + i)}')
            start_index = i * group_size
            end_index = start_index + group_size
            group.group_club_1 = group_clubs[start_index]
            group.group_club_2 = group_clubs[start_index + 1]
            group.group_club_3 = group_clubs[start_index + 2]
            group.group_club_4 = group_clubs[start_index + 3]
            group.save()
    """

    def __str__(self):
        return self.tournament_name


class GroupClub(models.Model):
    tournament = models.ForeignKey(MyTournament, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True, blank=True)
    club_name = models.ForeignKey(Club, related_name='team', on_delete=models.CASCADE, null=True, blank=True)
    played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    draw = models.PositiveIntegerField(default=0)
    lose = models.PositiveIntegerField(default=0)
    gf = models.PositiveIntegerField(default=0)
    ga = models.PositiveIntegerField(default=0)
    gd = models.IntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    group_table_number = models.IntegerField(default=0)

    class Meta:
        ordering = ['group', '-points', '-gd']

    def calculate_goal_difference(self):
        gd = int(self.gf) - int(self.ga)
        return gd

    def get_result(self):
        total_games = self.played
        total_wins = self.wins
        total_draws = self.draw
        total_losses = self.lose

        if total_games == 0:
            return 'not played'  # Return a specific result if no games have been played yet

        if total_wins > total_losses:
            return 'win'
        elif total_wins == total_losses:
            return 'draw'
        else:
            return 'loss'

    def clean(self):
        existing_clubs = GroupClub.objects.exclude(pk=self.pk).filter(tournament=self.tournament,
                                                                      club_name=self.club_name)
        if existing_clubs.exists():
            raise ValidationError(
                'Club {} has already been added to the Group Stages of this tournament.'.format(
                    self.club_name.club_name))

    def save(self, *args, **kwargs):
        self.gd = self.calculate_goal_difference()  # Calculate goal difference before saving
        # Call the parent's save() method to save the GroupClub object
        super(GroupClub, self).save(*args, **kwargs)

        # Update the related Groups object
        if self.group:
            self.group.save()

    """
        def save(self, *args, **kwargs):
        if self.group:
            # Update the group property of the club
            self.club_name.group = self.group
            self.club_name.save()
        super().save(*args, **kwargs)
    """

    def __str__(self):
        return self.club_name.club_name


class Group(models.Model):
    GROUPS = (
        ('A', 'Group A'),
        ('B', 'Group B'),
        ('C', 'Group C'),
        ('D', 'Group D'),
        ('E', 'Group E'),
        ('F', 'Group F'),
        ('G', 'Group G'),
        ('H', 'Group H'),
        ('I', 'Group I'),
        ('J', 'Group J'),
        ('K', 'Group K'),
        ('L', 'Group L'),
        ('M', 'Group M'),
        ('N', 'Group N'),
        ('O', 'Group O'),
        ('P', 'Group P'),

    )
    tournament = models.ForeignKey(MyTournament, on_delete=models.CASCADE, related_name='groups')
    group = models.CharField(max_length=1, choices=GROUPS)
    group_club_1 = models.ForeignKey(Club, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='team_1')
    group_club_2 = models.ForeignKey(Club, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='team_2')
    group_club_3 = models.ForeignKey(Club, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='team_3')
    group_club_4 = models.ForeignKey(Club, on_delete=models.PROTECT, null=True, blank=True,
                                     related_name='team_4')
    matches_count = models.PositiveIntegerField(default=0)

    # Groups Adding to each Tournament solved: NEXT solving the Team adding to new Tournaments.
    def clean(self):
        # Check if the group is already used in this tournament
        used_groups = Group.objects.exclude(pk=self.pk).filter(tournament=self.tournament, group=self.group)
        if used_groups.exists():
            raise ValidationError('{} has already been used in this tournament.'.format(self.get_group_display()))

        # Check if a team is assigned to multiple group clubs
        group_clubs = [self.group_club_1, self.group_club_2, self.group_club_3, self.group_club_4]
        assigned_group_clubs = [gc for gc in group_clubs if gc is not None]

        if len(set(assigned_group_clubs)) != len(assigned_group_clubs):
            raise ValidationError('A team cannot be assigned to multiple group clubs.')

        # Check if teams are already assigned to other groups within this tournament
        existing_groups = Group.objects.exclude(pk=self.pk).filter(tournament=self.tournament).exclude(pk=self.pk)
        for group in existing_groups:
            assigned_clubs = [group.group_club_1, group.group_club_2, group.group_club_3, group.group_club_4]
            if any(gc in assigned_group_clubs for gc in assigned_clubs):
                raise ValidationError('One or more teams are already assigned to other groups within this tournament.')

    def save(self, *args, **kwargs):
        if self.pk:
            # Retrieve the previous instance
            prev_instance = Group.objects.get(pk=self.pk)

            # Check if the GroupClub instances have changed
            if prev_instance.group_club_1 != self.group_club_1:
                if prev_instance.group_club_1:
                    prev_instance.group_club_1.group = None  # Clear the previous group
                    prev_instance.group_club_1.save()
                if self.group_club_1:
                    self.group_club_1.group = self  # Set the new group
                    self.group_club_1.save()

            if prev_instance.group_club_2 != self.group_club_2:
                if prev_instance.group_club_2:
                    prev_instance.group_club_2.group = None  # Clear the previous group
                    prev_instance.group_club_2.save()
                if self.group_club_2:
                    self.group_club_2.group = self  # Set the new group
                    self.group_club_2.save()

            if prev_instance.group_club_3 != self.group_club_3:
                if prev_instance.group_club_3:
                    prev_instance.group_club_3.group = None  # Clear the previous group
                    prev_instance.group_club_3.save()
                if self.group_club_3:
                    self.group_club_3.group = self  # Set the new group
                    self.group_club_3.save()

            if prev_instance.group_club_4 != self.group_club_4:
                if prev_instance.group_club_4:
                    prev_instance.group_club_4.group = None  # Clear the previous group
                    prev_instance.group_club_4.save()
                if self.group_club_4:
                    self.group_club_4.group = self  # Set the new group
                    self.group_club_4.save()

        if not self.pk:
            # Save the Groups object first to generate a primary key
            super().save(*args, **kwargs)
            print('it working dummy')

            # Initialize the counter

            # Create GroupClub objects for the group_club fields
            if self.group_club_1:
                GroupClub.objects.create(
                    group=self,
                    club_name=self.group_club_1,
                    tournament=self.tournament,
                    group_table_number=int(1)
                )

            if self.group_club_2:
                GroupClub.objects.create(
                    group=self,
                    club_name=self.group_club_2,
                    tournament=self.tournament,
                    group_table_number=int(2)
                )

            if self.group_club_3:
                GroupClub.objects.create(
                    group=self,
                    club_name=self.group_club_3,
                    tournament=self.tournament,
                    group_table_number=int(3)
                )

            if self.group_club_4:
                GroupClub.objects.create(
                    group=self,
                    club_name=self.group_club_4,
                    tournament=self.tournament,
                    group_table_number=int(4)
                )
        else:
            # Get the previous state of the object
            old_group = Group.objects.get(pk=self.pk)
            super().save(*args, **kwargs)

            # Check if any of the group club fields have changed
            if self.group_club_1 != old_group.group_club_1:
                try:
                    club_1 = Club.objects.get(club_name=old_group.group_club_1)
                    group_club_1 = GroupClub.objects.get(group=self, club_name=club_1)
                    group_club_1.delete()
                except ObjectDoesNotExist:
                    # Handle the case if the club or GroupClub is not found
                    pass

                try:
                    new_club_1 = Club.objects.get(club_name=self.group_club_1)
                    GroupClub.objects.create(
                        group=self,
                        club_name=new_club_1,
                        tournament=self.tournament,
                    )
                except ObjectDoesNotExist:
                    # Handle the case if the new club is not found
                    pass

            if self.group_club_2 != old_group.group_club_2:
                try:
                    club_2 = Club.objects.get(club_name=old_group.group_club_2)
                    group_club_2 = GroupClub.objects.get(group=self, club_name=club_2)
                    group_club_2.delete()
                except ObjectDoesNotExist:
                    # Handle the case if the club or GroupClub is not found
                    pass

                try:
                    new_club_2 = Club.objects.get(club_name=self.group_club_2)
                    GroupClub.objects.create(
                        group=self,
                        club_name=new_club_2,
                        tournament=self.tournament,
                    )
                except ObjectDoesNotExist:
                    # Handle the case if the new club is not found
                    pass

                if self.group_club_3 != old_group.group_club_3:
                    try:
                        club_3 = Club.objects.get(club_name=old_group.group_club_3)
                        group_club_3 = GroupClub.objects.get(group=self, club_name=club_3)
                        group_club_3.delete()
                    except ObjectDoesNotExist:
                        # Handle the case if the club or GroupClub is not found
                        pass

                    try:
                        new_club_3 = Club.objects.get(club_name=self.group_club_3)
                        GroupClub.objects.create(
                            group=self,
                            club_name=new_club_3,
                            tournament=self.tournament,
                        )
                    except ObjectDoesNotExist:
                        # Handle the case if the new club is not found
                        pass

                    if self.group_club_4 != old_group.group_club_4:
                        try:
                            club_4 = Club.objects.get(club_name=old_group.group_club_4)
                            group_club_4 = GroupClub.objects.get(group=self, club_name=club_4)
                            group_club_4.delete()
                        except ObjectDoesNotExist:
                            # Handle the case if the club or GroupClub is not found
                            pass

                        try:
                            new_club_4 = Club.objects.get(club_name=self.group_club_4)
                            GroupClub.objects.create(
                                group=self,
                                club_name=new_club_4,
                                tournament=self.tournament,
                            )
                        except ObjectDoesNotExist:
                            # Handle the case if the new club is not found
                            pass

    def __str__(self):
        return dict(self.GROUPS)[self.group]


# models.py

class ClubHistory(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='history')
    tournament = models.ForeignKey(MyTournament, on_delete=models.CASCADE)
    # group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    played = models.IntegerField(default=0)  # Total games played by the club
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)

    # Add more fields to store additional information about club performance

    def __str__(self):
        return f"{self.club.club_name} - {self.tournament.tournament_name}"

    def update_performance(self, result):
        if result == 'win':
            self.wins += 1
        elif result == 'loss':
            self.losses += 1
        else:
            self.draws += 1
        self.played = self.wins + self.losses + self.draws
        self.save()


class Match(models.Model):
    tournament = models.ForeignKey(MyTournament, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='matches')
    team_1 = models.ForeignKey(GroupClub, on_delete=models.CASCADE, related_name='team_1_matches')
    team_2 = models.ForeignKey(GroupClub, on_delete=models.CASCADE, related_name='team_2_matches')
    date = models.DateTimeField(default=datetime.now)
    team_1_score = models.PositiveIntegerField(null=True, blank=True)
    team_2_score = models.PositiveIntegerField(null=True, blank=True)
    is_match_ended = models.BooleanField(default=False)
    is_statistics_updated = models.BooleanField(default=False)
    match_number = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-tournament', 'group', 'match_number']

    def __str__(self):
        return f"{self.team_1.club_name} vs {self.team_2.club_name} in {self.group}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_match_ended:
            self.update_statistics()
            # Check if all matches in the group have ended
            all_matches_ended = Match.objects.filter(group=self.group, is_match_ended=False).exists()
            if not all_matches_ended:
                update_qualify_teams(self.group)
                # Reset the is_statistics_updated flag for all matches in the group
                Match.objects.filter(group=self.group).update(is_statistics_updated=False)

    def update_statistics(self):
        if self.is_match_ended and not self.is_statistics_updated:
            # Update the Group matches count
            self.group.matches_count = self.group.matches.count()
            self.group.save()

            # Update GroupClub statistics for team_1
            team_1_stats = self.team_1
            team_1_stats.played += 1
            team_1_stats.gf += self.team_1_score
            team_1_stats.ga += self.team_2_score

            if self.team_1_score > self.team_2_score:
                team_1_stats.wins += 1
                team_1_stats.points += 3
            elif self.team_1_score < self.team_2_score:
                team_1_stats.lose += 1
            else:
                team_1_stats.draw += 1
                team_1_stats.points += 1

            team_1_stats.save()

            # Update GroupClub statistics for team_2
            team_2_stats = self.team_2
            team_2_stats.played += 1
            team_2_stats.gf += self.team_2_score
            team_2_stats.ga += self.team_1_score

            if self.team_2_score > self.team_1_score:
                team_2_stats.wins += 1
                team_2_stats.points += 3
            elif self.team_2_score < self.team_1_score:
                team_2_stats.lose += 1
            else:
                team_2_stats.draw += 1
                team_2_stats.points += 1

            team_2_stats.save()

            self.is_statistics_updated = True
            self.save()

@receiver(post_save, sender=GroupClub)
def create_matches(sender, instance, created, **kwargs):
    if created:
        if instance.group.tournament and instance.group.tournament.tournament_type == 'Groups':
            group = instance.group
            teams = list(group.groupclub_set.all())  # Convert the queryset to a list

            # Sort the teams list based on their primary keys to ensure consistent order
            teams.sort(key=lambda x: x.pk)

            match_order = [(0, 1), (2, 3), (1, 3), (0, 2), (3, 0), (1, 2)]

            # Check if there are four teams in the group
            if len(teams) == 4:
                # Create match instances for each combination of teams within the group
                match_number = 1
                for match_data in match_order:
                    team_1 = teams[match_data[0]]
                    team_2 = teams[match_data[1]]
                    print(str(match_data[0]), 'vs', str(match_data[1]))

                    # Check if a match between the two teams already exists
                    existing_match = Match.objects.filter(group=group, team_1=team_1, team_2=team_2).first()
                    if not existing_match:
                        match = Match(group=group, team_1=team_1, team_2=team_2, tournament=group.tournament,
                                      match_number=match_number)
                        match.save()
                    match_number += 1
            else:
                print("The group should have exactly four teams to create matches.")



"""
@receiver(post_save, sender=Match)
def match_post_save(sender, instance, **kwargs):
    # The match is newly created, update the statistics
    instance.update_statistics()
"""
