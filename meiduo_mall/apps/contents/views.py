# contents 视图


from django.shortcuts import render
from django.views import View
from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories




# 渲染首页
class IndexView(View):
    '''首页'''


    def get(self,request):

        # 1.调用封装的商品频道三级分类函数
        categories = get_categories()

        # 2 获取首页广告数据
        contents = {}
        # 2.2 获取所有广告分类
        ad_categories = ContentCategory.objects.all()
        # 2.3 遍历分类 ,取出每个分类的广告内容
        for category in ad_categories:
            contents[category.key] = category.content_set.filter(status=True).order_by('sequence')


        # 构造返回给前端的数据
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request,'index.html',context)
