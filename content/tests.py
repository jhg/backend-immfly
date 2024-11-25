from django.test import TestCase
from content.models import Channel, Content

class TestChannel(TestCase):
    def test_channel_rating(self) -> None:
        channel = Channel.objects.create(title='Channel', language='en')
        subchannel_1 = Channel.objects.create(parent=channel, title='Subchannel 1', language='en')
        content = Content.objects.create(channel=subchannel_1, metadata={}, rating=5.00)
        self.assertEqual(channel.rating(), 5.00)

        subchannel_2 = Channel.objects.create(parent=channel, title='Subchannel 2', language='en')
        content = Content.objects.create(channel=subchannel_2, metadata={}, rating=7.00)
        self.assertEqual(channel.rating(), 6.00)

        subchannel_3 = Channel.objects.create(parent=channel, title='Subchannel 3', language='en')
        self.assertEqual(channel.rating(), 6.00)

        subsubchannel = Channel.objects.create(parent=subchannel_3, title='Subsubchannel', language='en')
        self.assertEqual(channel.rating(), 6.00)
        content = Content.objects.create(channel=subsubchannel, metadata={}, rating=6.00)
        self.assertEqual(channel.rating(), 6.00)

        subchannel_1 = Channel.objects.get(pk=subchannel_1.pk)
        subchannel_1.delete()
        self.assertEqual(channel.rating(), 6.50)
