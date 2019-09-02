# verfications 视图函数
import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http

from apps.users.models import User
from apps.verifications import constants
from celery_tasks.sms.tasks import ccp_send_sms_code
from meiduo_mall.settings.dev import logger
from django_redis import get_redis_connection

from utils.cookiesecret import CookieSecret
from utils.response_code import RETCODE












# 找回密码第三步 （设置新密码）
class PwdRetpasswordView(View):

    def post(self,request,username):

        # 接收参数
        json_dict = json.loads(request.body.decode())
        password = json_dict.get('password')
        password2 = json_dict.get('password2')
        access_token = json_dict.get('access_token')

        # 校验参数
        if not all([password,password2,access_token]):
            return http.JsonResponse({'error':'数据错误'},status=400)

        # 解密
        token = CookieSecret.loads(access_token)

        user_id = token['user_id']
        user_mobile = token['mobile']
        try:
            user = User.objects.get(id=user_id,mobile=user_mobile)
        except:
            return http.JsonResponse({'error':'数据错误'},status=400)
        if password != password2:
            return http.JsonResponse({'error':'数据错误'},status=400)

        # 修改密码
        user.set_password(password)
        user.save()


        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})





# 找回密码第二步 （验证短信验证码）
class PwdSMSCodeView(View):

    def get(self,request,username):


        # 接收参数
        sms_code = request.GET.get('sms_code')
        print("用户输入的短信验证码:",sms_code)

        # 取出用户对象信息，校验用户名是否正确
        try:
            user = User.objects.get(username=username)
        except:
            return http.JsonResponse({'error':'该用户不存在'},status=400)
        # 校验参数
        # 1 从redis中取出短信验证码
        redis_conn = get_redis_connection('sms_code')
        redis_sms_code = redis_conn.get('sms_%s' % user.mobile)
        print("user.mobile",user.mobile)
        print("redis取出来的短信验证码是：",redis_sms_code)
        # 2 判断是否过期
        if redis_sms_code is None:
            return http.JsonResponse({'error':'验证过期了，再发送一次吧'}, status = 400)
        # 3 删除Redis中的验证码
        redis_conn.delete('sms_%s' % user.mobile)

        # 4 判断短信验证码是否正确
        if sms_code.lower() != redis_sms_code.decode().lower():
            return http.JsonResponse({'error':'验证码错误'}, status = 400)

        # 加密
        json_str = CookieSecret.dumps({'user_id': user.id, 'mobile': user.mobile})

        # 响应结果
        return http.JsonResponse({'mobile': user.mobile, 'access_token': json_str})





# 找回密码第二步 （验证access_token,发送短信)
class PwdTokenView(View):

    def get(self,request):

        # 接收参数
        access_token = request.GET.get('access_token')

        # 解密
        token = CookieSecret.loads(access_token)
        # 提取用户id和手机号
        user_id = token['user_id']
        user_mobile = token['mobile']

        print("提出来的用户手机号:",user_mobile)

        # 校验用户的手机号是否存在
        try:
            mobile = User.objects.get(id=user_id,mobile=user_mobile)
        except:
            return http.JsonResponse({'error':'手机号不正确'},status=400)

        # 生成短信验证码
        from random import randint
        sms_code = '%06d' % randint(0,999999)
        # 写入redis中
        redis_conn = get_redis_connection('sms_code')
        redis_conn.setex('sms_%s' % user_mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)


        # 异步发送短信
        ccp_send_sms_code.delay(user_mobile,sms_code)
        print("手机验证码是:", sms_code)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})





# 找回密码第一步 （验证用户名和图形验证码）
class PwdCodeView(View):

    def get(self,request,username):

        # 接收参数 （图形验证码）
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('text')
        print("用户名:",username)
        print("用户输入的验证码:",image_code)

        # 连接redis数据库取出验证码
        redis_conn = get_redis_connection('verify_image_code')
        redis_image_code = redis_conn.get('img_%s' % uuid)
        print(redis_image_code)

        # 校验验证码是否过期
        if redis_image_code is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已过期，点击图片换一个'})

        # 立即删除redis中的图形验证码
        redis_conn.delete('img_%s' % uuid)

        # 判断用户输入的验证码是否正确
        if image_code.lower() != redis_image_code.decode().lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码错误'})

        # 校验用户名是否存在
        try:
            user = User.objects.get(username=username)
        except:
            return http.JsonResponse({}, status=404)

        print("该用户的手机号:",user.mobile)

        # 加密
        json_str = CookieSecret.dumps({'user_id':user.id,'mobile':user.mobile})

        # 响应结果
        return http.JsonResponse({'mobile': user.mobile, 'access_token': json_str})






#  验证图片验证码和短信验证码
class SMSCodeView(View):

    def get(self,request,mobile):

        # 接收uuid和用户输入的验证码
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')
        # 连接redis,根据uuid取出图片验证码
        image_client_redis = get_redis_connection('verify_image_code')
        image_code_redis = image_client_redis.get('img_%s' % uuid)

        # 判None
        if image_code_redis is None:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})

        # 删除redis数据库中的uuid中的图片验证码
        try:
            image_client_redis.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)

        # 判断redis取出来的数据和用户输入的验证码是否相等
        if image_code.lower() != image_code_redis.decode().lower():
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码有误'})

        # 生成短信验证码
        from random import randint
        sms_code = "%06d" % randint(0,999999)
        # 保存验证码到redis数据库
        sms_client_redis = get_redis_connection('sms_code')
        # sms_client_redis.setex('sms_%s' % mobile ,300 ,sms_code)

        # 避免频繁发送短信验证码
        # send_flag = sms_client_redis.get('send_flag_%s' % mobile)


        # if send_flag:
        #     return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 创建Redis管道
        pl = sms_client_redis.pipeline()
        # 将Redis请求添加到队列
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行请求
        pl.execute()

        # 使用第三方平台荣联云给手机号发短信
        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile,[sms_code,5],1)

        # Celery异步发送短信验证码
        from celery_tasks.sms.tasks import ccp_send_sms_code
        ccp_send_sms_code.delay(mobile, sms_code)
        print("当前验证码是:",sms_code)
        print("手机号:",mobile)

        # 告诉前端 短信发送完毕
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功！'})




# 图形验证码
class ImageCodeView(View):

    def get(self, request, uuid):
        '''

        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属的用户
        :return:  image/jpg
        '''
        # 生成图片验证码
        from libs.captcha.captcha import captcha
        text, image = captcha.generate_captcha()

        # 保存图片验证码
        from django_redis import get_redis_connection
        redis_client = get_redis_connection('verify_image_code')
        redis_client.setex('img_%s' % uuid,constants.IMAGE_CODE_REDIS_EXPIRES,text)


        # 响应图片验证码
        return http.HttpResponse(image, content_type = 'image/jpeg')


