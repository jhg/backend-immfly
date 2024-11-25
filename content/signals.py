from typing import Any

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete, pre_delete, post_save
from content.models import Channel, ContentFile, Content


@receiver(pre_save, sender=Channel)
def channel_pre_save(sender: Any, instance: Channel, **_kwargs: dict[str, Any]) -> None:
    if instance.pk:
        try:
            old_instance = Channel.objects.get(pk=instance.pk)
        except Channel.DoesNotExist:
            return

        old_picture = old_instance.picture
        if old_picture and old_picture != instance.picture:
            old_picture.delete(save=False)


@receiver(post_delete, sender=Channel)
def channel_post_delete(sender: Any, instance: Channel, **_kwargs: dict[str, Any]) -> None:
    if instance.picture:
        instance.picture.delete(save=False)


@receiver(pre_save, sender=ContentFile)
def content_file_pre_save(_sender: Any, instance: ContentFile, **_kwargs: dict[str, Any]) -> None:
    if instance.pk:
        try:
            old_instance = ContentFile.objects.get(pk=instance.pk)
        except ContentFile.DoesNotExist:
            return

        old_file = old_instance.file
        if old_file and old_file != instance.file:
            old_file.delete(save=False)


@receiver(post_delete, sender=ContentFile)
def content_file_post_delete(sender: Any, instance: ContentFile, **_kwargs: dict[str, Any]) -> None:
    if instance.file:
        instance.file.delete(save=False)


@receiver(post_save, sender=Channel)
@receiver(pre_delete, sender=Channel)
def channel_invalidate_cache(sender: Any, instance: Channel, **_kwargs: dict[str, Any]) -> None:
    instance.invalidate_cache()


@receiver(post_save, sender=Content)
@receiver(pre_delete, sender=Content)
def content_invalidate_cache(sender: Any, instance: Content, **_kwargs: dict[str, Any]) -> None:
    instance.channel.invalidate_cache()
