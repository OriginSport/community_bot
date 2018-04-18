#coding='utf-8'

import json

from django.db import models
from django.core import serializers
from django.utils import datetime_safe


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True)
    update_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return '<{0.__class__.__name__}> id={0.id}'.format(self)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)

    def get_json(self, clean=True):
        serials = serializers.serialize("json", [self])
        struct = json.loads(serials)
        data = struct[0]['fields']
        if 'pk' in struct[0]:
            data['id'] = struct[0]['pk']
        if clean:
            data.pop('create_time')
            data.pop('update_time')
            data.pop('is_active')
        return data

    def save(self, *args, **kwargs):
        self.update_time = datetime_safe.datetime.now()
        super(BaseModel, self).save(*args, **kwargs)


class AssistList(BaseModel):
    parent_id = models.IntegerField(unique=True, primary_key=True)
    order_id_list = models.TextField()

    class Meta:
        abstract = True

    @classmethod
    def get_list(cls, parent_id):
        try:
            current_list = cls.objects.get(pk=parent_id)
            if not current_list.order_id_list or current_list.order_id_list == '':
                return []
            order_id_list = current_list.order_id_list.strip(',').split(',')
            return order_id_list
        except:
            return []

    @classmethod
    def insert(cls, parent_id, new_id, pre_id=None):
        current_list = None
        try:
            current_list = cls.objects.get(pk=parent_id)
        except:
            pass
        if not current_list:
            o = cls(parent_id=parent_id, order_id_list=','.join([str(new_id)]))
            o.save()
            return [new_id]
        order_id_list = current_list.order_id_list.split(',')
        order_id_list = [str(x) for x in order_id_list]
        insert_index = 0
        if pre_id:
            insert_index = order_id_list.index(str(pre_id)) + 1
        order_id_list.insert(insert_index, str(new_id))
        current_list.order_id_list = ','.join(order_id_list)
        current_list.save()
        return order_id_list

    @classmethod
    def delete(cls, parent_id, id):
        current_list = cls.objects.get(pk=parent_id)
        order_id_list = current_list.order_id_list.split(',')
        order_id_list.remove(str(id))
        current_list.order_id_list = ','.join(order_id_list)
        current_list.save()
        return order_id_list

    @classmethod
    def update(cls, parent_id, target_id, index):
        current_list = cls.objects.get(pk=parent_id)
        order_id_list = current_list.order_id_list.split(',')
        order_id_list.remove(str(target_id))
        order_id_list.insert(index, str(target_id))
        current_list.order_id_list = ','.join(order_id_list)
        current_list.save()
        return order_id_list
