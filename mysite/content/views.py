from datetime import datetime

from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
from account.models import Account
from content.models import User, EmotionResult
import pandas as pd


class Dashboard(APIView):
    def get(self, request, number=None):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login-2.html')

        membertype = Account.objects.filter(account=id).values('membertype').first()
        membertype = membertype['membertype']

        if not membertype == 0: # 관리자의 경우 유저 매칭 skip
            user_id = Account.objects.filter(account=id).values('user_id').first()

        if membertype == 0:     # 관리자 계정
            if number:          # 유저번호 있을때
                results = EmotionResult.objects.filter(user_id=number).values()
                user = User.objects.filter(user_id=number).first()

                columns = ["Fear", "Surprised", "Anger", "Sadness", "Neutrality", "Happiness", "Anxiety", "Embarrassed",
                           "Hurt", "interested", "Boredom"]
                if results:
                    context = {'member': membertype,
                               'user': user,
                               'results': results}
                else:
                    context = {'member': membertype}

                return render(request, "content/dashboard.html", context)  # Dashboard 화면
            else:               # 유저번호 없으면 테이블로
                return redirect('/content/table')

        else:       # 보호자 계정
            if number:
                results = EmotionResult.objects.filter(user_id=number).values()
                user = User.objects.filter(user_id=number).first()
                results_df = pd.DataFrame(results)
                results_df = results_df.drop(['id'], axis=1)
                results_df = results_df.drop(['user_id'], axis=1)
                results_df['date'] = pd.to_datetime(results_df['date']).dt.date
                group = results_df.groupby(['date']).mean()

                columns = ["Fear", "Surprised", "Anger", "Sadness", "Neutrality", "Happiness", "Anxiety",
                           "Embarrassed",
                           "Hurt", "interested", "Boredom"]

                context = {'user_data': group,
                           'member': membertype,
                           'user': user}

                return render(request, "content/dashboard.html", context)  # Dashboard 화면

        return redirect('/content/dashboard/' + str(user_id['user_id']))


class UserProfile(APIView):
    def get(self, request, number=None):
        id = request.session.get('id', None)

        if id is None:  # 로그인 확인
            return render(request, 'account/login-2.html')

        membertype = Account.objects.filter(account=id).values('membertype').first()
        membertype = membertype['membertype']

        if not membertype == 0:
            return redirect('/account/logout')

        context = {}

        if number:  # 유저 프로필 보여주기
            user = User.objects.filter(user_id=number).first()
            user_birth = str(user.birth)

            context = {'user': user,
                       'user_birth': user_birth}

        return render(request, "content/user.html", context)     # user 화면

    def post(self, request, number=None):    # 새로운 유저 생성
        name = request.data.get('name')
        contact = request.data.get('contact')
        gender = request.data.get('gender')
        email = request.data.get('email')
        address = request.data.get('address')
        birth = request.data.get('birth')
        specifics = request.data.get('specifics')

        if number:      # 유저 수정하기
            user = User.objects.filter(user_id=number).first()

            user.name = name
            user.contact = contact
            user.gender = gender
            user.email = email
            user.address = address
            user.birth = birth
            user.specifics = specifics
            user.save()

            return redirect('/content/user/' + number)

        else:            # 유저 추가하기
            User.objects.create(name=name,
                                contact=contact,
                                gender=gender,
                                email=email,
                                address=address,
                                birth=birth,
                                status='평온',
                                specifics=specifics,
                                create_time=datetime.now())

            return redirect('/content/table')


class Table(APIView):
    def get(self, request):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login-2.html')
        recipients = User.objects.all()
        context = {'recipients': recipients}

        return render(request, "content/table.html", context)    # table 화면


class Notifications(APIView):
    def get(self, request):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login-2.html')

        return render(request, "content/notifications.html")    # notifications 화면

