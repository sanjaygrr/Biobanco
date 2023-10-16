# admin.py en tu aplicación

from django.contrib import admin
from .models import StorageType


@admin.register(StorageType)
class StorageTypeAdmin(admin.ModelAdmin):
    list_display = ['name_storagetype']
