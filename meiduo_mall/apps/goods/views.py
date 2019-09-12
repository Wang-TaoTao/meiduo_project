# goods 视图


import json
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from apps.contents.utils import get_categories
from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from apps.orders.models import OrderInfo, OrderGoods
from apps.verifications import constants
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE





# 商品评论的详情
class CommentDetailView(View):

    def get(self, request, sku_id):

        # 获取这个商品的评论对象
        try:
            comment = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')
        except:
            return
        comment_list = []
        # 遍历这个商品的所有评论信息
        for com in comment:
            username = com.order.user.username
            comment_list.append({
                'score': com.score,
                'comment': com.comment,
                'username': username[0] + '***' + username[-1] if com.is_anonymous else username,

            })
        count = len(comment_list)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "OK", 'comments': comment_list,'count':count})





# 去评价 保存评价信息
class CommentView(LoginRequiredMixin,View):

    def get(self,request):

        # 接收参数
        order_id = request.GET.get('order_id')

        # 查询该商品信息
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except:
            return http.HttpResponseNotFound('订单不存在')

        detail_list = []
        for detail in order.skus.all():

            detail_list.append({

                'default_image_url':detail.sku.default_image.url,
                'name':detail.sku.name,
                'total_mcount':str(detail.order.total_amount),
                'price':str(detail.price),
                'order_id':order_id,
                'sku_id':detail.sku.id,


            })

        # 构造前端需要的数据
        context = {
            'skus':detail_list,
        }


        return render(request,'goods_judge.html',context)


    def post(self,request):

        # 接收参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        display_score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')


        # 校验参数
        if not all([order_id,sku_id,display_score,comment]):
            return
        if not isinstance(is_anonymous,bool):
            return
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')

        try:
            goods = OrderGoods.objects.get(order_id=order_id)
        except:
            return

        # 保存数据
        goods.score = display_score
        goods.comment = comment
        goods.is_commented = True
        goods.is_anonymous = is_anonymous
        goods.save()

        # 累计评论数据
        sku.comments +=1
        sku.save()
        sku.spu.comments +=1
        sku.spu.save()

        # 修改订单基本信息表状态
        try:
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])
        except:
            return

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK,'errmsg': 'OK'})






# 展示用户全部订单
class ShowOrderView(LoginRequiredMixin,View):

    def get(self,request,page_num):

        # 取出用户的所有订单信息
        user = request.user

        try:
            order = OrderInfo.objects.filter(user_id=user.id).order_by('-create_time')
        except:
            return

        # 将所有订单信息分页
        paginator = Paginator(order,5)

        # 获取当前页数据
        page = paginator.page(page_num)

        # 获取所有页数
        total_page = paginator.num_pages

        # 遍历当前页所有订单信息
        info_list = []
        for order_id in page:

            detail_list = []
            # 遍历当前页所有信息的商品信息
            for detail in order_id.skus.all():
                detail_list.append({
                    'default_image_url':detail.sku.default_image.url,
                    'name':detail.sku.name,
                    'count':detail.count,
                    'price':detail.price,
                    'total_amount':detail.count * detail.price,

                })

            info_list.append({
                'create_time':order_id.create_time,
                'order_id':order_id.order_id,
                'details':detail_list,
                'total_amount':order_id.total_amount,
                'freight':order_id.freight,
                'status':order_id.status,
                'pay_method':order_id.pay_method,
            })


        # 构造前端需要的数据
        context = {
            'page':info_list,
            'page_num':page_num,
            'total_page':total_page,

        }

        # 响应结果
        return render(request,'user_center_order.html',context)






# 用户浏览记录
class UserBrowseHistory(LoginRequiredMixin,View):



    def post(self,request):
        '''保存用户浏览记录'''

        # 1.接收json参数
        sku_id = json.loads(request.body.decode()).get('sku_id')

        # 2.根据sku_id查询sku商品，判断商品是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.HttpResponseForbidden('商品不存在!')

        # 3.连接redis数据库
        history_redis = get_redis_connection('history')
        # 4.提取用户id
        user_key = "history_%s" % request.user.id

        # 5.使用管道 进行增删改查
        p1 = history_redis.pipeline()
        # 5.1 去重
        p1.lrem(user_key,0,sku_id)
        # 5.2 写入
        p1.lpush(user_key,sku_id)
        # 5.3 截取5条记录
        p1.ltrim(user_key,0,4)
        # 5.4 执行管道
        p1.execute()

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})



    def get(self,request):
        '''获取用户浏览记录'''

        # 获取Redis数据库中sku_id的列表信息
        # 先和Redis数据库建立连接
        sku_redis = get_redis_connection('history')
        # 取出信息
        sku_ids = sku_redis.lrange('history_%s' % request.user.id, 0, -1)

        # 根据sku_id信息取出表中的商品信息
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
            })

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': sku_list})




# 分类统计商品访问量
class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self,request,category_id):

        # 获取当前商品
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseNotFound('缺少必传参数')

        # 查询日期数据
        from datetime import datetime

        # 将日期格式转换为字符串
        today_str = datetime.now().strftime('%Y-%m-%d')

        # 将字符串转换为日期
        today_date = datetime.strptime(today_str,'%Y-%m-%d')

        try:
            # 如果有当天商品分类的数据 就直接增加数量
            count_data = category.goodsvisitcount_set.get(date=today_date)
        except Exception as e:
            # 否则 新增一条记录 然后增加数量
            count_data = GoodsVisitCount()

        # 增加数量
        try:
            count_data.count += 1
            count_data.category = category
            count_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('新增失败')

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})




# 商品详情页
class DetailView(View):

    def get(self,request,sku_id):

        # 获取当前sku信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            logger.error(e)
            return render(request, '404.html')

        # 调用商品分类频道
        categories = get_categories()

        # 调用面包屑组件
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)



# 热销排行
class HotGoodsView(View):

    def get(self,request,category_id):


        # 根据销量排行
        skus = SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')

        # 取前两名
        skus = skus[:2]

        # 序列化
        hot_skus = []
        for sku in skus:

            hot_skus.append({
                'id':sku.id,
                'default_image_url':sku.default_image.url,
                'name':sku.name,
                'price':sku.price,
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})





# 商品列表页  （商品频道分类、面包屑、排序、分页）
class ListView(View):

    def get(self,request,category_id,page_num):


        # 判断有没有三级分类数据
        try:
            category = GoodsCategory.objects.get(id=category_id)

        except Exception as e:
            logger.error(e)
            return http.HttpResponseNotFound('GoodsCategory does not exist')

        # 调用商品频道分类分数
        categories = get_categories()

        # 调用面包屑导航
        breadcrumb = get_breadcrumb(category)


        # 按照排序规则查询该分类商品SKU信息
        # 获取用户的查询方式
        sort = request.GET.get('sort','default')
        # 判断
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort_field = 'create_time'


        # SKU信息排序
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(sort_field)


        # 分页
        from django.core.paginator import Paginator
        # 实例化分页器 提供内容和分页的数
        pagenator = Paginator(skus,constants.GOODS_LIST_LIMIT)
        # 获取总页数
        total_page = pagenator.num_pages
        # 获取每页的数据
        try:
            page_skus = pagenator.page(page_num)

        except Exception as e:
            logger.error(e)
            return http.HttpResponseNotFound('empty page')

        # 渲染页面
        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        # 响应结果
        return render(request,'list.html',context)




