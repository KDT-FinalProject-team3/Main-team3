from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
from account.models import Account
from content.models import User, EmotionResult
import pandas as pd

from content.processing import make_dict


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
                user = User.objects.filter(user_id=number).first()
                results_dict = make_dict(number)
                color_list = [(179, 181, 198), (253, 171, 88), (255, 99, 132), (207, 149, 254), (168, 254, 149),
                              (149, 243, 254), (238, 165, 226)]
                count = [i for i in range(len(results_dict))]
                if results_dict:
                    context = {'member': membertype,
                               'user': user,
                               'results': results_dict,
                               'colors': color_list,
                               'count': count}
                    print(context['colors'])
                else:
                    context = {'member': membertype}

                return render(request, "content/dashboard.html", context)  # Dashboard 화면
            
            else:               # 유저번호 없으면 테이블로
                return redirect('/content/table')

        else:       # 보호자 계정
            if number:
                user = User.objects.filter(user_id=number).first()
                results_dict = make_dict(number)
                color_list = ["179,181,198", "253, 171, 88", "255,99,132", "207, 149, 254", "168, 254, 149",
                              "149,243,254", "238, 165, 226"]
                # 빨강, 주황, 파랑, 초록, 하늘, 핑크
                context = {'results': results_dict,
                           'member': membertype,
                           'user': user,
                           'colors': color_list,
                           'count': range(results_dict)}

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

        if number:  # 유저 프로필 보여주기
            users = User.objects.filter(user_id=number).first()
            user_birth = str(users.birth)

            context = {'users': users,
                       'users_birth': user_birth}

            return render(request, "content/user.html", context)

        else:
            context = {}
            return render(request, "content/user.html", context)  # user 화면

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

            return redirect('/content/user/' + str(number))

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

