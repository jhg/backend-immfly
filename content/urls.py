from django.urls import path
from content.views import ChannelList, ChannelDetails, ContentCreation, ContentDetails, ContentFile


urlpatterns = [
    path('', ChannelList.as_view(), name='channel-list'),
    path('channels/<int:pk>/', ChannelDetails.as_view(), name='channel-detail'),

    path('channels/<int:pk>/content/', ContentCreation.as_view(), name='content-creation'),
    path('contents/<int:pk>/', ContentDetails.as_view(), name='content-detail'),
    path('contents/<int:pk>/<str:filename>/', ContentFile.as_view(), name='content-files'),
]
