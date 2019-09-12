




from collections import OrderedDict

from apps.goods.models import GoodsChannel



# 封装首页商品频道的分类---三级联动--左边
def get_categories():


    categories = OrderedDict()

    # 1首先获取37个频道
    channels = GoodsChannel.objects.order_by('group_id','sequence')

    # 2遍历37个频道
    for channel in channels:

        # 2.1根据频道取频道组id
        group_id = channel.group_id

        # 2.2分组判断11组
        if group_id not in categories:
            categories[group_id]={'channels': [], 'sub_cats': []}


        # 获取当前频道的类别
        cat1 = channel.category


        # 3从频道表根据当前的category_id外键属性获取一级分类
        categories[group_id]['channels'].append({
                'id':cat1.id,
                'name':cat1.name,
                'url':channel.url,

        })
        # 4二级分类 一级.subs.all()
        for cat2 in cat1.subs.all():
            cat2.sub_cats=[]

            # 5三级分类 二级.subs.all()
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)

            categories[group_id]['sub_cats'].append(cat2)


    return categories
