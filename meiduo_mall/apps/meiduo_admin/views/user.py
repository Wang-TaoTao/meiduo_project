
from rest_framework.generics import  ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.meiduo_admin.serializers.user import UserSerializer, UserAddSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination
from apps.users.models import User




# 查询用户信息
class UserListView(ListCreateAPIView):

    # 获取查询集
    # queryset = User.objects.all()
    # 设置序列化器对象
    # serializer_class = UserSerializer
    # 设置分页
    pagination_class = CustomPageNumberPagination


    # 模糊搜索功能  根据关键字内容返回不同的查询集
    def get_queryset(self):

        # 接收搜索关键字参数
        keyword = self.request.query_params.get('keyword')
        # 根据关键字内容返回不同的查询集
        if keyword:
            # 返回模糊搜索查询集
            return User.objects.filter(username__contains=keyword)
        # 返回所有用户信息查询集
        return User.objects.all()



    # 新增用户功能  根据不同的请求方式来返回不同的序列化器
    def get_serializer_class(self):
        # 根据不同的请求方式来返回不同的序列化器
        if self.request.method == 'GET':
            # 返回查询序列化器
            return UserSerializer
        # 如果是post方式返回新增用户序列化器
        return UserAddSerializer