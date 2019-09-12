
from rest_framework import serializers
from rest_framework.views import APIView

from apps.goods.models import SKUImage, SKU


# 获取新增图片时候的sku表id 序列化器
class SKUSeriazlier(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id','name']





# 获取图片信息 序列化器
class ImageSeriazlier(serializers.ModelSerializer):

    # 返回图片关联的sku的id值
    sku = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUImage
        fields = ['id','sku','image']


