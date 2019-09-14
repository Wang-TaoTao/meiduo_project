


from rest_framework import serializers
from apps.goods.models import SpecificationOption


# 获取规格选项表信息 序列化器
class OptionSerialzier(serializers.ModelSerializer):

    # 将规格名称外键序列化
    spec = serializers.StringRelatedField(read_only=True)
    # 将规格选项id序列化
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'