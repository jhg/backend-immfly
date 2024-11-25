from django.core.management.base import BaseCommand
from content.models import Channel
import time
import csv


class Command(BaseCommand):
    help = 'Export channels and their ratings to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'output_file',
            nargs='?',
            default='channels_ratings.csv',
            help='The output CSV file (default: channels_ratings.csv)'
        )

    def handle(self, *args, **kwargs):
        start_time = time.time()

        output_file = kwargs['output_file']
        with open(output_file, 'w', buffering=32768, newline='') as csvfile:
            fieldnames = ['Channel Title', 'Rating']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            channels = sorted(
                (
                    (channel.title, channel.rating())
                    for channel
                    in Channel.objects.prefetch_related(
                        'contents', 'subchannels'
                    ).only('title')
                ),
                key=lambda v: v[1] or 0,
                reverse=True
            )

            for (title, rating) in channels:
                writer.writerow({
                    'Channel Title': title,
                    'Rating': rating
                })

        elapsed_time = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(f'Successfully exported channels and ratings to {output_file} in {elapsed_time:.3f}s'))
