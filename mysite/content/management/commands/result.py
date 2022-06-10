
from django.core.management.base import BaseCommand
from content.processing import predict


class Command(BaseCommand):
    help = 'test'

    def handle(self, *args, **options):
        print("감정분류를 실행합니다.")
        predict()