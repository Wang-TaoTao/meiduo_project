# oauth 视图

import re

from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse

from django.views import View
from django_redis import get_redis_connection
from pymysql import DatabaseError

from apps.oauth.models import OAuthQQUser, OAuthSinaUser
from apps.users.models import User
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE
from django import http
from utils.secret import SecretOauth
from libs.sinaweibo import sinaweibopy3






# 获取微博登录扫码页面
class WeiboAuthURLView(View):

    def get(self,request):


        # 创建sina登录授权对象
        sina = sinaweibopy3.APIClient(app_key=settings.APP_KEY,app_secret=settings.APP_SECRET,redirect_uri=settings.REDIRECT_URL)

        # 生成授权url地址
        login_url = sina.get_authorize_url()

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK,'errmsg': "OK",'login_url': login_url})




# 用户sina扫码的回调处理
class WeiboAuthOpenidView(View):

    def get(self,request):

        # 接收code
        code = request.GET.get('code')

        # 创建sin登录授权对象
        sina = sinaweibopy3.APIClient(app_key=settings.APP_KEY,app_secret=settings.APP_SECRET,redirect_uri=settings.REDIRECT_URL)

        # 1.根据code 向微博服务器 获取access_token
        result = sina.request_access_token(code)

        # 2.根据access_token 获取openid
        sina.set_access_token(result.access_token,result.expires_in)
        openid = result.uid


        # 判断是否初次授权
        try:
            qquser = OAuthSinaUser.objects.get(uid=openid)
        except:
            # 如果是初次授权 则显示绑定页面
            # 将openid加密
            json_str = SecretOauth().dumps({'openid':openid})
            # 显示绑定页面
            context = {
                'openid':json_str
            }
            return render(request,'oauth_callback.html',context)
        else:
            # 如果不是初次授权 则状态保持 转到相关页面
            user = qquser.user
            # 实现状态保持
            login(request,user)

            # 转到相关页面
            response = redirect(reverse('contents:index'))
            # 将用户名写入cookie
            response.set_cookie('username',user.username,max_age=3600*24*15)
            # 响应结果
            return response


    def post(self,request):

        # 接收openid
        openid_str = request.POST.get('openid')
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code = request.POST.get("sms_code")


        # 校验参数
        # 解密openid
        openid_dict = SecretOauth().loads(openid_str)
        if openid_dict is None:
            return http.HttpResponseForbidden('授权信息无效，请重新授权')
        if not all([mobile,password,sms_code]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 验证短信验证码
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('sms_code')
        redis_sms_code = redis_conn.get('sms_%s' % mobile)

        if redis_sms_code is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'无效的短信验证码'})
        if sms_code.lower() != redis_sms_code.decode().lower():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 取出openid
        openid = openid_dict.get('openid')
        # 处理：  初次授权 完成openid与user的绑定
        # 1 判断手机号是否已经存在
        try:
            user = User.objects.get(mobile=mobile)
        except:
            # 2 手机号不存在 就创建用户
            user = User.objects.create_user(username=mobile,password=password,mobile=mobile)
        else:
            # 3 如果手机号存在的话 就校验密码
            if not user.check_password(password):
                return http.HttpResponseForbidden('手机号已经存在或密码错误')

        # 绑定user和openid : 新建OAuthSinaUser对象
        OAuthSinaUser.objects.create(
            user=user,
            uid=openid,
        )
        # 状态保持
        login(request,user)

        # 重定向到用户原先所在的位置页面
        response = redirect(reverse('contents:index'))

        # 写入cooke
        response.set_cookie('username',user.username,max_age=3600*24*15)

        # 响应结果
        return response




# 提供QQ登录页面网址
class QQAuthURLView(View):
    """提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    """
    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        # next = request.GET.get('next')

        # 获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url':login_url})




# 用户QQ扫码登录的回调处理
class QQAuthUserView(View):
    """用户扫码登录的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 提取code请求参数
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少code')

        # 创建工具对象---- 和QQ认证
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)
            print("TOKEN:---------------",access_token)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
            print("openid------------:", openid)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没绑定美多商城用户
            # 加密 openid--使用itsdangerous
            secret_openid = SecretOauth().dumps({'openid': openid})
            context = {'openid': secret_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            # 如果openid已绑定美多商城用户
            # 实现状态保持
            qq_user = oauth_user.user
            login(request, qq_user)

            # 重定向到主页
            response = redirect(reverse('contents:index'))

            # 登录时用户名写入到cookie，有效期15天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)

            return response


    def post(self, request):
        """美多商城用户绑定到openid"""
        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, pwd, sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('sms_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 解密出openid 再判断openid是否有效
        openid = SecretOauth().loads(openid).get('openid')
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 保存注册数据 判断该用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=pwd, mobile=mobile)
        else:
            # 如果用户存在，检查用户密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # 将用户绑定openid
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 实现状态保持
        login(request, user)

        # 响应绑定结果
        next = request.GET.get('state')
        response = redirect(next)

        # 登录时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response