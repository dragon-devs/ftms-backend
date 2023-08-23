from django import forms

from ftms.models import Club
from .models import MyTournament


class MyTournamentForm(forms.ModelForm):
    class Meta:
        model = MyTournament
        fields = ['tournament_name', 'tournament_type', 'teams_selection', 'club_name']

    club_name = forms.ModelChoiceField(queryset=Club.objects.all())
