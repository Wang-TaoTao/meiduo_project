import json

from django_redis import get_redis_connection

from utils.cookiesecret import CookieSecret

# 封装合并购物车 redis_dict.update(cookie_dict)
def merge_cart_cookie_to_redis(request,response,user):

    # 获取cookie_str
    cookie_str = request.COOKIES.get('carts')
    # 判断cookie_str是否有值
    if cookie_str:
        # 解密
        cookie_dict = CookieSecret.loads(cookie_str)
    else:
        cookie_dict = {}
        return response

    # 获取redis
    client_conn = get_redis_connection('carts')
    client_data_dict = client_conn.hgetall(user.id)

    redis_dict = {}
    # 将取出的redis 二进制转换为普通字典
    for key,value in client_data_dict.items():
        sku_id = int(key.decode())
        sku_dict = json.loads(value.decode())
        redis_dict[sku_id] = sku_dict

    # 合并redis和cookie
    redis_dict.update(cookie_dict)

    # 重新插入数据到redis
    for sku_id in redis_dict:
        client_conn.hset(user.id,sku_id,json.dumps(redis_dict[sku_id]))

    # 删除cookie
    response.delete_cookie('carts')

    # 响应结果
    return response
