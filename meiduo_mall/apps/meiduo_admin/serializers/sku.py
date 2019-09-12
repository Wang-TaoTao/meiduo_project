from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from apps.goods.models import SKU, GoodsCategory, SPU, SPUSpecification, SpecificationOption, SKUSpecification





# 新增SKU数据 ----根据SPU规格信息获取里面的规格选项 序列化器
class SPUOptineSerializer(serializers.ModelSerializer):


    class Meta:

        model = SpecificationOption
        fields = ['id','value']



# 新增SKU数据 ----根据SPU信息获取SPU规格信息 序列化器
class SPUSpecSerialzier(serializers.ModelSerializer):

    # 可加可不加这两句，就是最好把外键一起都序列化
    spu_id = serializers.IntegerField()
    spu = serializers.StringRelatedField(read_only=True)

    # 使用隐藏字段进行序列化 来 调出规格选项表中的规格选项信息
    options = SPUOptineSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'




# 新增SKU数据 ---获取SPU信息 序列化器
class SPUSimpleSerializer(serializers.ModelSerializer):


    class Meta:
        model = SPU
        fields = ['id','name']


# 新增SKU数据 ---获取三级分类信息 序列化器
class SKUCategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'




# 保存SKU数据  ---SKU规格 序列化器
class SKUSpecificationSerialzier(serializers.ModelSerializer):

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


# 获取SKU数据 ---保存、更新SKU数据功能  序列化器
class SKUSerializer(serializers.ModelSerializer):

    category_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)

    spu_id = serializers.IntegerField()
    spu = serializers.StringRelatedField(read_only=True)

    # 使用隐藏字段序列化 sku规格表
    specs = SKUSpecificationSerialzier(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    # 重写保存SKU数据
    def create(self, validated_data):

        # 1.接收参数
        specs = validated_data.get('specs')

        # 2.判断 如果有 就删除
        if specs:
            del validated_data['specs']


        # 设置事务开启
        with transaction.atomic():

            # 设置事务保存点
            sava_id = transaction.savepoint()

            try:

                # 3.保存SKU数据
                try:
                    sku = SKU.objects.create(**validated_data)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                # 4.再保存SKU的规格信息

                try:

                    for spec in specs:
                        SKUSpecification.objects.create(
                            sku_id=sku.id,
                            spec_id = spec.get('spec_id'),
                            option_id = spec.get('option_id')
                            )
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                # 由于没有default_image 会报错 所以设置指定一个图片
                sku.default_image = 'group1/M00/00/02/CtM3BVrPB4GAWkTlAAGuN6wB9fU4220429'
                sku.save()
            except:
                # 设置事务回滚点
                transaction.savepoint_rollback(sava_id)
            else:

                # 提交事务
                transaction.savepoint_commit(sava_id)
                # 5.异步任务生成静态文件
                from celery_tasks.html.tasks import generate_static_sku_detail_html
                generate_static_sku_detail_html(sku.id)


                # 6.返回结果
                return sku


    # 重写更新SKU数据
    def update(self, instance, validated_data):

        # 1 接收参数
        specs = validated_data.get('specs')

        # 2 判断 如果有 就删除
        if specs:
            del validated_data['specs']

        # 设置事务开启
        with transaction.atomic():

            # 设置事务保存点
            save_id = transaction.savepoint()

            try:

                # 3 先更新SKU数据
                try:
                    sku = SKU.objects.filter(id=instance.id).update(**validated_data)
                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                # 4 再更新SKU规格表数据
                try:
                    for spec in specs:
                        SKUSpecification.objects.filter(sku_id=instance.id,spec_id=spec.get('spec_id')).update(option_id=spec.get('option_id'))

                except:
                    return Response(status=status.HTTP_400_BAD_REQUEST)


                # 由于没有default_image 会报错 所以设置指定一个图片
                sku.default_image = 'group1/M00/00/02/CtM3BVrPB4GAWkTlAAGuN6wB9fU4220429'
                sku.save()

            except:

                # 设置事务回滚
                transaction.savepoint_rollback(save_id)
            else:
                # 提交事务
                transaction.savepoint_commit(save_id)

                # 异步任务生成静态文件
                from celery_tasks.html.tasks import generate_static_sku_detail_html
                generate_static_sku_detail_html(instance.id)

                # 5 返回结果
                return instance