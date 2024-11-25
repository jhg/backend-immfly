from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache
from django.db import models


def channel_picture_path(instance, filename):
    return f"channels/{instance.id}/{filename}"


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

    def __str__(self):
        return self.title

    def clean(self):
        if self.parent and self.parent.contents.exists():
            raise ValidationError("Parent channel cannot have contents and sub-channels")
        if self.parent == self:
            raise ValidationError("Parent channel cannot be itself")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def rating(self):
        # Cache rating reduce time to half while the invalidation
        # ensures that the cache is always up to date.
        cached_rating = cache.get(self._rating_cache_key())
        if cached_rating is not None:
            return cached_rating
        return self._cache_rating()

    def _cache_rating(self):
        rating = self._rating()
        cache.set(self._rating_cache_key(), rating, timeout=None)
        return rating

    def _rating(self):
        if self.contents.exists():
            return Content.objects.filter(
                channel=self
            ).aggregate(models.Avg('rating'))['rating__avg']

        subchannels = Channel.objects.filter(parent=self)
        total = 0
        items = 0
        for subchannel in subchannels:
            if subchannel.rating():
                total += subchannel.rating()
                items += 1

        return (total / items) if items > 0 else None

    def _rating_cache_key(self):
        return f"channel_rating_{self.pk}"

    def invalidate_cache(self):
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

    def __str__(self):
        label = f"content {self.id}"

        if self.metadata.get('title'):
            label += f" - {self.metadata['title']}"

        return label

    def clean(self):
        if self.channel and self.channel.subchannels.exists():
            raise ValidationError("Channel cannot have sub-channels and contents")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


def content_file_path(instance, filename):
    return f"contents/{instance.content.id}/{filename}"


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

    def __str__(self):
        return f"file {self.id} - {self.content}"
