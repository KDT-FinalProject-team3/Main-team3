
from django.core.management.base import BaseCommand
from content.processing import StatusJudgment


class Command(BaseCommand):
    help = 'test'

    def handle(self, *args, **options):
        print("1번 유저의 감정 위험도를 측정합니다.")
        sentence = StatusJudgment()
        sentence.total_score(1)

