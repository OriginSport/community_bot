from django.contrib import admin
from .models import Reply

@admin.register(Reply)
class Reply(admin.ModelAdmin):
    list_display = ('keyword', 'en_us', 'zh_cn')

