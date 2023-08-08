from itertools import chain

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from knockout.models import QualifyTeam, RoundOf32, RoundOf16, QuarterFinal, SemiFinal, ThirdPlace, Final
from knockout.serializers import QualifyTeamSerializer, RoundOf32Serializer, RoundOf16Serializer, \
    QuarterFinalSerializer, SemiFinalSerializer, ThirdPlaceSerializer, FinalSerializer, AllMatchSerializer
from tournament.serializers import MatchSerializer


class QualifyTeamViewSet(viewsets.ModelViewSet):
    queryset = QualifyTeam.objects.all()
    serializer_class = QualifyTeamSerializer

    def get_queryset(self):
        queryset = super(QualifyTeamViewSet, self).get_queryset()
        tournament_id = self.kwargs.get('tournament_pk')  # Use get method to avoid KeyError
        if tournament_id:
            queryset = queryset.filter(tournament__id=tournament_id)
        return queryset

    @action(detail=False, methods=['GET'])
    def tournament_qualifyteams(self, request):
        tournament_pk = request.query_params.get('tournament_pk')
        if tournament_pk is not None:
            queryset = self.get_queryset().filter(tournament_id=tournament_pk)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "Missing 'tournament_pk' parameter."}, status=400)


class RoundOf32ViewSet(viewsets.ModelViewSet):
    serializer_class = RoundOf32Serializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None:
            return RoundOf32.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = RoundOf32.objects.filter(tournament__id=tournament_id)
        return queryset


class RoundOf16ViewSet(viewsets.ModelViewSet):
    serializer_class = RoundOf16Serializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None:
            return RoundOf16.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = RoundOf16.objects.filter(tournament__id=tournament_id)
        return queryset


class QuarterFinalViewSet(viewsets.ModelViewSet):
    serializer_class = QuarterFinalSerializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None:
            return QuarterFinal.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = QuarterFinal.objects.filter(tournament__id=tournament_id)
        return queryset


class SemiFinalViewSet(viewsets.ModelViewSet):
    serializer_class = SemiFinalSerializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None:
            return SemiFinal.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = SemiFinal.objects.filter(tournament__id=tournament_id)
        return queryset


class ThirdPlaceViewSet(viewsets.ModelViewSet):
    serializer_class = ThirdPlaceSerializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None:
            return ThirdPlace.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = ThirdPlace.objects.filter(tournament__id=tournament_id)
        return queryset


class FinalViewSet(viewsets.ModelViewSet):
    serializer_class = FinalSerializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None:
            return Final.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = Final.objects.filter(tournament__id=tournament_id)
        return queryset


class AllMatchesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AllMatchSerializer

    def get_queryset(self):
        tournament_id = self.kwargs.get('tournament_pk')
        print("Tournament ID:", tournament_id)
        round32_qs = RoundOf32.objects.filter(tournament__id=tournament_id)
        round16_qs = RoundOf16.objects.filter(tournament__id=tournament_id)
        quarterfinals_qs = QuarterFinal.objects.filter(tournament__id=tournament_id)
        third_place_qs = ThirdPlace.objects.filter(tournament__id=tournament_id)
        semifinals_qs = SemiFinal.objects.filter(tournament__id=tournament_id)
        finals_qs = Final.objects.filter(tournament__id=tournament_id)

        queryset = list(chain(round32_qs, round16_qs, quarterfinals_qs, semifinals_qs, third_place_qs, finals_qs))
        print("Combined queryset count:", len(queryset))
        return queryset
