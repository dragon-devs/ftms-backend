from django.shortcuts import render, redirect

# Create your views here.
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ftms.models import Club
from .forms import MyTournamentForm
from .models import GroupClub, Group, ClubHistory, MyTournament, Match

from rest_framework.viewsets import ModelViewSet

# RESTApi View.
from .serializers import MyTournamentSerializer, GroupSerializer, ClubSelectionSerializer, MatchSerializer, \
    GroupClubSerializer


class MyTournamentViewSet(viewsets.ModelViewSet):
    queryset = MyTournament.objects.all()
    serializer_class = MyTournamentSerializer

    # lookup_field = 'slug'  # Use the 'slug' field as the lookup field for the URL
    # lookup_url_kwarg = 'slug'  # Name of the URL keyword argument to capture the slug

    def create(self, request, *args, **kwargs):
        tournament_serializer = self.get_serializer(data=request.data)
        tournament_serializer.is_valid(raise_exception=True)

        clubs_serializer = ClubSelectionSerializer(data=request.data.get('clubs'), many=True)
        clubs_serializer.is_valid(raise_exception=True)

        tournament = tournament_serializer.save()

        # Get the selected clubs data
        selected_clubs_data = clubs_serializer.validated_data

        # Get the number of teams selected
        teams_selection = int(tournament_serializer.data.get('teams_selection'))

        # Calculate the number of groups needed
        num_groups = (teams_selection + 3) // 4  # Round up to the nearest multiple of 4

        # Get the available groups
        available_groups = Group.GROUPS[:num_groups]

        # Create groups and assign clubs to each group
        for group in available_groups:
            group_instance = Group.objects.create(tournament=tournament, group=group[0])
            for j in range(4):
                if len(selected_clubs_data) > 0:
                    club_data = selected_clubs_data.pop(0)
                    club_name = club_data.get('club_name')
                    club_id = club_data.get('club_id')

                    if club_id:
                        club = Club.objects.get(pk=club_id)
                    else:
                        club = Club.objects.get(club_name=club_name)

                    setattr(group_instance, f'group_club_{j + 1}', club)

            group_instance.save()

        headers = self.get_success_headers(tournament_serializer.data)
        return Response(tournament_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupViewSet(ModelViewSet):
    serializer_class = GroupSerializer

    def get_queryset(self):
        tournament_id = self.kwargs['tournament_pk']
        return Group.objects.filter(tournament__id=tournament_id)


class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer

    def get_queryset(self):
        # Get the tournament and group IDs from the URL parameters
        tournament_id = self.kwargs.get('tournament_pk')
        group_id = self.kwargs.get('group_pk')

        # Check if tournament_id and group_id are provided in the URL parameters
        if tournament_id is None or group_id is None:
            return Match.objects.all()  # Return an empty queryset if IDs are not provided

        # Filter the matches based on the tournament and group IDs
        queryset = Match.objects.filter(tournament__id=tournament_id, group__id=group_id)
        return queryset

    @action(detail=False, methods=['GET'])
    def tournament_group_matches(self, request):
        tournament_pk = request.query_params.get('tournament_pk')
        if tournament_pk is not None:
            queryset = self.get_queryset().filter(tournament_id=tournament_pk)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "Missing 'tournament_pk' parameter."}, status=400)

class GroupClubViewSet(viewsets.ModelViewSet):
    serializer_class = GroupClubSerializer
    queryset = GroupClub.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        tournament_pk = self.kwargs.get('tournament_pk')
        group_id = self.kwargs.get('group_pk')

        if tournament_pk:
            if group_id:
                queryset = queryset.filter(group__tournament_id=tournament_pk, group_id=group_id)
            else:
                queryset = queryset.filter(group__tournament_id=tournament_pk)

        return queryset

    @action(detail=False, methods=['GET'])
    def tournament_groups(self, request):
        tournament_pk = request.query_params.get('tournament_pk')
        if tournament_pk is not None:
            queryset = self.get_queryset().filter(tournament_id=tournament_pk)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"detail": "Missing 'tournament_pk' parameter."}, status=400)
    """
        def perform_create(self, serializer):
        # Get the tournament ID from the URL
        tournament_id = self.kwargs.get('tournament_pk')

        # Get the group ID from the request data
        group_id = self.request.data.get('group')

        # Get the team IDs from the request data
        team_1_id = self.request.data.get('team_1')
        team_2_id = self.request.data.get('team_2')

        # Retrieve the tournament, group, team_1, and team_2 instances
        try:
            tournament = MyTournament.objects.get(id=tournament_id)
            group = Group.objects.get(tournament=tournament, id=group_id)
            team_1 = GroupClub.objects.get(group=group, id=team_1_id)
            team_2 = GroupClub.objects.get(group=group, id=team_2_id)
        except (MyTournament.DoesNotExist, Group.DoesNotExist, GroupClub.DoesNotExist) as e:
            return Response({'error': str(e)}, status=400)

        # Add the tournament, group, team_1, and team_2 instances to the serializer data
        serializer.save(tournament=tournament, group=group, team_1=team_1, team_2=team_2)
    """


"""
# Create your views here.

def index(request):
    groups = Group.objects.all()
    groups_club = GroupClub.objects.all()
    history = ClubHistory.objects.filter(club_id=52)

    context = {'groups': groups, 'groups_club': groups_club, 'history': history}
    return render(request, 'tournament/index.html', context=context)


def create_my_tournament(request):
    if request.method == 'POST':
        form = MyTournamentForm(request.POST)
        if form.is_valid():
            my_tournament = form.save(commit=False)
            my_tournament.club_name = form.cleaned_data['club_name']
            my_tournament.save()
            return redirect('tournament-list')
    else:
        form = MyTournamentForm()

    context = {'form': form}
    return render(request, 'tournament/create_my_tournament.html', context)


"""
