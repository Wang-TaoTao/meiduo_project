from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.image import ImageSeriazlier, SKUSeriazlier
from apps.meiduo_admin.utils import CustomPageNumberPagination
from fdfs_client.client import Fdfs_client

# 获取新增图片时候的 sku表id
class SKUView(APIView):

    def get(self,request):

        # 获取sku表信息
        data = SKU.objects.all()
        # 序列化
        s = SKUSeriazlier(instance=data,many=True)
        # 响应结果
        return Response(s.data)




# 获取所有商品图片信息 --新增图片和更新图片功能
class ImageView(ModelViewSet):

    queryset = SKUImage.objects.all()

    serializer_class = ImageSeriazlier

    pagination_class = CustomPageNumberPagination


    # 新增图片 重写create方法
    def create(self, request, *args, **kwargs):


        # 1.创建FDFS对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 2.获取图片资源
        data = request.FILES.get('image')
        # 3.上传至服务器
        result = client.upload_by_buffer(data.read())
        # 4.判断上传状态
        if result['Status'] != 'Upload successed.':
            return Response(status=status.HTTP_403_FORBIDDEN)
        # 5.获取file_id
        file_id = result.get('Remote file_id')
        # 6.保存数据（入库）
        sku_image = SKUImage.objects.create(
            sku_id = request.data.get('sku'),
            image = file_id
        )
        # 7.响应结果
        return Response({
            'id':sku_image.id,
            'sku':sku_image.sku.id,
            'image':sku_image.image.url
        },status=status.HTTP_201_CREATED)

    # 更新图片
    def update(self, request, *args, **kwargs):

        # 1.创建FDFS对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 2.获取图片资源
        data = request.FILES.get('image')
        # 3.上传至服务器
        result = client.upload_by_buffer(data.read())
        # 4.判断上传状态
        if result['Status'] != 'Upload successed.':
            return Response(status=status.HTTP_404_NOT_FOUND)
        # 5.如果上传成功则过去file_id
        fild_id = result['Remote file_id']
        # 6.更新图片
        # 6.1 获取图片id
        image_id = kwargs['pk']
        # 6.2 根据图片id获取图片对象
        image_object = SKUImage.objects.get(id=image_id)
        # 6.3 根据图片对象更新图片
        image_object.image = fild_id
        image_object.save()

        # 7.响应结果
        return Response({
            'id':image_object.id,
            'sku':request.data.get('sku'),
            'image':image_object.image.url,
        },status=status.HTTP_201_CREATED)

