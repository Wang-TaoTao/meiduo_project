

# 生成详情页静态文件
import os

from django.conf import settings
from django.shortcuts import render
from django.template import loader
from requests import request

from apps.contents.utils import get_categories
from apps.goods.models import SKU
from apps.goods.utils import get_breadcrumb
from celery_tasks.main import app
from meiduo_mall.settings.dev import logger

@app.task
def generate_static_sku_detail_html(sku_id):

    # 获取当前sku信息
    try:
        sku = SKU.objects.get(id=sku_id)
    except Exception as e:
        logger.error(e)
        return render(request, '404.html')

    # 调用商品分类频道
    categories = get_categories()

    # 调用面包屑组件
    breadcrumb = get_breadcrumb(sku.category)

    # 构建当前商品的规格键
    sku_specs = sku.specs.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)
    # 获取当前商品的所有SKU
    skus = sku.spu.sku_set.all()
    # 构建不同规格参数（选项）的sku字典
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.specs.order_by('spec_id')
        # 用于形成规格参数-sku字典的键
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id
    # 获取当前商品的规格信息
    goods_specs = sku.spu.specs.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(goods_specs):
        return
    for index, spec in enumerate(goods_specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        spec_options = spec.options.all()
        for option in spec_options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.spec_options = spec_options

    # 渲染页面
    context = {
        'categories': categories,
        'breadcrumb': breadcrumb,
        'sku': sku,
        'specs': goods_specs,
    }


    # 获取详情页模板
    template = loader.get_template('detail.html')
    # 渲染成html_txt
    html_txt = template.render(context)
    # 将html_text写入指定路径
    # 设置路径
    file_path = os.path.join(settings.STATICFILES_DIRS[0],'detail/'+str(sku_id)+'.html')
    # 写入
    with open(file_path,'w') as file:
        file.write(html_txt)