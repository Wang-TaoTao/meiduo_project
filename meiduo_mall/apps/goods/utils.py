# goods 封装



# 封装列表页的面包屑导航数据
def get_breadcrumb(cat3):


    # 三级分类获取二级分类
    cat2 = cat3.parent

    # 二级分类获取一级分类
    cat1 = cat2.parent

    # 拼接数据
    breadcrumb = {
        'cat1': {
            'url': cat1.goodschannel_set.all()[0].url,
            'name': cat1.name,
        },
        'cat2': cat2,
        'cat3': cat3,
    }
    return breadcrumb