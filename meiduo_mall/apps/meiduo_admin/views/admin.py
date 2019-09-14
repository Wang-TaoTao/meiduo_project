from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.admin import AdminSerializer, AdminSimpleSerialzier
from apps.meiduo_admin.utils import CustomPageNumberPagination
from apps.users.models import User


# 新增管理员用户 ----获取用户组信息
class AdminSimpleAPIView(APIView):

    def get(self,request):

        quseryset = Group.objects.all()

        s = AdminSimpleSerialzier(quseryset,many=True)

        return Response(s.data)


# 获取管理员用户 ----增删改查功能
class AdminView(ModelViewSet):

    queryset = User.objects.filter(is_staff=True)

    serializer_class = AdminSerializer

    pagination_class = CustomPageNumberPagination



