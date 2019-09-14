



from rest_framework import serializers

from apps.goods.models import SPUSpecification




# 获取规格信息 序列化器
class SPUSpecificationSerializer(serializers.ModelSerializer):
    # 序列化spu名称
    spu = serializers.StringRelatedField(read_only=True)
    # 序列化spu_id
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'