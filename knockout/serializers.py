from rest_framework import serializers

from knockout.models import QualifyTeam, RoundOf32, RoundOf16, QuarterFinal, SemiFinal, ThirdPlace, Final


class QualifyTeamSerializer(serializers.ModelSerializer):
    # tournament = MyTournamentSerializer()

    class Meta:
        model = QualifyTeam
        fields = ['id', 'tournament', 'team', 'group_position', 'r32w', 'r16w',
                  'qfw', 'sfw', 'champion', 'tpw']


class RoundOf32Serializer(serializers.ModelSerializer):
    class Meta:
        model = RoundOf32
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended']


class RoundOf16Serializer(serializers.ModelSerializer):
    class Meta:
        model = RoundOf16
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended']


class QuarterFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuarterFinal
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended']


class SemiFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemiFinal
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended']


class ThirdPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPlace
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended']


class FinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Final
        fields = ['id', 'tournament', 'team1', 'team2', 'date', 'team1_score', 'team2_score', 'is_match_ended']


class AllMatchSerializer(serializers.ModelSerializer):
    team1 = QualifyTeamSerializer()
    team2 = QualifyTeamSerializer()

    class Meta:
        model = Final
        fields = '__all__'
