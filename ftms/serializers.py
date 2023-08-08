from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ftms.models import Club


class ClubSerializer(serializers.ModelSerializer):
    club_image = serializers.ImageField(read_only=True)  # Set read_only to True

    def validate(self, data):
        club_name = data.get('club_name')
        phone_number = data.get('phone_number')

        # Check if club_name or phone_number already exist in the database
        existing_clubs = Club.objects.filter(
            models.Q(club_name=club_name),
            models.Q(phone_number=phone_number)
        )

        if self.instance:  # If it's an update operation, exclude the current instance from the queryset
            existing_clubs = existing_clubs.exclude(pk=self.instance.pk)

        if existing_clubs.exists():
            raise ValidationError("A club with the same name or phone number already exists.")

        return data

    class Meta:
        model = Club
        fields = ['id', 'club_name', 'captain_name', 'phone_number', 'club_image', 'payment']

