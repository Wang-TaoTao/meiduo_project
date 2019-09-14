

from rest_framework import serializers
from apps.goods.models import Brand




# 获取品牌信息 序列化器
class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'