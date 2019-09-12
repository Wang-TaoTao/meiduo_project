



from rest_framework import serializers

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods

# 获取订单商品详情信息 sku 名字  序列化器
class SKUSerialzier(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id','name','default_image']

# 获取订单商品详情信息 商品详情 序列化器
class OrderGoodsSerialziers(serializers.ModelSerializer):

    sku = SKUSerialzier()

    class Meta:
        model = OrderGoods
        fields = '__all__'


# 获取订单及详情信息 修改订单状态 序列化器
class OrderSeriazlier(serializers.ModelSerializer):


    skus = OrderGoodsSerialziers(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'


