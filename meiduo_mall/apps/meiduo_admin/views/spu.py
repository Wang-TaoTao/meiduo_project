from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SPU, Brand, GoodsCategory
from apps.meiduo_admin.serializers.spu import SPUSerializer, BrandsSerizliser, CategorysSerizliser
from apps.meiduo_admin.utils import CustomPageNumberPagination




# 新增SPU表数据---获取二三级分类信息
class ChanelCategory23View(ListAPIView):

    serializer_class = CategorysSerizliser

    # 根据传入pk不同 返回条件不同的查询集
    def get_queryset(self):

        # 接收pk
        pk = self.kwargs.get('pk')
        # 根据pk返回分类信息
        return GoodsCategory.objects.filter(parent_id=pk)




# 新增SKU表数据---获取一级分类信息
class ChannelCategorysView(ListAPIView):

    # 获取一级分类信息 parent_id为None表示一级分类
    queryset = GoodsCategory.objects.filter(parent_id=None)

    serializer_class = CategorysSerizliser





# 新增SKU表数据---获取品牌信息
class SPUBrandView(ListAPIView):

    queryset = Brand.objects.all()

    serializer_class = BrandsSerizliser



# 获取SPU数据
class SPUGoodsView(ModelViewSet):

    queryset = SPU.objects.all()

    serializer_class = SPUSerializer

    pagination_class = CustomPageNumberPagination

    # def get_queryset(self):
    #
    #     keyword = self.request.query_params.get('keyword')
    #
    #     if keyword:
    #
    #         return SPU.objects.filter(name__contains=keyword)
    #
    #     return SPU.objects.all()


