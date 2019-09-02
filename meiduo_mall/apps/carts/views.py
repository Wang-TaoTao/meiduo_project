import json

from django import http
from django.shortcuts import render
from django.views import View

from django_redis import get_redis_connection
from apps.goods.models import SKU
from utils.cookiesecret import CookieSecret
from utils.response_code import RETCODE






# 展示商品页面简单购物车
class CartsSimpleView(View):

    def get(self,request):

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户登录 操作redis
            # 1 连接redis
            clident_conn = get_redis_connection('carts')
            # 2 获取当前用户的redis数据
            redis_dict = clident_conn.hgetall(user.id)

            # 3 转换成普通字典
            carts_dict = {}
            for key,value in redis_dict.items():
                stu_id = int(key.decode())
                stu_dict = json.loads(value.decode())
                carts_dict[stu_id] = stu_dict

        else:
            # 如果用户没登录 操作cookie
            # 1 接收cookie_str
            cookie_str = request.COOKIES.get('carts')

            # 2 判断是否有cookie_str
            if cookie_str:
                # 2.1 解密
                carts_dict = CookieSecret.loads(cookie_str)
            else:
                # 2.2 空字典
                carts_dict = {}

        # 构造简单的购物车json数据
        cart_skus = []
        # 获取键
        sku_ids = carts_dict.keys()
        # 根据键获取表中商品信息
        # skus = SKU.objects.filter(id__in = sku_ids)
        # 遍历商品信息
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            cart_skus.append({
                'id':sku.id,
                'name':sku.name,
                'count':carts_dict.get(sku.id).get('count'),
                'default_image_url':sku.default_image.url,
            })

        # 响应json列表数据
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})




# 全选购物车
class CartsSelectAllView(View):

    def put(self,request):

        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected',True)

        # 校验参数
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:

            # 登录 操作redis
            # 1 连接redis
            client_conn = get_redis_connection('carts')
            # 2 获取当前用户所有数据
            carts_dict = client_conn.hgetall(user.id)
            # 3 遍历 当前用户所有数据
            for key,value in carts_dict.items():
                # 3.1 提取所有的键和对应的字典
                sku_id = int(key.decode())
                # 3.2 将所有的sku_id的selected
                sku_dict = json.loads(value.decode())
                sku_dict['selected'] = selected

                # 3.3 修改redis中的值
                client_conn.hset(user.id,sku_id,json.dumps(sku_dict))

            # 4 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})

        else:

            # 没登录 则操作cookie
            # 1 获取cookie
            cookie_str = request.COOKIES.get('carts')

            # 2 构造响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            # 3 判断cookie_str是否为空
            if cookie_str is not None:
                # 3.1 解密
                carts_dict = CookieSecret.loads(cookie_str)
                # 3.2 遍历购物车中的内容
                for sku_id in carts_dict:

                    # 3.2 设置所有sku_id的selected
                    carts_dict[sku_id]['selected'] = selected

                # 3.3 加密
                cookie_sstr = CookieSecret.dumps(carts_dict)

                # 3.4 写入cookie
                response.set_cookie('carts',cookie_sstr,max_age=3600*15*24)

            # 4 响应结果
            return response




