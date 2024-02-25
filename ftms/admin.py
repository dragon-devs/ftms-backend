from django.contrib import admin

# Register your models here.
from ftms import models


@admin.register(models.Club)
class ClubAdmin(admin.ModelAdmin):
    actions = ['updating_teams_icons']
    list_display = ['id','club_name', 'captain_name', 'phone_number', 'payment', 'created_at']
    search_fields = ('club_name', 'captain_name')

    @admin.action(description='update logos')
    def updating_teams_icons(self, request, queryset):
        for obj in queryset:
            obj.club_image = None  # Set the club_image field to None (remove the picture)
            obj.save()

        updated_count = queryset.count()  # The number of instances in the queryset

        self.message_user(
            request,
            message=f'{updated_count} images have been successfully updated.'
        )