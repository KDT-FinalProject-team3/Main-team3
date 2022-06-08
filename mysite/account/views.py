from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
# Create your views here.
from account.models import Account
from datetime import datetime

from content.models import User


class Join(APIView):
    def get(self, request):
        return render(request, "account/signup.html") # Join 들어오면 화면으로 여길 보여줘라!!

    def post(self, request):
        # TODO 회원가입
        id = request.data.get('id')
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')
        crypted_password = make_password(password)
        phonenumber = request.data.get('phonenumber')
        user_id = request.data.get('user_id')
        user_name = request.data.get('user_name')

        user = User.objects.filter(user_id=user_id, name=user_name).first()

        if user is None:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))

        Account.objects.create(account=id,
                               password=crypted_password,
                               email=email,
                               name=name,
                               phonenumber=phonenumber,
                               membertype=1,
                               user_id=user_id,
                               user_name=user_name,
                               date_joined=datetime.now())

        return Response(status=200)


class Login(APIView):
    def get(self, request):
        id = request.session.get('id', None)

        if id:      # 로그인 되어있으면 대시보드 or 테이블
            return redirect('/content/dashboard')

        return render(request, "account/login.html/")

    def post(self, request):
        # TODO 로그인
        id = request.data.get('id', None)
        password = request.data.get('password', None)

        user = Account.objects.filter(account=id).first()

        if user is None:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))

        if check_password(password, user.password):
            # TODO 로그인을 했다. 세션 or 쿠키
            request.session['id'] = id
            return Response(status=200)
        else:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))


def logoutUser(request):
    logout(request)
    return redirect('login')
