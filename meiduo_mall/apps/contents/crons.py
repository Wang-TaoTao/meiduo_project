



import os
import time

from django.conf import settings
from django.template import loader

from apps.contents.models import ContentCategory
from apps.contents.utils import get_categories


# 实现首页静态化 定时器
def generate_static_index_html():

    # 测试
    print("%s:generate_static_index_html" % time.ctime())

    # 获取首页数据
    # 调用商品频道分类
    categories = get_categories()
    # 根据商品内容表获取首页商品
    try:
        content_category = ContentCategory.objects.all()
    except:
        return
    content = {}
    # 遍历商品分类取内容
    for category in content_category:
        content[category.key] = category.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories':categories,
        'contents':content,
    }

    # 获取首页模板文件
    template = loader.get_template('index.html')
    # 渲染成html_text
    html_text = template.render(context)
    # 将html_text写入指定目录
    file_path = os.path.join(settings.STATICFILES_DIRS[0],'index.html')
    with open(file_path,'w',encoding='utf-8') as file:
        file.write(html_text)


