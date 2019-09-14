
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from apps.meiduo_admin.serializers.channel import GoodsChannelSerializer, ChannelGroupSerializer, \
    GoodsCategorySerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination





# 获取商品频道信息
class ChannelsView(ModelViewSet):

    queryset = GoodsChannel.objects.all()

    serializer_class = GoodsChannelSerializer

    pagination_class = CustomPageNumberPagination

    # 自定义方法 获取频道组信息
    def channel_types(self,request):

        channel = GoodsChannelGroup.objects.all()

        s = ChannelGroupSerializer(instance=channel,many=True)

        return Response(s.data)

    # 自定义方法 获取一级分类信息
    def categories(self,request):

        category = GoodsCategory.objects.filter(parent=None)

        s = GoodsCategorySerializer(instance=category,many=True)

        return Response(s.data)