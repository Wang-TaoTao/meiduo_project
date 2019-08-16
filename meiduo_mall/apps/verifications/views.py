from django.shortcuts import render

# Create your views here.
from django.views import View
from django import http

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
        redis_client.setex(uuid,300,text)

        # 响应图片验证码
        return http.HttpResponse(image, content_type = 'image/jpeg')