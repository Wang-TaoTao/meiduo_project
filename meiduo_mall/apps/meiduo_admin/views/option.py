from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SpecificationOption, SPU
from apps.meiduo_admin.serializers.option import OptionSerialzier
from apps.meiduo_admin.serializers.spu import SPUSerializer

from apps.meiduo_admin.utils import CustomPageNumberPagination

# 新增规格选项数据 ---获取SPU表名
class SPUOptionSimpleView(ListAPIView):

    queryset = SPU.objects.all()

    serializer_class = SPUSerializer



# 获取规格选项表信息
class OptionsView(ModelViewSet):

    queryset = SpecificationOption.objects.all()

    serializer_class = OptionSerialzier

    pagination_class = CustomPageNumberPagination


