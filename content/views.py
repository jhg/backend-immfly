from urllib.request import Request

from django.core.serializers import serialize
from django.http import HttpRequest
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from content.serializers import ChannelSerializer, ContentSerializer, ContentFileSerializer
from content.models import Channel, Content, ContentFile


class ChannelList(generics.ListAPIView[Channel]):
    """
    List root channels or create a new one.
    """
    serializer_class = ChannelSerializer
    queryset = Channel.objects.filter(parent=None)

    def get_serializer_context(self) -> dict[str, None | HttpRequest | generics.GenericAPIView[Channel]]:
        """
        Sobrescribe el contexto para excluir el request.
        """
        context = super().get_serializer_context()
        context['request'] = None
        return context

    def post(self, request: Request) -> Response:
        serializer = ChannelSerializer(data=request.data, context={'request': None})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChannelDetails(generics.GenericAPIView[Channel]):
    """
    Retrieve, update or delete a channel instance.
    """
    serializer_class = ChannelSerializer

    def get(self, request: Request, pk: int) -> Response:
        channel = generics.get_object_or_404(Channel, pk=pk)
        serializer = ChannelSerializer(channel, context={'request': None})
        data = serializer.data
        data.pop('channel', None)
        return Response(data)

    def post(self, request: Request, pk: int) -> Response:
        parent_channel = generics.get_object_or_404(Channel, pk=pk)
        serializer = ChannelSerializer(data=request.data, context={'request': None})
        if serializer.is_valid():
            serializer.save(parent=parent_channel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request, pk: int) -> Response:
        channel = generics.get_object_or_404(Channel, pk=pk)
        serializer = ChannelSerializer(channel, data=request.data, context={'request': None})
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data.pop('channel', None)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request: Request, pk: int) -> Response:
        channel = generics.get_object_or_404(Channel, pk=pk)
        serializer = ChannelSerializer(channel, data=request.data, partial=True, context={'request': None})
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data.pop('channel', None)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int) -> Response:
        channel = generics.get_object_or_404(Channel, pk=pk)
        channel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContentCreation(APIView):
    """
    Create a new content instance.
    """

    def post(self, request: Request, pk: int) -> Response:
        channel = generics.get_object_or_404(Channel, pk=pk)
        serializer = ContentSerializer(data=request.data, context={'request': None})
        if serializer.is_valid():
            serializer.save(channel=channel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentDetails(generics.GenericAPIView[Content]):
    """
    Retrieve, update or delete a content instance.
    """
    serializer_class = ContentSerializer

    def get(self, request: Request, pk: int) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        serializer = ContentSerializer(content, context={'request': None})
        data = serializer.data
        data.pop('content', None)
        return Response(data)

    def put(self, request: Request, pk: int) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        serializer = ContentSerializer(content, data=request.data, context={'request': None})
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data.pop('content', None)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request: Request, pk: int) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        serializer = ContentSerializer(content, data=request.data, partial=True, context={'request': None})
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data.pop('content', None)
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        content.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContentFileUpload(generics.GenericAPIView[ContentFile]):
    """
    Upload a file to a content instance.
    """
    parser_classes = [FileUploadParser, FormParser, MultiPartParser]
    serializer_class = ContentFileSerializer

    def get(self, request: Request, pk: int, filename: str) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        file = content.files.filter(file__contains=filename).first()
        if not file:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ContentFileSerializer(file, context={'request': None})
        return Response(serializer.data)

    def put(self, request: Request, pk: int, filename: str) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        content_file = content.files.filter(file__contains=filename).first()
        if content_file:
            content_file.file.delete(save=False)

        serializer = ContentFileSerializer(content_file, data=request.data, context={'request': None})
        if serializer.is_valid():
            serializer.save(content=content)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK if content_file else status.HTTP_201_CREATED
            )
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk: int, filename: str) -> Response:
        content = generics.get_object_or_404(Content, pk=pk)
        file = content.files.get(file__contains=filename)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
