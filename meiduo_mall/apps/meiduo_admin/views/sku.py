from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKU, GoodsCategory, SPU, SPUSpecification
from apps.meiduo_admin.serializers.sku import SKUSerializer, SKUCategorieSerializer, SPUSimpleSerializer, \
    SPUSpecSerialzier

from apps.meiduo_admin.utils import CustomPageNumberPagination



# 新增SKU数据---根据SPU信息获取SPU规格信息
class SPUSpecView(ListAPIView):


    serializer_class = SPUSpecSerialzier

    # 根据前端传入参数不同 获取不同的查询集 也就是不同的规格
    def get_queryset(self):

        pk = self.kwargs.get('pk')

        return SPUSpecification.objects.filter(spu_id=pk)




# 新增SKU数据----获取SPU信息
class SPUSimpleView(ListAPIView):



    queryset = SPU.objects.all()

    serializer_class = SPUSimpleSerializer



# 新增SKU数据----获取三级分类信息
class SKUCategoriesView(ListAPIView):

    # 第一种 subs为None的是三级分类
    # queryset = GoodsCategory.objects.filter(subs=None)
    # 第二种 parent_id > 37的也是三级分类
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)

    serializer_class = SKUCategorieSerializer




#  获取 保存 更新 SKU数据功能
class SKUModelViewSet(ModelViewSet):

    # queryset = SKU.objects.all()
    # 设置序列化器对象
    serializer_class = SKUSerializer
    # 设置分页
    pagination_class = CustomPageNumberPagination

    # 模糊搜索功能
    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')

        if keyword:
            return SKU.objects.filter(name__contains=keyword)

        return SKU.objects.all()








