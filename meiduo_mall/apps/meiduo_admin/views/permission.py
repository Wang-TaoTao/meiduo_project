





from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.serializers.permission import PermissionSerialzier, ContentTypeSerialzier
from apps.meiduo_admin.utils import CustomPageNumberPagination



# 新增用户权限---获取权限类别信息
class ContentTypeAPIView(ListAPIView):

    queryset = ContentType.objects.all()

    serializer_class = ContentTypeSerialzier




# 获取用户权限数据  ---增删改查功能
class PermissionView(ModelViewSet):

    queryset = Permission.objects.all()

    serializer_class = PermissionSerialzier

    pagination_class = CustomPageNumberPagination