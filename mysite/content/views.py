from datetime import datetime

import pandas as pd
from django.shortcuts import render, redirect
from rest_framework.views import APIView

# Create your views here.
from account.models import Account
from content.models import User, S3Image, ComfortBot, ChatHistory, EmotionResult
from django.core.paginator import Paginator
from content.processing import make_dict, StatusJudgment
import operator
from operator import itemgetter, attrgetter


class Dashboard(APIView):
    def get(self, request, number=None, emotion=None):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login.html')

        membertype = Account.objects.filter(account=id).values('membertype').first()
        membertype = membertype['membertype']

        if not membertype == 0:  # 관리자의 경우 유저 매칭 skip
            user_id = Account.objects.filter(account=id).values('user_id').first()

        if membertype == 0:  # 관리자 계정
            if number:  # 유저번호 있을때
                user = User.objects.filter(user_id=number).first()
                results_dict = make_dict(number)

                if results_dict:
                    context = {'member': membertype,
                               'users': user,
                               'results': results_dict}
                else:
                    context = {'member': membertype}

                return render(request, "content/dashboard.html", context)  # Dashboard 화면

            else:  # 유저번호 없으면 테이블로
                return redirect('/content/table')

        else:  # 보호자 계정
            if number:
                user = User.objects.filter(user_id=number).first()
                results_dict = make_dict(number)
                color_list = ["179,181,198", "253, 171, 88", "255,99,132", "207, 149, 254", "168, 254, 149",
                              "149,243,254", "238, 165, 226"]
                # 빨강, 주황, 파랑, 초록, 하늘, 핑크
                context = {'results': results_dict,
                           'member': membertype,
                           'users': user,
                           'colors': color_list,
                           'count': range(results_dict)}

                return render(request, "content/dashboard.html", context)  # Dashboard 화면

        return redirect('/content/dashboard/' + str(user_id['user_id']))

    def post(self, request, number=None):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login.html')

        membertype = Account.objects.filter(account=id).values('membertype').first()
        membertype = membertype['membertype']
        user = User.objects.filter(user_id=number).first()

        # radar 차트 (startdate, enddate)
        sdate = request.data.get('sdate')
        edate = request.data.get('edate')

        if sdate:
            datetime_format = "%Y-%m-%d"
            sdate = datetime.strptime(sdate, datetime_format).date()
            edate = datetime.strptime(edate, datetime_format).date()

            radar_dict = make_dict(number, sdate, edate)
            context = {
                'results': radar_dict,
                'users': user,
                'member': membertype,
            }

            return render(request, "content/dashboard.html", context=context)


        else:
            # line 차트 (emotion, date)
            emotion = request.data.get('emotions')
            date = request.data.get('line_date')
            emotion_r = EmotionResult.objects.filter(user_id=number, date__contains=date).values(emotion, 'date')
            emotion_df = pd.DataFrame(emotion_r)

            emotion_df['date_str'] = emotion_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
            emotion_df = emotion_df.drop(['date'], axis=1)

            emotion_df['date'] = emotion_df['date_str'].str[5:10]
            emotion_df['time'] = emotion_df['date_str'].str[11:13]
            emotion_df['emotion'] = emotion_df[emotion]

            emotion_df = emotion_df.drop(['date_str'], axis=1)
            emotion_df = emotion_df.drop([emotion], axis=1)

            # 시간을 기준으로 수치값 groupby

            final_df = emotion_df.sort_values(by=['time'])

            final_df = final_df.groupby('time').agg({'emotion': 'mean'}).reset_index()
            final_df['date'] = date

            line_dict = final_df.to_dict('records')

            context = {
                'line_data': line_dict,
                'label': emotion,
                'users': user,
                'member': membertype,
            }

            return render(request, "content/line.html", context=context)


class UserProfile(APIView):
    def get(self, request, number=None):
        id = request.session.get('id', None)

        if id is None:  # 로그인 확인
            return render(request, 'account/login.html')

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

    def post(self, request, number=None):  # 새로운 유저 생성
        name = request.data.get('name')
        contact = request.data.get('contact')
        gender = request.data.get('gender')
        email = request.data.get('email')
        address = request.data.get('address')
        birth = request.data.get('birth')
        specifics = request.data.get('specifics')

        if number:  # 유저 수정하기
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

        else:  # 유저 추가하기
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
    def get(self, request, number=None):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login.html')

        users = User.objects.all()
        page = request.GET.get('page', '1') # 페이지
        paginator = Paginator(users, 10)  # 페이지당 12개
        page_obj = paginator.get_page(page)

        judgements = StatusJudgment()
        if number is None:
            number = 1
        total_score, score_data, count_dict = judgements.make_dataframe(number)

        sorted_count = sorted(
            count_dict.items(),
            key=operator.itemgetter(1),
            reverse=True  # 내림차순: 빈도수 높은 것부터 정렬
        )

        count_list = []

        for count in sorted_count:
            count_list.append(count)

        count_list = count_list[:10]

        for i, count in enumerate(count_list):
            count_list[i] = list(count)

        for label in count_list:
            print(label[0], label[1])

        context = {'users': page_obj,
                   'scores': score_data,
                   'counts': count_list}

        return render(request, "content/table.html", context)  # table 화면


class ImageList(APIView):
    def get(self, request):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login.html')

        images = S3Image.objects.all().values('image')

        context = {'images': images}

        return render(request, "content/image.html", context=context)  # image_list 화면


class Notifications(APIView):
    def get(self, request):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login.html')

        return render(request, "content/notifications.html")  # notifications 화면


class Messages(APIView):
    def get(self, request):
        id = request.session.get('id', None)

        if id is None:
            return render(request, 'account/login.html')

        messages = ComfortBot.objects.all().order_by('id')
        history = ChatHistory.objects.all().order_by('-id')[:5]
        history = reversed(history)

        context = {'messages': messages,
                   'histories': history}

        return render(request, "content/messages.html", context)  # messages 화면
