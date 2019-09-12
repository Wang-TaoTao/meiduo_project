from django.contrib.auth.backends import ModelBackend
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.response import Response

from apps.users.models import User

# 前后端请求验证 目的是只让管理员或者公司员工登录后台管理系统
class MeiduoModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):

        # 判断是后端用户请求还是前端用户请求  为None说明是后端用户请求
        if request is None:
            # 如果是后端请求
            # 判断用户输入的是用户名还是手机号
            try:
                user = User.objects.get(username=username,is_staff=True)
            except:

                try:
                    user = User.objects.get(mobile=username,is_staff=True)
                except:
                    return None

            # 校验密码
            if user.check_password(password):
                return user
            else:
                return None

        else:
            # 如果是前端请求
            # 同样判断用户输入的是用户名还是手机号
            try:
                user = User.objects.get(username=username)
            except:

                try:
                    user = User.obejcts.get(mobile=username)
                except:
                    return None

            # 校验密码
            if user.check_password(password):
                return user
            else:
                return None

