from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.users.models import User


# 新增管理员用户---获取用户组信息 序列化器
class AdminSimpleSerialzier(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'

# 获取管理员信息 序列化器
class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

        # 序列化的时候不把密码返回给前端
        extra_kwargs = {
            'password':{'write_only':True}
        }


    # 加密密码和更改is_staff 所以重写create方法
    def create(self, validated_data):

        # 使用super调用ModelSerializer的create方法  自动解包
        user = super().create(validated_data)
        # 更改员工状态
        user.is_staff=True
        # 加密密码
        user.set_password(validated_data['password'])
        user.save()

        # 返回结果
        return user

    # 加密密码
    def update(self, instance, validated_data):

        user = super().update(instance,validated_data)

        if validated_data['password']:

            user.set_password(validated_data['password'])
            user.save()

        return user


