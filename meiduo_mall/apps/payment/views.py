import os

from alipay import AliPay
from django import http
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from apps.orders.models import OrderInfo
from apps.payment.models import Payment
from utils.response_code import RETCODE






# 保存订单支付结果
class PaymentStatusView(View):

    def get(self,request):

        # 接受参数
        query_dict = request.GET
        data = query_dict.dict()
        # 取出sign标签并删除
        signature = data.pop('sign')
        # 生成支付宝支付对象
        alipay = AliPay(
            appid = settings.ALIPAY_APPID,
            app_notify_url = None,
            app_private_key_path= os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/app_private_key.pem'),

            alipay_public_key_path= os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/alipay_public_key.pem'),

            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG,


        )
        # 检查这个重定向是否是alipay重定向过来的
        success = alipay.verify(data,signature)
        # 如果正确的话
        if success:
            # 取出订单号
            order_id = data.get('out_trade_no')
            # 取出支付宝流水好
            trade_id = data.get('trade_no')
            # 保存支付模型类信息
            Payment.objects.create(
                order_id = order_id,
                trade_id = trade_id,

            )

            # 更改支付状态
            OrderInfo.objects.filter(order_id=order_id,status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])


            # 构造前端需要的数据
            context = {
                'trade_id':trade_id,
            }
            # 响应结果
            return render(request, 'pay_success.html', context)

        else:
            # 如果不正确 订单支付失败 重定向到我的订单
            return http.HttpResponseForbidden('非法请求')


# 支付宝支付订单功能  --- 生成登录支付宝链接
class PaymentView(LoginRequiredMixin,View):

    def get(self,request,order_id):

        # 获取用户
        user = request.user
        # 查询要获取的订单
        try:
            order = OrderInfo.objects.get(user=user,order_id=order_id,status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return

        # 创建支付宝支付对象
        alipay = AliPay(
            appid =  settings.ALIPAY_APPID,
            app_notify_url = None,
            app_private_key_path= os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/app_private_key.pem'),
            alipay_public_key_path= os.path.join(os.path.dirname(os.path.abspath(__file__)),'keys/alipay_public_key.pem'),
            sign_type="RSA2",
            debug= settings.ALIPAY_DEBUG,

        )

        # 获取登录支付宝支付链接
        order_string = alipay.api_alipay_trade_page_pay(

            subject = "美多商城 %s " % order_id,
            out_trade_no = order_id,
            total_amount = str(order.total_amount),
            return_url= settings.ALIPAY_RETURN_URL,
            notify_url= None,

        )

        # 拼接支付宝登录链接
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
