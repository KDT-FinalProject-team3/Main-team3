from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
# Create your views here.
from account.models import User
from datetime import datetime


class Join(APIView):
    def get(self, request):
        return render(request, "account/signup.html") # Join 들어오면 화면으로 여길 보여줘라!!

    def post(self, request):
        # TODO 회원가입
        id = request.data.get('id')
        email = request.data.get('email')
        relationship = request.data.get('relationship')
        name = request.data.get('name')
        password = request.data.get('password')
        crypted_password = make_password(password)
        phonenumber = request.data.get('phonenumber')
        gender = request.data.get('gender')
        member_type = request.data.get('member_type')   # 1관리자 2보호자
        recipient_id = request.data.get('recipient_id')

        User.objects.create(id=id,
                            password=crypted_password,
                            relationship=relationship,
                            recipient_id=recipient_id,
                            gender=gender,
                            email=email,
                            username=name,
                            phonenumber=phonenumber,
                            membertype=member_type,
                            date_joined=datetime.now())

        return Response(status=200)


class Login(APIView):
    def get(self, request):
        return render(request, "account/login-2.html/")

    def post(self, request):
        # TODO 로그인
        id = request.data.get('id', None)
        password = request.data.get('password', None)

        user = User.objects.filter(id=id).first()

        if user is None:
            return Response(status=404, data=dict(message="회원정보가 잘못되었습니다."))

        if check_password(password, user.password):
            # TODO 로그인을 했다. 세션 or 쿠키
            request.session['id'] = id
            return Response(status=200)
        else:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))


def logoutUser(request):
    logout(request)
    return redirect('login')
