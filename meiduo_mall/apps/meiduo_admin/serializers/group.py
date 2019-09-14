

from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

# 新增用户组数据---获取权限表信息
class GroupSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


# 获取用户组信息 序列化器
class GroupSerialzier(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'