

from rest_framework import serializers
from apps.goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory


# 新增商品频道组---获取一级分类信息 序列化器
class GoodsCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'



# 新增商品频道组---获取频道组信息 序列化器
class ChannelGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsChannelGroup
        fields= '__all__'

# 获取商品频道信息 序列化器
class GoodsChannelSerializer(serializers.ModelSerializer):

    # 使用外键序列化 显示组id和组名字
    group_id = serializers.IntegerField()
    group = serializers.StringRelatedField(read_only=True)
    # 使用外键序列化 显示分类id和分类名字
    category_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsChannel
        fields = '__all__'