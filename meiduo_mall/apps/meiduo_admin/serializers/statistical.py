from rest_framework import serializers

from apps.goods.models import GoodsVisitCount


class GoodsVisitCountSerialzer(serializers.ModelSerializer):

    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ['count','category']


