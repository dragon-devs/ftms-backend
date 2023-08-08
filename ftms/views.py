from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ftms.models import Club
from ftms.serializers import ClubSerializer
from tournament.serializers import MyTournamentSerializer


class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    @action(detail=True, methods=['GET'])
    def joined_tournaments(self, request, pk=None):
        try:
            club = self.get_object()
            join_tournaments = club.joined_tournaments()
            serializer = MyTournamentSerializer(join_tournaments, many=True)
            return Response(serializer.data)
        except Club.DoesNotExist:
            return Response({'error': 'Club not found'}, status=404)

    @action(detail=True, methods=['GET'])
    def qualified_tournaments(self, request, pk=None):
        try:
            club = self.get_object()
            qualified_tournaments = club.qualified_tournaments()
            serializer = MyTournamentSerializer(qualified_tournaments, many=True)
            return Response(serializer.data)
        except Club.DoesNotExist:
            return Response({'error': 'Club not found'}, status=404)
