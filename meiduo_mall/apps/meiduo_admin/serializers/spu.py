

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from apps.goods.models import SPU, Brand, GoodsCategory





# 新增SPU数据---获取一级分类信息 序列化器
class CategorysSerizliser(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'



# 新增SPU数据---获取品牌信息  序列化器
class BrandsSerizliser(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'



# 获取SPU数据 序列化器
class SPUSerializer(serializers.ModelSerializer):

    brand_id = serializers.IntegerField()
    brand = serializers.StringRelatedField(read_only=True)

    category1_id = serializers.IntegerField()
    category1 = serializers.StringRelatedField(read_only=True)

    category2_id = serializers.IntegerField()
    category2 = serializers.StringRelatedField(read_only=True)

    category3_id = serializers.IntegerField()
    category3 = serializers.StringRelatedField(read_only=True)


    class Meta:
        model = SPU
        fields = '__all__'


