from datetime import datetime

from django.shortcuts import render
from rest_framework.views import APIView

# Create your views here.
from content.models import Recipient, EmotionResult
import pandas as pd


class Dashboard(APIView):
    def get(self, request, number=None):
        context = {}

        if number:
            results = EmotionResult.objects.filter(user_id=number).values()
            user = Recipient.objects.filter(user_id=number).first()
            results_df = pd.DataFrame(results)
            results_df = results_df.drop(['id'], axis=1)
            results_df = results_df.drop(['user_id'], axis=1)
            results_df['date'] = pd.to_datetime(results_df['date']).dt.date
            group = results_df.groupby(['date']).mean()

            columns = ["Fear", "Surprised", "Anger", "Sadness", "Neutrality", "Happiness", "Anxiety", "Embarrassed",
                       "Hurt", "interested", "Boredom"]

            context = {'user_data': group,
                       'user': user }

        return render(request, "content/dashboard.html", context)   # Dashboard 화면


class UserProfile(APIView):
    def get(self, request, number=None):
        context = {}

        if number:
            recipient = Recipient.objects.filter(user_id=number).first
            context = {'recipient': recipient}

        return render(request, "content/user.html", context)     # user 화면


class Table(APIView):
    def get(self, request):
        recipients = Recipient.objects.all()
        context = {'recipients': recipients}

        return render(request, "content/table.html", context)    # table 화면


class Notifications(APIView):
    def get(self, request):

        return render(request, "content/notifications.html")    # notifications 화면


#
# id = request.session.get('id', None)
#
# if id is None:
#     return render(request, "account/login.html")