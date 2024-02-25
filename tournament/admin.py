import random
from time import sleep

from django.contrib import admin

# Register your models here.
from tournament import models
from tournament.models import Group


@admin.register(models.MyTournament)
class MyTournamentAdmin(admin.ModelAdmin):
    list_display = ['tournament_name', 'teams_selection', 'tournament_type', 'current_stage']
    prepopulated_fields = {
        'slug': ['tournament_name']
    }


@admin.register(models.GroupClub)
class GroupClubAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'group', 'club_name', 'played', 'wins', 'draw', 'lose', 'gf', 'ga', 'gd', 'points']
    search_fields = ('club_name__club_name', 'tournament__tournament_name')


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'group', 'tournament', 'group_club_1', 'group_club_2', 'group_club_3', 'group_club_4']
    search_fields = ('tournament__tournament_name',)




@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'group', 'team_1', 'team_2', 'date', 'team_1_score', 'team_2_score',
                    'is_match_ended', 'match_number']
    readonly_fields = ('group', 'tournament', 'team_1', 'team_2')
    search_fields = ('tournament__tournament_name',)
    actions = ['auto_matching']

    @admin.action(description='Auto Match')
    def auto_matching(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            obj.team_1_score = random.randint(1, 4)
            obj.team_2_score = random.randrange(1, 4)
            obj.is_match_ended = True
            obj.save()
            updated_count += 1


        self.message_user(
            request,
            f'{updated_count} matches are successfully done.'
        )