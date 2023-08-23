from datetime import datetime

from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ftms.models import Club
from ftms.serializers import ClubSerializer
from tournament.models import MyTournament, Group, Match, GroupClub


class ChoicesDisplayField(serializers.Field):
    def __init__(self, choices, *args, **kwargs):
        self._choices = dict(choices)
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        # Convert the key to the human-readable value using the provided choices
        return self._choices.get(value, "")

    def to_internal_value(self, data):
        # Convert the human-readable value back to the key
        for key, value in self._choices.items():
            if value == data:
                return key
        raise serializers.ValidationError("Invalid value for ChoicesDisplayField.")


class MyTournamentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='mytournament-detail')
    current_stage_display = ChoicesDisplayField(choices=MyTournament.STAGE_CHOICES, source='current_stage',
                                                read_only=True)
    tournament_type_display = ChoicesDisplayField(choices=MyTournament.TOURNAMENT_TYPE_CHOICES,
                                                  source='tournament_type',
                                                  read_only=True)
    teams_selection_display = ChoicesDisplayField(choices=MyTournament.TEAM_SIZE, source='teams_selection',
                                                  read_only=True)

    def to_representation(self, instance):
        # Serialize the instance data
        data = super().to_representation(instance)

        # Determine the value of match_per_day
        match_per_day = data.get('match_per_day')

        # Exclude match_time_2 from the serialized data if match_per_day is 1
        if match_per_day == '1':
            data.pop('match_time_2', None)

        return data

    def create(self, validated_data):
        # Generate the slug from the tournament_name
        # If match_per_day is 1, set match_time_2 to None
        if validated_data['match_per_day'] == '1':
            validated_data['match_time_2'] = None

        slug = slugify(validated_data['tournament_name'])

        # Add the slug to the validated data before creating the instance
        validated_data['slug'] = slug
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.match_per_day == '1':
            validated_data['match_time_2'] = None

        # Generate the slug from the tournament_name
        slug = slugify(validated_data['tournament_name'])

        # Update the slug in the instance before saving
        instance.slug = slug

        return super().update(instance, validated_data)

    champion = ClubSerializer(read_only=True)  # Set read_only=True for the champion field

    class Meta:
        model = MyTournament
        fields = ['url', 'id', 'tournament_name', 'tournament_type', 'match_per_day', 'match_time_1', 'match_time_2',
                  'teams_selection',
                  'teams_selection_display', 'tournament_type_display',
                  'current_stage_display', 'champion']

    def validate(self, data):
        # Check if a tournament with the same slug or name already exists
        slug = data.get('slug')
        tournament_name = data.get('tournament_name')

        if slug and MyTournament.objects.filter(slug=slug).exists():
            raise serializers.ValidationError('A tournament with this slug already exists.')

        if tournament_name and MyTournament.objects.filter(tournament_name=tournament_name).exists():
            raise serializers.ValidationError('A tournament with this name already exists.')

        return data


class ClubSelectionSerializer(serializers.Serializer):
    club_name = serializers.CharField(required=False)
    club_id = serializers.IntegerField(required=False)

    def validate(self, data):
        club_name = data.get('club_name')
        club_id = data.get('club_id')

        if not club_name and not club_id:
            raise serializers.ValidationError("Either 'club_name' or 'club_id' is required.")

        if club_name and club_id:
            raise serializers.ValidationError("You can only provide either 'club_name' or 'club_id', not both.")

        return data


class GroupClub_name(serializers.ModelSerializer):
    class Meta:
        model = GroupClub
        fields = ['club_name']


class GroupClubSerializer(serializers.ModelSerializer):
    # group = GroupSerializer()
    club_name = ClubSerializer()

    class Meta:
        model = GroupClub
        fields = ['id', 'tournament', 'group', 'club_name', 'played', 'wins', 'draw', 'lose', 'gf', 'ga', 'gd',
                  'points']


class GroupSerializer(serializers.ModelSerializer):
    group_club_1 = ClubSerializer()
    group_club_2 = ClubSerializer()
    group_club_3 = ClubSerializer()
    group_club_4 = ClubSerializer()

    class Meta:
        model = Group
        fields = ['id', 'tournament', 'group', 'group_club_1', 'group_club_2', 'group_club_3', 'group_club_4']
        # lookup_field = 'slug'

    def validate(self, data):
        # Get the instance of the group being updated (if available)
        instance = getattr(self, 'instance', None)

        # Check if the group is already used in this tournament, excluding the current group instance
        used_groups = Group.objects.filter(tournament=data['tournament'], group=data['group']).exclude(
            pk=instance.pk if instance else None)
        if used_groups.exists():
            raise serializers.ValidationError(
                {'group': ['{} has already been used in this tournament.'.format(data['group'])]})

        # Check if a team is assigned to multiple group clubs
        group_clubs = [data['group_club_1'], data['group_club_2'], data['group_club_3'], data['group_club_4']]
        assigned_group_clubs = [gc for gc in group_clubs if gc is not None]

        if len(set(assigned_group_clubs)) != len(assigned_group_clubs):
            raise serializers.ValidationError('A team cannot be assigned to multiple group clubs.')

        # Check if teams are already assigned to other groups within this tournament
        existing_groups = Group.objects.filter(tournament=data['tournament']).exclude(
            pk=instance.pk if instance else None)
        for group in existing_groups:
            assigned_clubs = [group.group_club_1, group.group_club_2, group.group_club_3, group.group_club_4]
            if any(gc in assigned_group_clubs for gc in assigned_clubs):
                raise serializers.ValidationError(
                    'One or more teams are already assigned to other groups within this tournament.')

        return data


class Club_name(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['club_name']


class MatchSerializer(serializers.ModelSerializer):
    tournament = MyTournamentSerializer()
    team_1 = GroupClubSerializer()
    team_2 = GroupClubSerializer()

    class Meta:
        model = Match
        fields = ['id', 'tournament', 'group', 'team_1', 'team_2', 'date', 'team_1_score', 'team_2_score',
                  'is_match_ended']
