from datetime import date, timedelta


from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.goods.models import GoodsVisitCount
from apps.meiduo_admin.serializers.statistical import GoodsVisitCountSerialzer
from apps.orders.models import OrderInfo
from apps.users.models import User




# 统计日分类商品访问量
class UserCategoryCountAPIView(APIView):

    def get(self,request):

        # 1.获取当天日期
        now_date = date.today()
        # 2.查询当天每个分类商品的访问量
        try:
            goods = GoodsVisitCount.objects.filter(date=now_date)
        except:
            return Response(404)

        # data = []
        # for good in goods:
        #     data.append({
        #         'count':good.count,
        #         'category':good.category.name,
        #     })

        # 3.使用序列化器
        s = GoodsVisitCountSerialzer(instance=goods,many=True)
        # 4.响应结果
        return Response(s.data)



# 统计月增用户
class UserMonthCountAPIView(APIView):

    def get(self,request):

        # 1.获取当天日期
        now_date = date.today()
        # 2.根据当天日期获取30天前的日期
        month_start_date = now_date - timedelta(days=30)
        data = []
        # 3.遍历
        for i in range(30):
            # 3.1 求出30天前的第一天日期
            start_date = month_start_date + timedelta(i)
            # 3.2 求出30天前的第二天日期
            end_date = month_start_date + timedelta(i+1)
            # 3.3 根据日期求出每天增加的人数
            try:
                count = User.objects.filter(date_joined__gte=start_date,date_joined__lte=end_date).count()
            except:
                return Response(404)
            # 3.4 将每日的赠数量追加到列表
            data.append({
                'count':count,
                'date':start_date,
            })

        # 4.响应结果
        return Response(data)



# 统计日下单用户量
class UserDailyOrderCountAPIView(APIView):

    # 设置权限
    permission_classes = [IsAdminUser]


    def get(self,request):

        # 1.获取当天日期
        now_date = date.today()
        # 2.获取当天下单的所有用户对象
        try:
            users = User.objects.filter(orderinfo__create_time__gte=now_date)

        except:
            return Response(404)

        count_list = []
        # 3.遍历所有当天下单的用户对象，去重
        for user in users:
            # 3.1 判断该用户id是否已存在列表中
            if user.id not in count_list:
                # 3.2 如果不存在，将用户id添加到列表中
                count_list.append(user.id)
        # 4.求出列表长度，也就是用户的数量
        count= len(count_list)

        # 5.响应结果
        return Response({
            'count':count,
            'date':now_date,
        })



# 统计日活跃用户
class UserDailyActiveCountAPIView(APIView):


    def get(self,request):

        # 1.获取当天日期
        now_date = date.today()
        # 2.查询user表中最后登录日期是今天的用户
        try:
            count = User.objects.filter(last_login__gte=now_date).count()
        except:
            return Response(404)
        # 3.响应结果
        return Response({
            'count':count,
            'date':now_date,
        })



# 统计日增用户
class UserDailyCountAPIView(APIView):

    def get(self,request):

        # 1.获取当天日期
        now_date = date.today()
        # 2.查询创建日期为今天的所有用户数量
        try:
            count = User.objects.filter(date_joined__gte=now_date).count()
        except:
            return Response(404)
        # 3.响应结果
        return Response({
            'count':count,
            'date':now_date,
        })



# 统计用户总数
class UserTotalCountAPIView(APIView):

    def get(self,request):


        # 1.获取今天日期
        now_date = date.today()
        # 2.查询所有用户
        try:
            count = User.objects.all().count()
        except:
            return Response(404)

        # 3.响应结果
        return Response({
            'count':count,
            'date':now_date,
        })