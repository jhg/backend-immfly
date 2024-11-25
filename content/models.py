from __future__ import annotations
from decimal import Decimal
from typing import cast, Any

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache
from django.db import models


def channel_picture_path(instance: Channel, filename: str) -> str:
    return f"channels/{instance.pk}/{filename}"


class Channel(models.Model):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='subchannels',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255)
    language = models.CharField(max_length=5)
    picture = models.ImageField(
        upload_to=channel_picture_path,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if self.parent and self.parent.contents.exists():
            raise ValidationError("Parent channel cannot have contents and sub-channels")
        if self.parent == self:
            raise ValidationError("Parent channel cannot be itself")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def rating(self) -> Decimal | None:
        # Cache rating reduce time to half while the invalidation
        # ensures that the cache is always up to date.
        cached_rating = cast(Decimal | None, cache.get(self._rating_cache_key()))
        if cached_rating is not None:
            return cached_rating
        return self._cache_rating()

    def _cache_rating(self) -> Decimal | None:
        rating = self._rating()
        cache.set(self._rating_cache_key(), rating, timeout=None)
        return rating

    def _rating(self) -> Decimal | None:
        if self.contents.exists():
            return cast(Decimal, self.contents.aggregate(models.Avg('rating'))['rating__avg'])

        subratings = [
            subrating for subrating in (
                subchannel.rating() for subchannel
                in self.subchannels.prefetch_related('contents')
            ) if subrating
        ]

        return Decimal(sum(subratings) / len(subratings)) if subratings else None

    def _rating_cache_key(self) -> str:
        return f"channel_rating_{self.pk}"

    def invalidate_cache(self) -> None:
        cache.delete(self._rating_cache_key())
        if self.parent:
            self.parent.invalidate_cache()


class Content(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='contents'
    )

    metadata = models.JSONField()
    rating = models.DecimalField(max_digits=4, decimal_places=2, validators=[
        MinValueValidator(Decimal(0.00)), MaxValueValidator(Decimal(10.00))
    ])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        label = f"content {self.id}"

        if self.metadata.get('title'):
            label += f" - {self.metadata['title']}"

        return label

    def clean(self) -> None:
        if self.channel and self.channel.subchannels.exists():
            raise ValidationError("Channel cannot have sub-channels and contents")

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        super().save(*args, **kwargs)


def content_file_path(instance: ContentFile, filename: str) -> str:
    return f"contents/{instance.content.pk}/{filename}"


class ContentFile(models.Model):
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(
        upload_to=content_file_path,
        null=False,
        blank=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"file {self.id} - {self.content}"
