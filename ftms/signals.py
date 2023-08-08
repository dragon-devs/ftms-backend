import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ftms.models import Club


@receiver(pre_delete, sender=Club)
def delete_club_image(sender, instance, **kwargs):
    # Check if the instance has a club_image associated with it
    if instance.club_image:
        # Get the file path of the club_image
        file_path = instance.club_image.path

        # Delete the file from the storage
        if os.path.exists(file_path):
            os.remove(file_path)