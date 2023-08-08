from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from ftms.views import ClubViewSet
from knockout.views import QualifyTeamViewSet, RoundOf32ViewSet, RoundOf16ViewSet, QuarterFinalViewSet, \
    SemiFinalViewSet, ThirdPlaceViewSet, FinalViewSet, AllMatchesViewSet
from .views import MyTournamentViewSet, GroupViewSet, MatchViewSet, GroupClubViewSet


router = DefaultRouter()
router.register(r'tournaments', MyTournamentViewSet, basename='mytournament')
router.register(r'clubs', ClubViewSet, basename='clubs')
router.register(r'matches', MatchViewSet, basename='matchs')
router.register(r'groupclubs', GroupClubViewSet, basename='groupclub')
router.register(r'qualifyteams', QualifyTeamViewSet, basename='qualifyteam')

# Nested router for groups
tournament_router = NestedDefaultRouter(router, r'tournaments', lookup='tournament')
tournament_router.register(r'groups', GroupViewSet, basename='tournament-groups')
tournament_router.register(r'groupclubs', GroupClubViewSet, basename='tournament-groupclubs')
tournament_router.register(r'roundof32', RoundOf32ViewSet, basename='tournament-roundof32')
tournament_router.register(r'roundof16', RoundOf16ViewSet, basename='tournament-roundof16')
tournament_router.register(r'quarterfinals', QuarterFinalViewSet, basename='tournament-quarterfinals')
tournament_router.register(r'semifinals', SemiFinalViewSet, basename='tournament-semifinals')
tournament_router.register(r'thirdplace', ThirdPlaceViewSet, basename='tournament-thirdplace')
tournament_router.register(r'final', FinalViewSet, basename='tournament-final')
tournament_router.register(r'all', AllMatchesViewSet, basename='tournament-all')
tournament_router.register(r'qualifyteams', QualifyTeamViewSet, basename='tournament-qualifyteams')


# Create a router for the matches nested under groups and tournaments
matches_router = NestedDefaultRouter(tournament_router, r'groups', lookup='group')
matches_router.register(r'matches', MatchViewSet, basename='group-matches')
matches_router.register(r'groupclubs', GroupClubViewSet, basename='group-clubs-table')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tournament_router.urls)),
    path('', include(matches_router.urls)),
]

# For the nested actions
urlpatterns += [
    path('', include((router.urls, 'qualifyteams'))),
]

# For the custom method
urlpatterns += [
    path('', include((router.urls, 'qualifyteam'))),
    path('', include((tournament_router.urls, 'qualifyteams-tournament'))),
]
