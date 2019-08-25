# users 视图

import json

from django.conf import settings
from django.contrib.auth import login
from django.contrib.messages.storage import session
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from itsdangerous import BadData
from apps.areas.models import Address

from apps.verifications import constants
from utils.response_code import RETCODE
import re
from apps.users.models import User
from meiduo_mall.settings.dev import logger
from django.contrib.auth.mixins import LoginRequiredMixin






# 用户收货地址
class AddressView(View):

    def get(self,request):
        '''提供收货地址界面'''
        # 获取用户地址列表
        login_user = request.user
        addresses = Address.objects.filter(user=login_user,is_deleted=False)

        address_list = []
        for address in addresses:
            address_list.append(
                {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email

                }
            )
        context = {
            'default_address_id':login_user.default_address_id,
            'addresses':address_list
        }
        return render(request, 'user_center_site.html', context)



# 验证链接提取user信息
def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    from utils.secret import SecretOauth
    try:
        token_dict = SecretOauth().loads(token)
    except BadData:
        return None

    try:
        user = User.objects.get(id=token_dict['user_id'], email=token_dict['email'])
    except Exception as e:
        logger.error(e)
        return None
    else:
        return user



# 邮箱的验证
class VerifyEmailView(LoginRequiredMixin,View):
    """验证邮箱"""

    def get(self, request):
        """实现邮箱验证逻辑"""
        # 接收参数
        token = request.GET.get('token')

        # 校验参数：判断token是否为空和过期，提取user
        if not token:
            return http.HttpResponseBadRequest('缺少token')

        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden('无效的token')

        # 修改email_active的值为True
        try:
            request.user.email_active = True
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')

        # 返回邮箱验证结果
        return redirect(reverse('users:info'))



# 邮箱
class EmailView(LoginRequiredMixin,View):

    def put(self,request):
        '''实现邮箱添加逻辑'''

        # 接收参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict['email']
        print("邮箱是:",email)


        # 校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 赋值email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})


        # 拼接url
        from apps.users.utils import generate_verify_email_url
        verify_url = generate_verify_email_url(request.user)

        # 4.异步发送邮件
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)


        # 5.响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})



# 个人中心
class UserInfoView(LoginRequiredMixin,View):

    def get(self,request):
        '''提供个人信息界面'''
        context = {
            'username':request.user.username,
            'mobile':request.user.mobile,
            'email':request.user.email,
            'email_active':request.user.email_active,
        }


        return render(request,'user_center_info.html',context=context)



# 登录功能
class LoginView(View):

    def get(self,request):
        '''登录界面'''
        return render(request,'login.html')


    def post(self,request):

        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        if not all([username,password]):
            return http.HttpResponseForbidden("请将信息填写完整！")

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名！")

        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):
            return http.HttpResponseForbidden("请输入8-20个字符的密码！")

        # 校验账户
        from django.contrib.auth import authenticate,login
        user = authenticate(username=username,password=password)

        if user is None:

            return render(request,'login.html',{'account_errmsg':"用户名或密码错误"})

        # 保持登陆状态
        login(request,user)

        # 是否记住用户名
        if remembered == 'on':
            request.session.set_expiry(None)

        else:
            request.session.set_expiry(0)

        # 翻转首页 next
        next = request.GET.get('next')
        if next:

            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))


        # 实现合并购物车
        from apps.carts.utils import merge_cart_cookie_to_redis
        response = merge_cart_cookie_to_redis(request,response,user)


        response.set_cookie('username',user.username,max_age=3600*24*15)

        # 返回响应结果
        return response



# 退出
class LogOutView(View):

    def get(self,request):

        from django.contrib.auth import logout
        logout(request)

        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        return response



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
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')


        # 校验参数
        if not all([username, password, password2, mobile, allow]):

            return http.HttpResponseForbidden("缺少参数，请把信息输入完整！")

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$',username):

            return http.HttpResponseForbidden("请输入5-20位的用户名！")

        if not re.match(r'^[0-9A-Za-z]{8,20}$',password):

            return http.HttpResponseForbidden("请输入8-20位的密码!")

        if password != password2:

            return http.HttpResponseForbidden("请输入相同的密码！")

        if not re.match(r'^1[345789]\d{9}$',mobile):

            return http.HttpResponseForbidden("请输入正确的手机号！")

        # 短信验证
        sms_code = request.POST.get('msg_code')
        from django_redis import get_redis_connection
        sms_code_redis = get_redis_connection('sms_code')
        redis_sms_code = sms_code_redis.get('sms_%s' % mobile)

        # 判空
        if redis_sms_code is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        # 对比验证码
        if sms_code.lower() != redis_sms_code.decode().lower():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})



        # # 保存短信验证码
        # sms_code_redis.setex('sms_%s' % phone,constants.SMS_CODE_REDIS_EXPRES,sms_code)
        # # 重新写入send_flag
        # sms_code_redis.setex('send_flag_%s' % phone,constants.SEND_SMS_CODE_INTERVAL,1)

        if allow != "on":

            return http.HttpResponseForbidden("请勾选协议！")

        try:
            user = User.objects.create_user(username=username,password=password,mobile=mobile)

        except Exception as e:
            logger.error(e)

            return render(request,'register.html',{'register_error': '注册失败'})

        # 保持会话登录状态
        login(request, user)


        # 如果验证成功就跳转到首页
        response = redirect(reverse('contents:index'))
        response.set_cookie('username',user.username,max_age=3600*24*15)
        return response