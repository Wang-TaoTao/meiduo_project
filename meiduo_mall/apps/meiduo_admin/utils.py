from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def jwt_response_payload_handler(token,user=None,request=None):


    '''自定义jwt认证成功返回的数据'''

    return {
        'token':token,
        'id':user.id,
        'username':user.username,
    }




# 重写分页功能
class CustomPageNumberPagination(PageNumberPagination):

    # 设置每页条数
    page_size = 5
    # 设置前端请求（查询参数）的时候设置每页条数的关键字
    page_size_query_param = 'pagesize'
    # 设置每页最大能返回的条数
    max_page_size = 20

    # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),     # 用户总数量
            ('lists', data),                          # 数据
            ('page', self.page.number),               # 当前页码
            ('pages', self.page.paginator.num_pages), # 总页数
            ('pagesize', self.page_size)              # 当前页显示条数

        ]))