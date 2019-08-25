# verfications 视图函数

from django.shortcuts import render


from django.views import View
from django import http
from apps.verifications import constants
from meiduo_mall.settings.dev import logger


# 短信验证码
from utils.response_code import RETCODE






#  验证图片验证码和短信验证码
class SMSCodeView(View):

    def get(self,request,mobile):

        # 接收uuid和用户输入的验证码
        uuid = request.GET.get('image_code_id')
        image_code = request.GET.get('image_code')
        # 连接redis,根据uuid取出图片验证码
        from django_redis import get_redis_connection
        image_client_redis = get_redis_connection('verify_image_code')
        image_code_redis = image_client_redis.get('img__%s' % uuid)

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
        send_flag = sms_client_redis.get('send_flag_%s' % mobile)


        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

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
        redis_client.setex('img__%s' % uuid,constants.IMAGE_CODE_REDIS_EXPIRES,text)


        # 响应图片验证码
        return http.HttpResponse(image, content_type = 'image/jpeg')


