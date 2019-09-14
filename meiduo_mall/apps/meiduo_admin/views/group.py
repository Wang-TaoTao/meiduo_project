




from django.contrib.auth.models import Group, Permission
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.serializers.group import GroupSerialzier, GroupSimpleSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination

# 新增用户组数据---获取权限表信息
class GroupSimpleAPIView(ListAPIView):

    queryset = Permission.objects.all()

    serializer_class = GroupSimpleSerializer




# 获取用户组数据
class GroupView(ModelViewSet):

    queryset = Group.objects.all()

    serializer_class = GroupSerialzier

    pagination_class = CustomPageNumberPagination