from rest_framework import serializers

from knockout.models import QualifyTeam, RoundOf32, RoundOf16, QuarterFinal, SemiFinal, ThirdPlace, Final
from tournament.serializers import GroupClubSerializer, MyTournamentSerializer


class QualifyTeamSerializer(serializers.ModelSerializer):
    # tournament = MyTournamentSerializer()

    team = GroupClubSerializer()
    class Meta:
        model = QualifyTeam
        fields = ['id', 'tournament', 'team', 'group_position', 'r32w', 'r16w',
                  'qfw', 'sfw', 'champion', 'tpw']


class RoundOf32Serializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = RoundOf32
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended', 'position']


class RoundOf16Serializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = RoundOf16
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended', 'position']


class QuarterFinalSerializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = QuarterFinal
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended', 'position']


class SemiFinalSerializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = SemiFinal
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended', 'position']


class ThirdPlaceSerializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = ThirdPlace
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended', 'position']


class FinalSerializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = Final
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended', 'position']


class AllMatchSerializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()
    tournament = MyTournamentSerializer()

    class Meta:
        model = Final
        fields = '__all__'
