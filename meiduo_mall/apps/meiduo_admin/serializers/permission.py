




from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

# 新增权限数据---获取权限类别信息 序列化器
class ContentTypeSerialzier(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields= ['id','name']


# 获取用户权限数据 序列化器
class PermissionSerialzier(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'