# 购物车  增删改查
class CartsView(View):

    # 新增购物车
    def post(self,request):


        # 1接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected',True)
        # 2校验参数
        # 2.1校验参数是否齐全
        if not all([sku_id,count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 2.2校验stu_id商品是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')
        # 2.3校验count是否为整形
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')
        # 2.4校验selected
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 3判断用户是否登录
        user = request.user
        if user.is_authenticated:

            # 如果登录 操作redis
            # 1连接reds
            redis_conn = get_redis_connection('carts')
            # 2取出用户数据
            carts_dict = redis_conn.hgetall(user.id)

            # 3判断用户数据是否存在
            if not carts_dict:
                # 3.1如果不存在 则直接新增记录
                redis_conn.hset(user.id,sku_id,json.dumps({"count":count,"selected":selected}))
            # 4如果用户数据在redis中存在，则判断商品是否已经在购物车中
            if str(sku_id).encode() in carts_dict:
                # 4.1取出商品数据
                child_dict = json.loads(carts_dict[str(sku_id).encode()].decode())

                # 4.2新增当前商品的个数
                child_dict['count'] += count

                # 4.3更新数据
                redis_conn.hset(user.id,sku_id,json.dumps(child_dict))

            # 5如果用户数据在redis中不存在
            else:
                # 5.1则直接更新数据
                redis_conn.hset(user.id,sku_id,json.dumps({"count":count,"selected":selected}))

            # 6响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        else:

            # 如果没登录 操作cookie
            # 1获取cookie
            cookie_str = request.COOKIES.get('carts')

            # 2判断用户是否有cookie_str
            if cookie_str:
                # 2.2解密
                cart_dict = CookieSecret.loads(cookie_str)
            else:
                # 2.2空字典
                cart_dict = {}

            # 3判断要加入购物车的商品是否已经在购物车中
            if sku_id in cart_dict:
                # 3.1取出原来的count
                old_count = cart_dict[sku_id]['count']
                # 3.2新增
                count += old_count

            # 4写入字典
            cart_dict[sku_id]={
                'count':count,
                'selected':selected,
                }

            # 5转换成密文
            cookie_str_dict = CookieSecret.dumps(cart_dict)

            # 6创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

            # 7写入cookie
            response.set_cookie('carts',cookie_str_dict,max_age=3600*15*24)

            # 8响应结果
            return response


    # 展示购物车
    def get(self,request):


        # 1 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 1如果用户登录 获取Redis中的数据
            redis_conn = get_redis_connection('carts')

            # 2获取redis中的所有数据
            redis_data = redis_conn.hgetall(user.id)

            # 3转换成和cookie一样的字典 方便构造数据
            carts_dict = {}
            for key,value in redis_data.items():
                sku_id = int(key.decode())
                sku_dict = json.loads(value.decode())
                carts_dict[sku_id] = sku_dict

        else:
            # 1如果用户没登录 获取Cookie中的数据
            cookie_str = request.COOKIES.get('carts')

            # 2判断是否有cookie_str
            if cookie_str:
                # 2.1解密
                carts_dict = CookieSecret.loads(cookie_str)

            else:
                # 2.2空字典
                carts_dict = {}

        # 3将carts_dict中的sku_id取出来
        sku_ids = carts_dict.keys()

        # 4根据sku_id取出所有商品对象
        # skus_data = SKU.objects.filter(id__in=sku_ids)
        cart_skus= []
        # 5遍历商品对象
        for sku_id in sku_ids:
            sku = SKU.objects.get(id = sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts_dict.get(sku.id).get('count')),
            })

        context = {
            'cart_skus': cart_skus,
            }

        return render(request,'cart.html',context)


    # 修改购物车
    def put(self,request):


        # 1 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected',True)


        # 2 校验参数
        if not all([sku_id,count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')

        try:
            count != int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count有误')

        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')


        # 3 判断用户是否登录
        user = request.user
        if user.is_authenticated:

            # 如果用户登录 redis
            # 1 连接redis
            client_conn = get_redis_connection('carts')

            # 2 修改redis数据
            client_conn.hset(user.id,sku_id,json.dumps({"count":count,"selected":selected}))

        else:

            # 如果用户没登录 cookie
            # 1 读取cookie
            cookie_str = request.COOKIES.get('carts')

            # 2 判断用户是否操作过cookie
            if cookie_str:
                # 2.1解密
                carts_dict = CookieSecret.loads(cookie_str)

            else:
                # 2.2空字典
                carts_dict = {}

            # 3 修改cookie数据
            carts_dict[sku_id] = {
                'count':count,
                'selectd':selected,
            }

            # 4 加密
            cookie_sstr = CookieSecret.dumps(carts_dict)

        # 5 构建前端的数据
        cart_sku = {
            'id': sku_id,
            'count': count,
            'selected': selected,
            'name': sku.name,
            'default_image_url': sku.default_image.url,
            'price': sku.price,
            'amount': sku.price * count,
        }

        # 6 构造响应对象
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        # 7 如果用户设没登录的状态 就将数据写入cookie
        if not user.is_authenticated:
            response.set_cookie('carts',cookie_sstr,max_age=3600*5*24)

        # 8 响应结果
        return response


    # 删除购物车
    def delete(self,request):

        # 1 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 2 校验参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        # 3 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户登录，操作redis
            # 1 连接redis
            client_conn = get_redis_connection('carts')

            # 2 删除redis中数据
            client_conn.hdel(user.id,sku_id)

            # 3 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})

        else:
            # 如果用户没登录 操作cookie
            # 1 获取cookie
            cookie_str = request.COOKIES.get('carts')

            # 2 判断用户是否操作过cookie
            if cookie_str:
                # 2.1 解密
                carts_dict = CookieSecret.loads(cookie_str)

            else:
                # 2.2 空字典
                carts_dict = {}

            # 3 构造响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            # 4 判断 商品 是否在cookie中
            if sku_id in carts_dict:
                # 4.1删除数据
                del carts_dict[sku_id]
                # 4.2加密
                cookie_sstr = CookieSecret.dumps(carts_dict)
                # 4.3将结果写入cookie
                response.set_cookie('carts', cookie_sstr, max_age=3600 * 15 * 24)

            # 5 响应结果
            return response






