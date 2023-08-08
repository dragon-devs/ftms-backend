import random

from django.contrib import admin

# Register your models here.
from django.contrib.admin import AdminSite

from knockout.models import (
    QualifyTeam,
    RoundOf32,
    RoundOf16,
    QuarterFinal,
    SemiFinal,
    ThirdPlace,
    Final,
)

"""
model_order = {
    "QualifyTeam": 2,
    "RoundOf32": 4,
    "RoundOf16": 6,
    "QuarterFinal": 8,
    "SemiFinal": 10,
    "ThirdPlace": 12,
    "Final": 14,

}


def get_model_order(model):
    return model_order.get(model.__name__, 9999)


class CustomAdminSite(AdminSite):
    def get_model_ordering(self, request):
        return sorted(self._registry.keys(), key=lambda model: model_order.get(model.__name__, 9999))




"""


@admin.register(QualifyTeam)
class QualifyTeamAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'group', 'team', 'position', 'group_position', 'r32w', 'r16w',
                    'qfw', 'sfw', 'tpw', 'champion']
    readonly_fields = ['group_position', 'tournament', 'group', 'team', 'position']
    search_fields = ('tournament__tournament_name',)


@admin.register(RoundOf32)
class RoundOf32Admin(admin.ModelAdmin):
    list_display = ['tournament', 'team1', 'team2', 'team1_score', 'team2_score', 'date', 'position', 'is_match_ended']

    actions = ['auto_matching']

    @admin.action(description='Auto Match')
    def auto_matching(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            obj.team1_score = random.randint(1, 2)
            obj.team2_score = random.randrange(3, 4)
            obj.is_match_ended = True
            obj.save()
            updated_count += 1

        self.message_user(
            request,
            f'{updated_count} matches are successfully done.'
        )


@admin.register(RoundOf16)
class RoundOf16Admin(admin.ModelAdmin):
    list_display = ['tournament', 'team1', 'team2', 'team1_score', 'team2_score', 'date', 'position', 'is_match_ended']

    actions = ['auto_matching']

    @admin.action(description='Auto Match')
    def auto_matching(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            obj.team1_score = random.randint(1, 2)
            obj.team2_score = random.randrange(3, 4)
            obj.is_match_ended = True
            obj.save()
            updated_count += 1

        self.message_user(
            request,
            f'{updated_count} matches are successfully done.'
        )


@admin.register(QuarterFinal)
class QuarterFinalAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'team1', 'team2', 'team1_score', 'team2_score', 'date', 'is_match_ended']

    actions = ['auto_matching']

    @admin.action(description='Auto Match')
    def auto_matching(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            obj.team1_score = random.randint(1, 2)
            obj.team2_score = random.randrange(3, 4)
            obj.is_match_ended = True
            obj.save()
            updated_count += 1

        self.message_user(
            request,
            f'{updated_count} matches are successfully done.'
        )


@admin.register(SemiFinal)
class SemiFinalAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'team1', 'team2', 'team1_score', 'team2_score', 'date', 'is_match_ended']

    actions = ['auto_matching']

    @admin.action(description='Auto Match')
    def auto_matching(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            obj.team1_score = random.randint(1, 2)
            obj.team2_score = random.randrange(3, 4)
            obj.is_match_ended = True
            obj.save()
            updated_count += 1

        self.message_user(
            request,
            f'{updated_count} matches are successfully done.'
        )


@admin.register(ThirdPlace)
class ThirdPlaceAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'team1', 'team2', 'team1_score', 'team2_score', 'date', 'is_match_ended']


@admin.register(Final)
class FinalAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'team1', 'team2', 'team1_score', 'team2_score', 'date', 'is_match_ended']
