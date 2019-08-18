# users 视图



from django.contrib.auth import login
from django.contrib.messages.storage import session
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from utils.response_code import RETCODE
import re

from apps.users.models import User
from meiduo_mall.settings.dev import logger




# 判断手机号是否重复
class PhoneCountView(View):

    def get(self,request,mobile):

        phonecount = User.objects.filter(mobile = mobile).count()

        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','count':phonecount})


# 判断用户名是否重复
class UserCountView(View):

    def get(self,request,username):

        usercount = User.objects.filter(username=username).count()

        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK','count':usercount})


# 注册功能
class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """
        提供注册界面
        :param request: 请求对象
        :return: 注册界面
        """
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册
        :param request:请求对象
        :return:注册结果
        """
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        allow = request.POST.get('allow')



        # 校验参数
        if not all([username, password, password2, phone, allow]):

            return http.HttpResponseForbidden("缺少参数，请把信息输入完整！")

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):

            return http.HttpResponseForbidden("请输入5-20位的用户名！")

        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):

            return http.HttpResponseForbidden("请输入8-20位的密码!")

        if password != password2:

            return http.HttpResponseForbidden("请输入相同的密码！")

        if not re.match(r'^1[345789]\d{9}$',phone):

            return http.HttpResponseForbidden("请输入正确的手机号！")



        if allow != "on":

            return http.HttpResponseForbidden("请勾选协议！")

        try:
            user = User.objects.create_user(username=username,password=password,mobile=phone)

        except Exception as e:
            logger.error(e)

            return render(request,'register.html',{'register_error': '注册失败'})

        # 保持会话登录状态
        login(request, user)





        # 如果验证成功就跳转到首页
        return redirect(reverse('users:index'))