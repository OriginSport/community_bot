import logging

from django.conf import settings
from django.db import models
from utils.basemodel.base import BaseModel

class Reply(models.Model):
    keyword = models.CharField(max_length=32, db_index=True, unique=True)
    en_us = models.TextField('English')
    zh_cn = models.TextField('简体中文')

    def __str__(self):
        return 'Reply:%s' % self.keyword

    @classmethod
    def get_content(cls, keyword, lang):
        key = cls.objects.filter(keyword=keyword).first()
        if not key:
            return None
        return getattr(key, lang, None)
        
