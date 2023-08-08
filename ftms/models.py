from io import BytesIO
import random

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.core.files.images import ImageFile
from PIL import Image, ImageDraw, ImageFont
import os

from django.db.models import Q

from knockout.models import QualifyTeam

User = get_user_model()



def create_club_image(instance):
    club_name = instance.club_name
    #first_three_words = " ".join(club_name.split()[:3]).upper()
    first_three_words = club_name[:3].upper()


    # Load the background image
    label_assets = ["club_images/Asset 1.png",
                    "club_images/Asset 2.png",
                    "club_images/Asset 3.png",
                    "club_images/Asset 4.png",
                    "club_images/Asset 5.png",
                    "club_images/Asset 6.png",
                    "club_images/Asset 7.png",
                    "club_images/Asset 8.png",
                    "club_images/Asset 9.png"]

    background_image_path = random.choice(label_assets)  # Replace with the path to your background image
    background_image = Image.open(background_image_path).convert("RGBA")

    # Create a new transparent image with the same size as the background image
    image = Image.new("RGBA", background_image.size, (0, 0, 0, 0))

    # Create a draw object to write the text on the image
    draw = ImageDraw.Draw(image)

    font_path = "club_images/fonts/Poppins-ExtraBold.ttf"
    # Choose a font and size
    font = ImageFont.truetype(font_path, 60)

    # Calculate the position to center the text
    text_width, text_height = draw.textsize(first_three_words, font=font)
    position = ((image.width - text_width) / 2, (image.height - text_height) / 2 - 6)

    # Draw the text (first three words) on the image with white color and alpha = 255 (fully opaque)
    draw.text(position, first_three_words, font=font, fill=(255, 255, 255, 255))

    # Paste the text image onto the background image with a mask
    final_image = Image.alpha_composite(background_image, image)

    # Convert the image to bytes
    image_bytes = BytesIO()
    final_image.save(image_bytes, format='PNG')
    image_bytes.seek(0)  # Reset the buffer position to the beginning

    return image_bytes.getvalue()


class Club(models.Model):
    club_name = models.CharField(max_length=255)
    captain_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    payment = models.BooleanField()
    club_image = models.ImageField(upload_to='club_images', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
    def clean(self):
        # Check if club_name, captain_name, or phone_number already exist in the database
        existing_clubs = Club.objects.filter(
            models.Q(club_name=self.club_name)
            | models.Q(phone_number=self.phone_number)
        )

        if self.pk:  # If it's an update operation, exclude the current instance from the queryset
            existing_clubs = existing_clubs.exclude(pk=self.pk)

        if existing_clubs.exists():
            raise ValidationError("A club with the same name, captain name, or phone number already exists.")

    def save(self, *args, **kwargs):
        if not self.club_image:  # Only create the image if it doesn't already exist
            image_data = create_club_image(self)
            self.club_image.save(f"{self.club_name}.png", ContentFile(image_data), save=False)
        super(Club, self).save(*args, **kwargs)


    def __str__(self):
        return self.club_name


    def joined_tournaments(self):
        # Get the primary key of the current club instance
        Tournament = apps.get_model('tournament', 'MyTournament')
        GroupClub = apps.get_model('tournament', 'GroupClub')

        club_id = self.pk
        # Query GroupClub to find all instances related to the current club
        group_clubs = GroupClub.objects.filter(club_name_id=club_id)
        # Get the tournaments associated with the found GroupClub instances
        tournaments = Tournament.objects.filter(group__groupclub__in=group_clubs).distinct()
        return tournaments

    def qualified_tournaments(self):
        # Get the primary key of the current club instance
        Tournament = apps.get_model('tournament', 'MyTournament')

        club_id = self.pk
        # Query QualifyTeam to find all instances related to the current club
        qualify_teams = QualifyTeam.objects.filter(team__club_name_id=club_id)
        # Get the tournaments associated with the found QualifyTeam instances
        tournaments = Tournament.objects.filter(Q(roundof16__in=qualify_teams) |
                                                  Q(quarterfinal__in=qualify_teams) |
                                                  Q(semifinal__in=qualify_teams) |
                                                  Q(final__in=qualify_teams)).distinct()
        return tournaments
