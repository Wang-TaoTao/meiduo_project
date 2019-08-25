# areas 视图

import json
import re


from django import http
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View


from apps.areas.models import Area, Address
from apps.verifications import constants
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE





# 修改密码
class ChangePasswordView(LoginRequiredMixin,View):

    # 展示修改密码界面
    def get(self,request):

        return render(request,'user_center_pass.html')

    # 实现修改密码逻辑
    def post(self,request):

        # 接收参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 校验密码是否正确
        result = request.user.check_password(old_password)
        # 如果result为假则不正确，如果为真则正确
        if not result:

            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        # 校验新密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        # 校验输入的两次新密码是否相等
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')


        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        # 响应密码修改结果 ：并且重定向到登录界面
        return response




# 修改地址标题
class UpdateTitleAddressView(LoginRequiredMixin,View):

    # 设置地址标题
    def put(self,request,address_id):

        # 接收参数:地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        # 返回响应地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})




# 设置默认收货地址
class DefaultAddressView(LoginRequiredMixin,View):
    # 设置默认收货地址
    def put(self,request,address_id):

        try:
            # 接收参数
            address = Address.objects.get(id=address_id)

            # 设置地址为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})


        # 响应设置默认地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})




# 修改和删除收货地址
class UpdateDestroyAddressView(LoginRequiredMixin,View):
    # 修改收货地址
    def put(self,request,address_id):

        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2.校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')


        # 3.判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(

                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})


        # 4.构造响应数据  dict
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 5.响应更新地址结果给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    # 删除收货地址
    def delete(self,request,address_id):

        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})


        # 响应删除地址的结果给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})




# 新增收货地址
class CreateAddressView(LoginRequiredMixin,View):

    def post(self,request):

        '''实现新增地址逻辑'''

        # 判断用户的地址是否大于20个
        count = Address.objects.filter(user=request.user).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 1.接受参数

        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')


        # 2.校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')


        # 3.保存地址信息
        try:
            address = Address.objects.create(
                user = request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email,
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address= address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})


        # 新增地址成功,将新增的地址相应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 返回响应结果给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})




# 省市区数据---三级联动
class AreasView(View):

    def get(self,request):
        '''提供省市区数据'''

        area_id = request.GET.get('area_id')

        if not area_id:
            # 说明用户没有省份数据,所以我们要提供省份数据
            # 读取省份缓存数据
            province_list = cache.get('province_list')

            # 判断是否有缓存数据
            if not province_list:

                try:
                    # 查询省份数据
                    province_model_list = Area.objects.filter(parent__isnull=True)

                    # 序列化省级数据
                    province_list = []
                    for province_model in province_model_list:
                        province_list.append(
                            {
                                'id':province_model.id,
                                'name':province_model.name
                            }
                        )
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})

                # 存数省份的缓存数据
                cache.set('province_list',province_list,3600)

            # 响应省份数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        else:
            # 说明用户有省份数据,所以我们需要提供市区数据
            # 读取市或区的缓存数据
            sub_data = cache.get('sbs_adea_' + area_id)

            # 判断是否有市或区的缓存数据
            if not sub_data:


                try:
                    # 查询市或区的父级
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()

                    # 序列化市或区的数据
                    sub_list = []
                    for sub_model in sub_model_list:

                        sub_list.append(
                            {
                                'id':sub_model.id,
                                'name':sub_model.name,
                            }
                        )

                        sub_data = {
                            'id':parent_model.id,     # 父级id
                            'name':parent_model.name, # 父级name
                            'subs':sub_list,          # 父级的子集
                        }
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})

                # 存储市或区的缓存数据
                cache.set('sub_area_' + area_id, sub_data,3600)

            # 响应市或区的数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
