from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import Brand
from apps.meiduo_admin.serializers.brand import BrandSerializer
from apps.meiduo_admin.utils import CustomPageNumberPagination




# 获取品牌信息 增删改查功能
class BrandsView(ModelViewSet):

    queryset = Brand.objects.all()

    serializer_class = BrandSerializer

    pagination_class = CustomPageNumberPagination

    # 重写新增品牌信息方法
    def create(self, request, *args, **kwargs):


        from fdfs_client.client import Fdfs_client
        # 1 创建fdfs连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 2 获取图片资源
        data = request.FILES.get('logo')
        # 3 将图片上传至服务器
        result = client.upload_by_buffer(data.read())
        # 4 判断上传状态
        if result['Status'] != 'Upload successed.':
            return Response({'msg':'图片上传失败'})
        # 5 获取图片路径
        file_id = result['Remote file_id']
        # 6 将图片写入brand表中
        try:
            brands =Brand.objects.create(name=request.data.get('name'),
                                         logo = file_id,
                                         first_letter=request.data.get('first_letter'))
        except:
            return Response({'msg':"入库失败"})

        # 7 响应结果
        return Response({
            'id':brands.id,
            'name':request.data.get('name'),
            'logo':file_id,
            'first_letter':request.data.get('first_letter')
        },status=status.HTTP_201_CREATED)


    # 重写更新品牌信息方法
    def update(self, request, *args, **kwargs):


        from fdfs_client.client import Fdfs_client
        # 1 创建fdfs连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 2 获取图片资源
        data = request.FILES.get('logo')
        # 3 将图片上传至服务器
        result = client.upload_by_buffer(data.read())
        # 4 判断上传状态
        if result['Status'] != 'Upload successed.':
            return Response({'msg':'图片更新失败'})
        # 5 获取图片路径
        file_id = result['Remote file_id']
        # 6 更新品牌表
        # 6.1 获取前端传过来的要修改的id--pk
        pk = self.kwargs['pk']
        # 6.2 根据pk获取品牌表中要修改的对象
        brand = Brand.objects.get(id=pk)
        # 6.3 根据获取的对象更新信息
        brand.name = request.data.get('name')
        brand.logo = file_id
        brand.first_letter = request.data.get('first_letter')
        brand.save()

        # 7 响应结果
        return Response({
            'id':brand.id,
            'name':request.data.get('name'),
            'logo':file_id,
            'first_letter':request.data.get('first_letter')
        },status=status.HTTP_204_NO_CONTENT)
