# orders 视图

import json

from datetime import datetime

from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from apps.areas.models import Address
from apps.goods.models import SKU




from apps.orders.models import OrderInfo, OrderGoods
from utils.response_code import RETCODE








# 展示订单提交成功界面
class OrderSuccessView(LoginRequiredMixin,View):

    def get(self,request):

        # 接收参数
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        # 构造前端需要的数据
        context = {
            'order_id':order_id,
            'payment_amount':payment_amount,
            'pay_method':pay_method,

        }

        return render(request,'order_success.html',context)




# 保存订单基本信息和订单商品信息  ----事务提交----乐观锁
class OrderCommitView(LoginRequiredMixin,View):

    def post(self,request):

        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            address = Address.objects.get(id=address_id)
        except:
            return http.HttpResponseForbidden('参数pay_method错误')
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')




        from django.db import transaction

        # -----------设置事务起点----------
        with transaction.atomic():

            # ----------设置事务保存点---------
            save_id = transaction.savepoint()

            try:

                # 获取用户对象
                user = request.user
                # 生成订单号
                order_id = datetime.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

                # 保存订单基本信息
                order = OrderInfo.objects.create(

                order_id = order_id,
                user = user,
                address = address,
                total_count = 0,
                total_amount = Decimal('0'),
                freight = Decimal('10.00'),
                pay_method = pay_method,
                status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                else OrderInfo.ORDER_STATUS_ENUM['UNSEND']

            )

                # 查询用户选中的购物车数据
                redis_conn = get_redis_connection('carts')
                redis_data = redis_conn.hgetall(user.id)

                carts_dict = {}
                # 取出用户选中的购物车数据
                for key,value in redis_data.items():
                    sku_id = int(key.decode())
                    sku_value = json.loads(value.decode())
                    # 判断是否选中
                    if sku_value['selected']:
                        carts_dict[sku_id] = sku_value

                # 根据选中的购物车数据 遍历商品信息
                for sku_id in carts_dict.keys():

                    while True:

                        sku = SKU.objects.get(id=sku_id)

                        # 设置当前商品操作前（原始）的库存量和销量
                        old_stock = sku.stock
                        old_sales = sku.sales

                        # 取出购物车数据中当前商品的数量（也就是用户购买的当前商品的数量）
                        sku_count = carts_dict[sku_id]['count']
                        # 判断库存是否充足
                        if sku_count > sku.stock:

                            # ------------事务回滚--------------
                            transaction.savepoint_rollback(save_id)

                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})



                        # # 动态修改sku表中的数据 库存减少，销量增加
                        # sku.sales += sku_count
                        # sku.stock -= sku_count
                        # sku.save()

                        # # 模拟资源竞争
                        # import time
                        # time.sleep(10)

                        # 使用乐观锁 更新库存量和销量
                        new_stock = old_stock - sku_count
                        new_sales = old_sales + sku_count
                        result = SKU.objects.filter(id=sku_id,stock = old_stock).update(stock=new_stock,sales=new_sales)


                        # 如果下单失败 --库存足够就继续下单 直到下单成功或库存不足
                        if result == 0:
                            continue

                        # 动态修改spu表中的数据 分类销量增加
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 动态修改商品基本信息表中的 总数量和 总价
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price

                        # 保存商品信息数据
                        OrderGoods.objects.create(
                            order = order,
                            sku = sku,
                            count = sku_count,
                            price = sku.price,
                        )

                        # 下单成功 或 失败跳出
                        break

                # 商品总价钱加上 运费
                order.total_amount += order.freight
                # 保存订单
                order.save()

            except:
                # ------------事务回滚------------
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单失败'})


            # ---------------提交事务-------------
            transaction.savepoint_commit(save_id)


        # 清除购物车中已经结算过的商品
        redis_conn.hdel(user.id,*carts_dict)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})





# 结算订单页面
class OrderSettlementView(LoginRequiredMixin,View):

    def get(self,request):


        # 1 获取用户对象
        user = request.user

        # 2 获取该用户对象的收货地址
        try:
            address = Address.objects.filter(user=user,is_deleted=False)
        except:
            address = None

        # 3 从redis中取出选中的购物车数据
        # 3.1 连接redis
        redis_conn = get_redis_connection('carts')
        # 3.2 取出所有购物车数据
        redis_data = redis_conn.hgetall(user.id)
        # 3.3 取出所有选中的购物车数据
        print(redis_data)
        carts_dict = {}
        for key,value in redis_data.items():
            sku_id = int(key.decode())
            sku_value = json.loads(value.decode())
            # 取出选中的
            if sku_value['selected']:
                carts_dict[sku_id] = sku_value

        # 4 计算总数量和总金额
        total_count = 0
        total_amount = Decimal(0.00)

        # 5 求出所有选中的商品信息中的 数量 总金额
        skus = SKU.objects.filter(id__in = carts_dict.keys())

        for sku in skus:
            # 求出单个商品的数量和金额 动态添加到对应属性中
            sku.count = carts_dict[sku.id]['count']
            sku.amount = sku.count * sku.price

            # 累计求出总数量和总金额
            total_count += sku.count
            total_amount += sku.amount

        # 6 运费
        freight = Decimal('10.00')
        # 7 构造前端需要的数据
        context = {
            'addresses':address,
            'skus':skus,
            'total_count':total_count,
            'total_amount':total_amount,
            'freight':freight,
            'payment_amount':total_amount + freight,
            'default_address_id': user.default_address_id,
        }
        # 8 响应结果
        return render(request,'place_order.html',context)