
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SPUSpecification
from apps.meiduo_admin.serializers.spec import SPUSpecificationSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination




# 获取规格信息
class SpecsView(ModelViewSet):


    queryset = SPUSpecification.objects.all()

    serializer_class = SPUSpecificationSerializer

    pagination_class = CustomPageNumberPagination

