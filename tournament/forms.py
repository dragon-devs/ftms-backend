from django import forms

from ftms.models import Club
from .models import MyTournament


class MyTournamentForm(forms.ModelForm):
    class Meta:
        model = MyTournament
        fields = ['tournament_name', 'teams_selection', 'tournament_type', 'club_name']

    club_name = forms.ModelChoiceField(queryset=Club.objects.all())
