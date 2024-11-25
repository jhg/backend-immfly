import base64
from decimal import Decimal

from django.core.files.base import ContentFile as DjangoContentFile
from rest_framework.reverse import reverse
from rest_framework import serializers
from content.models import Channel, Content, ContentFile


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    channel = serializers.HyperlinkedIdentityField(
        view_name='channel-detail',
        required=False,
        read_only=True
    )
    picture = serializers.ImageField(
        required=False,
        allow_null=True,
        allow_empty_file=True
    )
    rating = serializers.SerializerMethodField(
        required=False,
        read_only=True
    )

    class Meta:
        model = Channel
        fields = [
            'parent',
            'channel',
            'title',
            'language',
            'picture',
            'rating',
            'subchannels',
            'contents',
        ]
        read_only_fields = [
            'id',
            'channel',
            'rating',
            'subchannels',
            'contents',
        ]

    def get_rating(self, instance):
        return instance.rating()

    def to_representation(self, instance):
        """
        Modifica la representación para excluir `parent`, `subchannels` y `contents` si están vacíos.
        """
        representation = super().to_representation(instance)

        if not instance.parent:
            representation.pop('parent', None)

        if not instance.subchannels.exists():
            representation.pop('subchannels', None)

        if not instance.contents.exists():
            representation.pop('contents', None)

        return representation

    def to_internal_value(self, data):
        """
        Procesa la entrada para manejar imágenes en Base64 en el campo `picture`.
        """
        picture_data = data.get('picture', None)

        title_data = data.get('title', None)
        if title_data is None:
            if not self.partial:
                raise serializers.ValidationError("Title is required")
            else:
                title_data = self.instance.title

        if picture_data and isinstance(picture_data, str) and picture_data.startswith('data:image/'):
            img_format, imgstr = picture_data.split(';base64,')
            ext = img_format.split('/')[-1]
            name = f"{title_data}.{ext}"

            data['picture'] = DjangoContentFile(
                base64.b64decode(imgstr),
                name
            )

        return super().to_internal_value(data)


class ContentFileSerializer(serializers.HyperlinkedModelSerializer):
    file = serializers.FileField(
        required=True,
        allow_null=True,
        allow_empty_file=True
    )

    class Meta:
        model = ContentFile
        fields = [
            'file',
        ]


class ContentFileItemSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    download = serializers.FileField(source='file', read_only=True)

    class Meta:
        model = ContentFile
        fields = [
            'file',
            'download',
        ]

    def get_file(self, obj):
        """
        Devuelve la URL relativa de la API para interactuar con este archivo.
        """
        request = self.context.get('request')
        filename = obj.file.name.split('/')[-1]
        return reverse('content-files', kwargs={'pk': obj.content.pk, 'filename': filename}, request=request)


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    channel = serializers.HyperlinkedRelatedField(
        queryset=Channel.objects.all(),
        view_name='channel-detail',
        required=False
    )
    content = serializers.HyperlinkedIdentityField(
        view_name='content-detail',
        required=False,
        read_only=True
    )
    rating = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,
        min_value=Decimal(0.00),
        max_value=Decimal(10.00)
    )
    files = ContentFileItemSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = Content
        fields = [
            'channel',
            'content',
            'metadata',
            'rating',
            'files',
        ]
        read_only_fields = [
            'content',
            'files',
        ]
