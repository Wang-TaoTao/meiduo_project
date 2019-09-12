from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.order import OrderSeriazlier
from apps.meiduo_admin.utils import CustomPageNumberPagination
from apps.orders.models import OrderInfo






# 获取订单信息
class OrdersView(ModelViewSet):

    queryset = OrderInfo.objects.all()

    serializer_class = OrderSeriazlier

    pagination_class = CustomPageNumberPagination



    # 自己定义一个方法 修改订单状态
    @action(methods=['put'],detail=True)
    def status(self, request, pk):

        # 根据pk修改订单状态
        try:
            order = OrderInfo.objects.filter(order_id=pk).update(status=request.data.get('status'))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 返回结果
        return Response({
            'order_id':pk,
            'status':request.data.get('status')
        })