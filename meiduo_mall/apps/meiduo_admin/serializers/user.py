



from rest_framework import serializers
from rest_framework.response import Response

from apps.users.models import User

# 查询用户信息 序列化器
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','username','mobile','email']


# 新增用户 序列化器
class UserAddSerializer(serializers.ModelSerializer):

    # 新增外键  并设置参数write_only = True 表示序列化的时候不会输出 ，只作为反序列化输入使用。
    passcheck = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','username','mobile','email','password','passcheck']
        extra_kwargs={
            'password':{'write_only':True}
        }

    # 校验密码
    def validate(self, attrs):

        password = attrs.get('password')
        passcheck = attrs.get('passcheck')

        if password != passcheck:
            raise serializers.ValidationError("两次密码输入不一致")

        return attrs



    # 重写create方法
    def create(self, validated_data):
        # 入库之前先删除校验密码passcheck 因为数据库中没有这个字段
        del validated_data['passcheck']

        # 创建用户信息 并加密密码
        try:
            user = User.objects.create_user(**validated_data)
        except:
            return Response(404)

        return user
# from fdfs_client.client import Fdfs_client
#
# # 1.创建客户端找到Tracker Server
# client = Fdfs_client('utils/fastdfs/client.conf')
# # 2.上传图片
# client.upload_by_filename('/home/python/Desktop/en.jpg')
# # 3.返回file_id